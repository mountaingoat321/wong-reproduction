module CoastalPaths
using ..Reproduction
using ..RecoveredModels: adaptation_menu
const R=Reproduction

"""Piecewise-linear cumulative area, in km2, below elevation z in m."""
function area_below(z,edges,areas)
    sum(areas[j]*clamp((z-edges[j])/(edges[j+1]-edges[j]),0.,1.) for j in eachindex(areas))
end

"""Annual segment cash-flow experiment, not an exact W25/CIAM reproduction.
Documented: ten candidate strategies, first-period selection, retained strategy,
stationary surge, quadratic protection, flood/retreat/wetland cost mechanisms.
Explicit timing alternative: annual cash flows, upgrades at 2010/2051/2101,
incremental construction paid at period start, maintenance paid annually.
land_rule=:literal uses the D16 Eq7 retreat expression with nonnegative area;
:physical instead charges each new physically inundated km2 exactly once.
No target segment exposure data or posterior is fabricated by this function.
"""
function candidate_path(years,sea,income,density,segment,candidate;
                        land_rule=:literal,maintenance_rule=:linear,panels=512)
    n=length(years)
    length(sea)==length(income)==length(density)==n || throw(DimensionMismatch())
    all(diff(years).==1) && years[1]==2010 || throw(ArgumentError("annual grid must start in 2010"))
    all(diff(sea).>=0) && sea[1]>=0 || throw(ArgumentError("experiment requires nondecreasing nonnegative SLR"))
    g=segment;strategy=candidate.strategy;rp=candidate.return_period
    surge=rp==0 ? 0.0 : rp==1 ? g.high_tide : R.gev_quantile(1-1/rp;g.gev...)
    maximum_surge=R.gev_quantile(1-1/10000;g.gev...)
    costs=zeros(n,6);height=zeros(n);retreat=zeros(n);migration=zeros(n)
    oldheight=0.0;oldretreat=0.0;oldsea=0.0
    for i in 1:n
        y=years[i];land=g.land_value*(income[i]/income[1])^.5*(density[i]/density[1])^.03
        capital=3income[i]*density[i]
        value_life=g.vslmult*g.us_income_2010*(income[i]/g.us_income_2010)^g.vslel
        wetland_value=g.wetland_value*(income[i]/income[1])^g.wvel*(density[i]/density[1])^g.wvpdl
        h=oldheight;r=oldretreat
        if y in (2010,2051,2101)
            stop=y==2010 ? 2050 : y==2051 ? 2100 : 2150
            j=findlast(t->t<=stop,years)
            if strategy==:protect
                h=max(h,sea[j]+surge)
                costs[i,1]=g.length*g.protection_coefficient*(h^2-oldheight^2)+
                    g.length*land*1.7*(h-oldheight)/1000 # m width -> km
            elseif strategy==:retreat
                r=max(r,sea[j]+surge)
            end
        end
        strategy==:none && (r=sea[i])
        new_area=max(0.,area_below(r,g.edges,g.areas)-area_below(oldretreat,g.edges,g.areas))
        if strategy!=:protect
            costs[i,3]=R.relocation_cost(new_area,income[i],density[i],capital;
                income_years=g.movefactor,reactive=strategy==:none)
            migration[i]=new_area*density[i]
            previous=land_rule==:physical ? oldsea : land_rule==:literal ? oldretreat :
                throw(ArgumentError("unknown land accounting"))
            lost=max(0.,area_below(sea[i],g.edges,g.areas)-area_below(previous,g.edges,g.areas))
            costs[i,4]=R.inundation_cost(lost,land,capital;depreciation=strategy==:retreat ? 1.0 : 0.0)
        else
            # D16 Eq3 has maintenance proportional to H; quadratic variant
            # tests interpreting 2% as a fraction of actual constructed cost.
            base=maintenance_rule==:linear ? h : maintenance_rule==:quadratic ? h^2 :
                throw(ArgumentError("unknown maintenance accounting"))
            costs[i,2]=.02*g.length*g.protection_coefficient*base
        end
        rate=i==1 ? 0.0 : sea[i]-sea[i-1]
        costs[i,5]=R.wetland_loss(area_below(sea[i],g.edges,g.areas),g.wetland_area,
            wetland_value,rate;protected=strategy==:protect)
        lower=max(0.,(strategy==:protect ? h : r)-sea[i])
        min_elevation=strategy==:protect ? 0.0 : r
        damage=s->R.flood_damage(s+sea[i],g.edges,g.areas;min_elevation=min_elevation,
            capital_density=capital,population_density=density[i],mortality=.01,
            value_of_life=value_life,resilience=income[i]/(g.us_income_2010+income[i]))
        costs[i,6]=lower>=maximum_surge ? 0.0 :
            R.expected_flood_loss(damage,g.gev;lower=lower,upper=maximum_surge,panels=panels)
        height[i]=h;retreat[i]=r;oldheight=h;oldretreat=r;oldsea=sea[i]
    end
    (costs=costs,total=vec(sum(costs,dims=2)),height=height,retreat=retreat,migration=migration)
end

function choose_path(years,sea,income,density,segment;kwargs...)
    menu=adaptation_menu()
    paths=[candidate_path(years,sea,income,density,segment,c;kwargs...) for c in menu]
    first=findall(y->2010<=y<=2050,years)
    values=[R.present_value(p.total[first],years[first]) for p in paths]
    choice=argmin(values)
    (choice=choice,candidate=menu[choice],path=paths[choice],paths=paths,first_period_pv=values)
end
end
