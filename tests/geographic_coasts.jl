using Test,TOML
include("../src/Reproduction.jl")
include("../src/RecoveredModels.jl")
include("../src/CoastalPaths.jl")
include("../src/GeographicCoasts.jl")
const G=GeographicCoasts;const C=CoastalPaths;const R=Reproduction
raw=TOML.parsefile("config/coastal_experiment.toml")
raw["gev"]=(;[Symbol(k)=>v for (k,v) in raw["gev"]]...)
old=(;[Symbol(k)=>v for (k,v) in raw]...)
years=collect(2010:2150);n=length(years);income=10000.;density=100.
g=(edges=old.edges,areas=old.areas,population=density.*old.areas,
   capital=3income*density.*old.areas,wetland=old.areas.*old.wetland_area/sum(old.areas),
   length=old.length,pc=old.protection_coefficient,mobile=.25,gev=old.gev)
eco=(income=fill(income,n),land=fill(old.land_value,n),wetland=fill(old.wetland_value,n),
     popscale=ones(n),capscale=ones(n),us_income_2010=old.us_income_2010)
suite=@testset "Geographic exposure and independent quadrature" begin
    q=G.quadrature(12)
    @test sum(q.weights)≈2. atol=1e-14
    @test sum(q.weights.*q.nodes.^22)≈2/23 atol=1e-14
    narrow=merge(g,(gev=(location=2.5,scale=.001,shape=0.0),))
    moments=G.flood_moments(0.,0.,0.,narrow,q)
    upper=-log(-log(.9999))
    for field in (:capital,:population)
        reference=R.simpson(z->getproperty(G.damage_moments(2.5+.001*z,0.,g.edges,g.capital,g.population),field)*exp(-z-exp(-z)),-8.,upper,32768)
        @test getproperty(moments,field)≈reference rtol=1e-9
    end
    for water in (0.,.2,1.5,4.,20.),retreat in (0.,.5,3.)
        d=G.damage_moments(water,retreat,g.edges,g.capital,g.population)
        expected=R.flood_damage(water,g.edges,g.areas;min_elevation=retreat,
            capital_density=3income*density,population_density=density,mortality=.01,
            value_of_life=1e6,resilience=.5)
        @test .5*(d.capital+.01*1e6*d.population)≈expected atol=1e-6
    end
    sea=collect(range(0.,1.;length=n))
    for c in RecoveredModels.adaptation_menu()
        # The geographic alternative's minimum retreat is explicitly MSL.
        c.return_period==1 && continue
        a=C.candidate_path(years,sea,fill(income,n),fill(density,n),old,c;
            land_rule=:physical,panels=2048)
        b=G.candidate_path(years,sea,eco,g,c;quad=G.quadrature(24),
            wetland_rule=:paper,movefactor=old.movefactor,vslmult=old.vslmult,vslel=old.vslel)
        @test b.costs≈a.costs rtol=1e-7 atol=1e-3
        @test b.migrants≈a.migration rtol=1e-12 atol=1e-10
    end
    chosen=G.choose_path(years,sea,eco,g)
    @test chosen.choice==argmin(chosen.first_period_pv)
    @test all(chosen.path.costs.>=0)
    steady=G.candidate_path(years,zeros(n),eco,g,(strategy=:retreat,return_period=100))
    @test all(steady.migrants[2:end].==0)
    @test all(steady.costs[:,4:5].==0)
end
c=Test.get_test_counts(suite)
open("results/geographic_coasts_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>c[1]+c[5],"failed"=>c[2]+c[6],"errors"=>c[3]+c[7]))
end
