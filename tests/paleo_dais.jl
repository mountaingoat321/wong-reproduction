using Test,TOML
include("../src/PaleoDAIS.jl")
const D=PaleoDAIS
suite=@testset "Paleo DAIS inversion and switching dynamics" begin
    p=D.M.dais_parameters()
    for r in (1.1e6,1.8636e6,2.3e6),s in (-150.,0.,10.)
        v=D.M.dais_geometry(r,s,p).volume/1e15
        @test D.radius_from_volume(v,s,p)≈r atol=1e-6
    end
    @test D.ocean_temperature(-18.)≈.7236
    @test D.SLE_PER_VOLUME*24.78≈57.
    # Exact trajectories of the discontinuous flux, including finite hitting
    # time, sliding, ordinary mass loss below cutoff and departure upward.
    @test D.cutoff_step((t,v)->.2,0.,19.,4.,.5)≈18.
    @test D.cutoff_step((t,v)->.2,0.,17.,8.,.5)≈18.
    @test D.cutoff_step((t,v)->-.2,0.,19.,4.,.5)≈18. - .2*(4-1/.7) atol=1e-8
    @test D.cutoff_step((t,v)->.8,0.,18.,4.,.5)≈19.2
    @test D.cutoff_step((t,v)->.2+.1t,0.,18.,6.,.5)≈18.45 atol=1e-8
    @test D.cutoff_step((t,v)->.2-.1t,0.,18.,6.,.5)≈17.2 atol=1e-8
    req=D.M.bisect(r->D.M.dais_radius_rhs(r,-18.,0.,0.,.72,p),1.5e6,2.1e6)
    constant=[0. -18. 0.;200. -18. 0.]
    z=D.run(constant,[0.,200.];initial_radius=req,ocean_rule=:fixed,dt=2.)
    @test z.radius[2]≈req atol=1e-6
    # Independent radius-coordinate RK4 includes the geometric sea derivative.
    forcing=[0. -18. 0.;200. -14. 3.]
    vv=D.run(forcing,0.:1.:200.;dt=.5,ocean_rule=:fixed)
    r=1.8636e6;gate=(-p.h0/p.c+18)/.02
    breaks=sort(unique(vcat(collect(0.:.5:200.),[gate])))
    for j in 1:length(breaks)-1
        t=breaks[j];h=breaks[j+1]-t;active=p.h0+p.c*(-18+.02*(t+h/2))>0
        f=(tt,x)->D.M.dais_radius_rhs(x,-18+.02tt,.015tt,.015,.72,p;runoff_active=active)
        r=D.rk4(f,t,r,h)
    end
    @test vv.radius[end]≈r atol=1e-5
end
counts=Test.get_test_counts(suite)
open("results/paleo_dais_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>counts[1]+counts[5],"failed"=>counts[2]+counts[6],"errors"=>counts[3]+counts[7]))
end
