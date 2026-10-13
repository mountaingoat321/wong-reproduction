using Test, LinearAlgebra, Random, TOML
include(joinpath(@__DIR__,"..","src","RecoveredModels.jl"))
const M=RecoveredModels
include(joinpath(@__DIR__,"..","src","Reproduction.jl"))
const R=Reproduction

suite=@testset "Recovered coupled mechanisms" begin
    @testset "DOECLIM steady state and heat accounting" begin
        for ecs in (1.5,3.0,4.5), diffusivity in (0.0,0.55,2.0)
            s=M.climate_system(ecs=ecs,diffusivity=diffusivity,cells=20)
            eq=vcat(s.equilibrium_land,fill(s.equilibrium_sea,21))
            @test maximum(abs.(s.A*eq+3.7s.forcing))<1e-12
            @test M.global_temperature(s,eq)≈ecs
            x=collect(range(0.0,2.0,length=22))
            net=2.0-s.land_fraction*s.lambda_land*x[1]-(1-s.land_fraction)*s.lambda_sea*x[2]
            @test dot(s.mass,s.A*x+2s.forcing)≈net atol=1e-12
        end
        s=M.climate_system(cells=20)
        uniform=ones(22)
        @test M.ocean_heat_to_depth(s,uniform,0.)==0
        @test M.ocean_heat_to_depth(s,uniform,700.) ≈
            3.62e14*M.SECONDS_PER_YEAR*s.cv*(57.5+s.ocean_fraction*(700-57.5))
        @test M.ocean_heat_to_depth(s,uniform,4057.5) ≈ M.ocean_heat(s,uniform;mixed_depth=57.5)
        @test M.ocean_heat_to_depth(s,uniform,30.) ≈ 3.62e14*M.SECONDS_PER_YEAR*s.cv*30
        @test all(iszero,M.climate_run(s,zeros(5)))
        q=fill(3.7,21)
        out=M.climate_run(s,q;substeps=8)
        @test all(out.>=0)
        @test all(diff([M.global_temperature(s,out[:,j]) for j in 1:21]).>0)
        @test all(diff([M.ocean_heat(s,out[:,j]) for j in 1:21]).>0)
        eq=-(s.A\(3.7s.forcing))
        exact=eq-exp(Matrix(s.A)*20)*eq
        errs=[maximum(abs.(M.climate_run(s,q;substeps=n)[:,end]-exact)) for n in (1,2,4)]
        @test all(3.8.<errs[1:2]./errs[2:3].<4.2)
    end
    @testset "DAIS dimensions, quadrature and differentiated geometry" begin
        p=M.dais_parameters()
        @test M.dais_discharge(1e6,0.0,0.72,p)==0
        @test M.dais_discharge(p.radius0,0.0,0.72,p)<0
        @test M.dais_discharge(p.radius0,0.0,1.72,p)<M.dais_discharge(p.radius0,0.0,0.72,p)
        for radius in (1e6,1.864e6), sea in (-100.0,0.0,100.0)
            g=M.dais_geometry(radius,sea,p)
            dr=(M.dais_geometry(radius+1.0,sea,p).volume-M.dais_geometry(radius-1.0,sea,p).volume)/2
            # BigFloat prevents cancellation of ~1e16 m³ when the derivative is zero.
            step=big"0.000001"
            ds=(M.dais_geometry(BigFloat(radius),BigFloat(sea)+step,p).volume-
                M.dais_geometry(BigFloat(radius),BigFloat(sea)-step,p).volume)/(2step)
            @test dr≈g.dr rtol=2e-9
            @test ds≈g.ds rtol=2e-7 atol=10.0
        end
        for air in (-18.0,-12.0,-5.0)
            # Numerical area integral of S14 Eq.4, with its stated runoff gate.
            radius=p.radius0; precip=p.precip0*exp(p.kappa*air); line=p.h0+p.c*air
            # u=sqrt(R-r) removes the square-root endpoint singularity.
            edge=p.bed-p.slope*radius
            f=u->4pi*u*(radius-u^2)*(precip-(line>0 ? p.nu*sqrt(precip)*max(0,line-edge-sqrt(p.mu)*u) : 0))
            split=clamp((line-edge)/sqrt(p.mu),0.0,sqrt(radius))
            numerical=R.simpson(f,0.0,split,2048)+R.simpson(f,split,sqrt(radius),2048)
            @test numerical≈M.dais_accumulation(radius,air,p) rtol=1e-7
        end
        eq=M.bisect(r->M.dais_radius_rhs(r,-18.0,0.0,0.0,0.72,p),1.5e6,2.1e6)
        # Published S14 steady-state benchmark (not a Wong2025 reproduction).
        @test M.dais_geometry(eq,0.0,p).volume/1e15≈24.78 rtol=0.002
        @test abs(M.dais_radius_rhs(eq,-18.0,0.0,0.0,0.72,p))<1e-8
        @test M.dais_radius_rhs(eq,-18.0,0.0,0.0,0.72,p;fast_loss_m_per_year=.01)<0
    end
    @testset "Recovered socioeconomic specifications" begin
        menu=M.adaptation_menu()
        @test length(menu)==10
        @test count(x->x.strategy==:protect,menu)==4
        @test count(x->x.strategy==:retreat,menu)==5
        @test !any(x->x.strategy==:protect && x.return_period==1,menu)
        @test M.annual_high_tide(0.8,2.0,3.0)≈1.2
        @test_throws DomainError M.annual_high_tide(0.8,0.0,3.0)
        rng=MersenneTwister(20251035)
        for p in M.SOCIO_PRIORS
            xs=[M.truncated_normal(rng,p.mean,p.sd,p.lo,p.hi) for i in 1:1000]
            @test all(p.lo.<=xs.<=p.hi)
        end
    end
end
counts=Test.get_test_counts(suite)
open(joinpath(@__DIR__,"..","results","recovered_test_summary.toml"),"w") do io
    TOML.print(io,Dict("passed"=>counts[1]+counts[5],"failed"=>counts[2]+counts[6],
        "errors"=>counts[3]+counts[7],"scope"=>"Recovered coupled mechanisms, not full target reproduction"))
end
