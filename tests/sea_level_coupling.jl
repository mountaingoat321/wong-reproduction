using Test,TOML
include("../src/PaleoDAIS.jl");include("../src/SeaLevelCoupling.jl")
const D=PaleoDAIS;const S=SeaLevelCoupling
suite=@testset "Antarctic feedback and component accounting" begin
    p=D.M.dais_parameters();r0=1.8636e6;years=collect(0.:1.:100.)
    air=-18 .+.04years;other=.01years;ocean=fill(.72,length(years))
    prescribed=D.run(hcat(years,air,other),years;dt=.25,initial_radius=r0,ocean_rule=:fixed)
    zero=S.antarctic_path(years,air,ocean,other;initial_radius=r0,initial_sea=0.,fingerprint=0.,dt=.25)
    @test zero.volume≈prescribed.volume atol=1e-9
    coupled=S.antarctic_path(years,air,ocean,other;initial_radius=r0,initial_sea=0.,dt=.25)
    @test coupled.shore≈other-coupled.antarctic
    @test coupled.antarctic≈(coupled.volume[1].-coupled.volume)*D.SLE_PER_VOLUME
    # Independent radius ODE includes dS/dt=dOther/dt+k*dV/dt at f_AIS=-1.
    v0=coupled.volume[1];r=r0
    breaks=sort(unique(vcat(collect(0.:.125:100.),[(-p.h0/p.c+18)/.04])))
    # Solve the implicit sea/volume geometry for prescribed radius by bisection.
    function sea_at(t,r)
        D.M.bisect(s->s-.01t-(D.M.dais_geometry(r,s,p).volume/1e15-v0)*D.SLE_PER_VOLUME,-10.,10.;xtol=1e-10)
    end
    for j in 1:length(breaks)-1
        t=breaks[j];h=breaks[j+1]-t;active=p.h0+p.c*(-18+.04*(t+h/2))>0
        function rhs(tt,rr)
            s=sea_at(tt,rr);g=D.M.dais_geometry(rr,s,p)
            vd=(D.M.dais_accumulation(rr,-18+.04tt,p;runoff_active=active)+D.M.dais_discharge(rr,s,.72,p))/1e15
            sd=.01+D.SLE_PER_VOLUME*vd
            (1e15vd-g.ds*sd)/g.dr
        end
        r=D.rk4(rhs,t,r,h)
    end
    @test D.radius_from_volume(coupled.volume[end],coupled.shore[end],p)≈r atol=1e-4
    fine=S.antarctic_path(years,air,ocean,other;initial_radius=r0,initial_sea=0.,dt=.125)
    @test maximum(abs.(fine.antarctic-coupled.antarctic))<1e-7
    req=D.M.bisect(r->D.M.dais_radius_rhs(r,-18.,0.,0.,.72,p),1.5e6,2.1e6)
    equilibrium=S.antarctic_path(years,fill(-18.,length(years)),ocean,zeros(length(years));initial_radius=req,initial_sea=0.)
    @test maximum(abs.(equilibrium.antarctic))<1e-9
    # Integrated covariance differs by N vs N^2; exact balanced variates test
    # rate bookkeeping without statistical-test randomness.
    @test S.landwater([1.,-1.,1.,-1.])[end]≈.0012
    @test S.landwater([1.,-1.,1.,-1.];mode=:common)[end]≈.00192
    @test S.landwater(zeros(100))[end]≈.03
    @test_throws ArgumentError S.landwater([0.];mode=:unknown)
end
counts=Test.get_test_counts(suite)
open("results/sea_level_coupling_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>counts[1]+counts[5],"failed"=>counts[2]+counts[6],"errors"=>counts[3]+counts[7]))
end
