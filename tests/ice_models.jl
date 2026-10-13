using Test,TOML
include("../src/Reproduction.jl")
include("../src/IceModels.jl")
const R=Reproduction;const I=IceModels
suite=@testset "Analytical ice trajectories and induced priors" begin
    for n in (.55,.75,1.)
        t=fill(1.,101);s=I.glaciers(t,.001,.4,n,0.)
        numerical=R.rk4((time,x)->R.glacier_rhs(x,1.;beta=.001,volume=.4,exponent=n),0.,0.,.25,400)
        @test s[end]≈numerical[end] atol=1e-12
        @test all(diff(s).>=0)
        @test I.glaciers(fill(-.15,10),.01,.4,n,.001)≈fill(.001,10) atol=1e-14
    end
    extinct=I.glaciers(vcat(fill(20.,100),fill(-1.,5)),.04,.3,.55,0.)
    @test all(extinct[end-5:end].==.3)
    @test all(extinct.<=.3)
    @test I.glaciers([10.,-10.],.4,.3,.5,0.)[end]==.3
    @test I.glaciers([-1.,2.],.001,.4,.75,.4)==[.4,.4]
    @test R.simpson(I.greenland_difference_prior,-1.672,1.672,16720)≈1 atol=1e-8
    @test I.greenland_difference_prior(-.5)≈I.greenland_difference_prior(.5)
    t=fill(1.,101);s=I.greenland(t,.2,2.,.3,.1)
    @test s[end]≈2.2*(1-exp(-.0004*100)) atol=1e-13
    @test_throws DomainError I.greenland([-1.,0.],.2,2.,1.,.1)
    t=collect(range(-.1,3.;length=141))
    @test I.greenland(t,.1,2.,.5,.2)≈I.greenland(t,.1,2.,.5,.2;substeps=8) atol=1e-11
    part=I.greenland(t[1:50],.1,2.,.5,.2)
    @test I.greenland(t[50:end],.1,2.,.5,.2;initial=part[end])[end]≈I.greenland(t,.1,2.,.5,.2)[end] atol=1e-13
    part=I.glaciers(t[1:50],.001,.4,.75,0.)
    @test I.glaciers(t[50:end],.001,.4,.75,part[end])[end]≈I.glaciers(t,.001,.4,.75,0.)[end] atol=1e-13
end
c=Test.get_test_counts(suite)
open("results/ice_models_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>c[1]+c[5],"failed"=>c[2]+c[6],"errors"=>c[3]+c[7]))
end
