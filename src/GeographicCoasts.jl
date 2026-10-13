module GeographicCoasts
using LinearAlgebra
using ..Reproduction
using ..RecoveredModels: adaptation_menu
using ..CoastalPaths: area_below
const R=Reproduction

"""Gauss--Legendre nodes/weights from the Legendre Jacobi matrix."""
function quadrature(n=12)
    n>=2 || throw(DomainError(n))
    e=eigen(SymTridiagonal(zeros(n),[i/sqrt(4i^2-1) for i in 1:n-1]))
    (nodes=e.values,weights=2 .* e.vectors[1,:].^2)
end

"""Event losses for elevation-binned capital and population stocks.
Capital integrates depth/(1m+depth); population integrates the flooded fraction.
Stocks need not have the same elevation profile as land area.
"""
function damage_moments(water,retreat,edges,capital,population)
    k=0.0;p=0.0
    @inbounds for j in eachindex(capital)
        edges[j]>=water && break
        a=max(edges[j],retreat);b=min(edges[j+1],water)
        b<=a && continue
        width=edges[j+1]-edges[j]
        cap=(b-a)-log1p((b-a)/(1+water-b))
        k+=capital[j]*cap/width;p+=population[j]*(b-a)/width
    end
    (capital=k,population=p)
end

"""Expected stock damage, integrating each smooth elevation interval separately.
The surge density is stationary; upper cutoff is the documented 10,000yr level.
No values are taken from a coastal model's simulated outputs.
"""
function flood_moments(sea,retreat,lower,g,quad)
    upper=R.gev_quantile(.9999;g.gev...)
    lower>=upper && return (capital=0.0,population=0.0)
    # Elevation cuts resolve damage-function changes; probability cuts also
    # resolve narrow hazard densities wholly contained within one land bin.
    hazard=[R.gev_quantile(p;g.gev...) for p in (1e-12,1e-8,1e-5,.001,.01,.1,.5,.9,.99,.999)]
    cuts=sort!(unique!(vcat(lower,[e-sea for e in g.edges if lower<e-sea<upper],
        [s for s in hazard if lower<s<upper],upper)))
    k=0.0;p=0.0
    for i in 2:length(cuts)
        midpoint=(cuts[i]+cuts[i-1])/2;half=(cuts[i]-cuts[i-1])/2
        for j in eachindex(quad.nodes)
            s=midpoint+half*quad.nodes[j]
            d=damage_moments(s+sea,retreat,g.edges,g.capital,g.population)
            w=half*quad.weights[j]*R.gev_pdf(s;g.gev...)
            k+=w*d.capital;p+=w*d.population
        end
    end
    (capital=k,population=p)
end

"""Annual geographic alternative using independent SLIIDERS stocks/economics.
2019 USD PPP; 2010 discount origin; first-period strategy retained.
Explicit alternatives: minimum retreat follows mean sea level (DP23), annual
upfront upgrades, actual elevation profiles, physical annual land loss,
and a paired no-SLR counterfactual. It is not the target W25 accounting.
"""
function candidate_path(years,sea,eco,g,candidate;quad=quadrature(),movefactor=1.0,
                        vslmult=200.0,vslel=.47,wetland_rule=:profile)
    n=length(years)
    years[1]==2010 && all(diff(years).==1) && length(sea)==n || throw(ArgumentError("annual 2010 start required"))
    all(diff(sea).>=0) && sea[1]>=0 || throw(DomainError(sea))
    all(g.areas.>=0) && all(g.population.>=0) && all(g.capital.>=0) || throw(DomainError(g))
    strategy=candidate.strategy;rp=candidate.return_period
    surge=rp<=1 ? 0.0 : R.gev_quantile(1-1/rp;g.gev...)
    costs=zeros(n,6);migrants=zeros(n);height=0.;retreat=0.;oldsea=0.
    for i in eachindex(years)
        oldheight=height;oldretreat=retreat
        if years[i] in (2010,2051,2101)
            stop=years[i]==2010 ? 2050 : years[i]==2051 ? 2100 : 2150
            j=findlast(y->y<=stop,years)
            if strategy==:protect
                height=max(height,sea[j]+surge)
                costs[i,1]=g.length*g.pc*(height^2-oldheight^2)+
                    g.length*eco.land[i]*1.7*(height-oldheight)/1000
            elseif strategy==:retreat
                retreat=max(retreat,sea[j]+surge)
            end
        end
        strategy==:none && (retreat=sea[i])
        if strategy!=:protect
            dp=(area_below(retreat,g.edges,g.population)-area_below(oldretreat,g.edges,g.population))*eco.popscale[i]
            dk=(area_below(retreat,g.edges,g.capital)-area_below(oldretreat,g.edges,g.capital))*eco.capscale[i]
            migrants[i]=dp
            costs[i,3]=(strategy==:none ? 5 : 1)*(movefactor*eco.income[i]*dp+(.1*g.mobile+.05*(1-g.mobile))*dk)
            da=area_below(sea[i],g.edges,g.areas)-area_below(oldsea,g.edges,g.areas)
            dksea=(area_below(sea[i],g.edges,g.capital)-area_below(oldsea,g.edges,g.capital))*eco.capscale[i]
            costs[i,4]=eco.land[i]*da+(strategy==:none ? (1-g.mobile)*dksea : 0.)
        else
            costs[i,2]=.02*g.length*g.pc*height
        end
        rate=sea[i]-oldsea
        wet=wetland_rule==:profile ? area_below(sea[i],g.edges,g.wetland) :
            wetland_rule==:paper ? min(area_below(sea[i],g.edges,g.areas),sum(g.wetland)) :
            throw(ArgumentError("unknown wetland rule"))
        fraction=strategy==:protect || rate>=.01 ? 1.0 : (rate/.01)^2
        costs[i,5]=eco.wetland[i]*wet*fraction
        lower=max(0.,(strategy==:protect ? height : retreat)-sea[i])
        d=flood_moments(sea[i],strategy==:protect ? 0. : retreat,lower,g,quad)
        vsl=vslmult*eco.us_income_2010*(eco.income[i]/eco.us_income_2010)^vslel
        resilience=eco.income[i]/(eco.us_income_2010+eco.income[i])
        costs[i,6]=(1-resilience)*(eco.capscale[i]*d.capital+.01*vsl*eco.popscale[i]*d.population)
        oldsea=sea[i]
    end
    (costs=costs,total=vec(sum(costs,dims=2)),migrants=migrants)
end

function choose_path(years,sea,eco,g;kwargs...)
    menu=adaptation_menu()
    paths=[candidate_path(years,sea,eco,g,c;kwargs...) for c in menu]
    first=findall(y->y<=2050,years)
    values=[R.present_value(p.total[first],years[first]) for p in paths]
    choice=argmin(values)
    (choice=choice,candidate=menu[choice],path=paths[choice],paths=paths,first_period_pv=values)
end
end
