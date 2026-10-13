using Test, LinearAlgebra, TOML
include("../src/RecoveredModels.jl")
include("../src/CarbonCycle.jl")
const M=RecoveredModels
const C=CarbonCycle
set=@testset "Recovered carbon mass balance and split integration" begin
    p=C.parameters(); x=C.initial_state()
    @test C.partition(0.0,p).co2 ≈ 280.0 atol=1e-8
    @test maximum(abs.(C.rhs(x,0.0,0.0,p)))<1e-8
    @test maximum(abs.(C.prescribed_run(zeros(5),zeros(5);p=p).-x))<1e-8
    for initial_co2 in (275.,295.)
        reference=C.parameters(c0=initial_co2)
        @test C.partition(0.,reference).co2≈initial_co2 atol=1e-8
        @test maximum(abs.(C.rhs(x,0.,0.,reference)))<1e-8
        @test maximum(abs.(C.prescribed_run(zeros(5),zeros(5);p=reference).-x))<1e-8
        driven=C.prescribed_run(fill(2.,5),zeros(5);p=reference)
        @test sum(driven[:,end])-sum(x)≈8. atol=1e-9
    end
    forced=C.prescribed_run(fill(2.,5),fill(.5,5);p=p)
    @test sum(forced[:,end])-sum(x)≈8.0 atol=1e-9
    for perturbation in (-50.0,1.0,100.0,1000.0,5000.0)
        a=C.partition(perturbation,p)
        @test a.atmosphere+a.mixed ≈ perturbation atol=1e-12
        dic=a.co2/p.solubility*(1+p.k1/a.hydrogen+p.k1*p.k2/a.hydrogen^2)
        @test p.conversion*(dic-p.dic0) ≈ a.mixed atol=1e-8
    end
    for e in (0.0,10.0), t in (0.0,4.0)
        xx=x+[500.,25.,100.,200.,20.,40.,10.,100.]
        @test sum(C.rhs(xx,e,t,p)) ≈ e atol=1e-12
    end
    sys=M.climate_system(cells=40)
    a=C.coupled_run(sys,fill(10.,41),zeros(41);substeps=4)
    @test vec(sum(a.carbon,dims=1)).-sum(x) ≈ collect(0.:10.:400.) atol=2e-9
    @test all(a.carbon[5:end,:].>0)
    @test C.partition(a.carbon[1,end],p).co2>280
    @test M.global_temperature(sys,a.climate[:,end])>0
    b=C.coupled_run(sys,fill(10.,41),zeros(41);substeps=8)
    c=C.coupled_run(sys,fill(10.,41),zeros(41);substeps=16)
    err1=abs(a.carbon[1,end]-b.carbon[1,end]);err2=abs(b.carbon[1,end]-c.carbon[1,end])
    @test 3.5<err1/err2<4.5
    restart=C.coupled_run(sys,fill(10.,21),zeros(21);substeps=8,
        carbon_initial=b.carbon[:,21],climate_initial=b.climate[:,21])
    @test restart.carbon[:,end]≈b.carbon[:,end] atol=1e-9
    @test restart.climate[:,end]≈b.climate[:,end] atol=1e-12
    cool=C.coupled_run(sys,fill(10.,41),zeros(41);substeps=8,carbon_temperature_offset=1.)
    @test C.partition(cool.carbon[1,end],p).co2<C.partition(b.carbon[1,end],p).co2
end
open("results/carbon_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>Test.get_test_counts(set)[1],"failed"=>0,"errors"=>0))
end
