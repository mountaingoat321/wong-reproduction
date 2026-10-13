using Test,TOML
include("../src/Reproduction.jl")
include("../src/RecoveredModels.jl")
include("../src/CoastalPaths.jl")
const C=CoastalPaths
const R=Reproduction
raw=TOML.parsefile("config/coastal_experiment.toml")
raw["gev"]=(;[Symbol(k)=>v for (k,v) in raw["gev"]]...)
segment=(;[Symbol(k)=>v for (k,v) in raw]...)
set=@testset "Annual coastal cash flows and policy persistence" begin
    years=collect(2010:2150);income=fill(10000.,141);density=fill(100.,141);sea=zeros(141)
    @test C.area_below(1.5,segment.edges,segment.areas)==15.0
    @test C.area_below(20.,segment.edges,segment.areas)==sum(segment.areas)
    chosen=C.choose_path(years,sea,income,density,segment;panels=128)
    @test chosen.choice==argmin(chosen.first_period_pv)
    @test length(chosen.paths)==10
    for (c,p) in zip(RecoveredModels.adaptation_menu(),chosen.paths)
        @test all(isfinite,p.total) && all(p.costs.>=0)
        @test p.total==vec(sum(p.costs,dims=2))
        @test all(p.migration[2:end].==0)
        @test all(p.costs[2:end,1].==0)
        @test all(p.retreat.==p.retreat[1]) && all(p.height.==p.height[1])
    end
    c=(strategy=:protect,return_period=100)
    p=C.candidate_path(years,collect(range(0.,1.;length=141)),income,density,segment,c;panels=128)
    @test count(>(0),p.costs[:,1])==3
    @test sum(p.migration)==0
    @test all(p.height.>=collect(range(0.,1.;length=141)))
    # With constant land value, incremental dike costs telescope to final cost.
    expected=segment.length*segment.protection_coefficient*p.height[end]^2+
        segment.length*segment.land_value*1.7*p.height[end]/1000
    @test sum(p.costs[:,1]) ≈ expected rtol=1e-12
    # New policy choices only inspect the first planning horizon.
    altered=copy(sea);altered[42:end].=range(.1,2.;length=100)
    second=C.choose_path(years,altered,income,density,segment;panels=128)
    @test second.first_period_pv==chosen.first_period_pv
    @test second.choice==chosen.choice
end
open("results/coastal_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>Test.get_test_counts(set)[1],"failed"=>0,"errors"=>0))
end
