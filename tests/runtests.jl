using Test, TOML, Random, Statistics, LinearAlgebra
include(joinpath(@__DIR__, "..", "src", "Reproduction.jl"))
const R = Reproduction
const ROOT = normpath(joinpath(@__DIR__,".."))
const cfg = TOML.parsefile(joinpath(ROOT,"config","validation.toml"))

suite = @testset "Independent scientific kernels" begin
    @testset "Emissions, carbon and forcing" begin
        years,q = R.emissions(2000,2004,10.0,0.1,2002,0.07)
        @test q[1:3] ≈ [10,10.1,10.1]
        @test all(diff(q[3:end]) .< 0)
        _,zeroq = R.emissions(2000,2010,0.0,0.0,2005,0.1)
        @test all(iszero,zeroq)
        @test_throws ArgumentError R.emissions(2000,2010,1.,.1,1999,.1)
        @test R.co2_forcing(560.,280.) ≈ 3.7
        @test R.co2_forcing(280.,280.) == 0
        @test R.co2_forcing(280.,560.) ≈ -3.7
        @test R.npp(280.,0.4) == 60
        @test R.npp(560.,0.4)/60 ≈ 1+0.4log(2)
        @test R.respiration(10.,20.,.2,.1,2.,10.) == 2R.respiration(10.,20.,.2,.1,2.,0.)
        @test_throws DomainError R.co2_forcing(0,280)
    end
    @testset "Ocean conservation and spatial-temporal refinement" begin
        uniform,flux = R.diffuse_step(fill(2.,10),2.,.1,.1,.02)
        @test uniform ≈ fill(2.,10)
        @test abs(flux) < 1e-13
        zero,flux0 = R.diffuse_step(zeros(10),0.,.1,.1,.02)
        @test all(iszero,zero) && flux0 == 0
        t0 = collect(range(0.,1.,length=10))
        updated,flux = R.diffuse_step(t0,2.,.1,.1,.02)
        @test .1sum(updated-t0) ≈ .02flux atol=1e-14
        # Exact eigenmode: T=sin(pi*z/(2L))*exp[-k*(pi/(2L))^2*t].
        errors = Float64[]
        for n in [10,20,40]
            dz=1/n; dt=.2/n^2; z=((1:n).-0.5).*dz
            t=sin.(pi.*z./2)
            for j in 1:n^2
                t,_=R.diffuse_step(t,0.,.1,dz,dt)
            end
            truth=sin.(pi.*z./2).*exp(-.1*(pi/2)^2*.2)
            push!(errors,maximum(abs.(t-truth)))
        end
        @test all(3.8 .< errors[1:2]./errors[2:3] .< 4.2)
    end
    @testset "Sea-level limits and ODE accuracy" begin
        @test R.glacier_rhs(0.,-.15;beta=.01,volume=.5,exponent=1.) == 0
        @test R.glacier_rhs(.5,2.;beta=.01,volume=.5,exponent=.7) == 0
        @test_throws DomainError R.glacier_rhs(.51,2.;beta=.01,volume=.5,exponent=.7)
        # n=1 permits an independent exponential solution.
        f=(t,s)->R.glacier_rhs(s,1.;beta=.01,volume=.5,exponent=1.)
        numerical=R.rk4(f,0.,0.,.25,400)[end]
        @test numerical ≈ .5*(1-exp(-.01*1.15/.5*100)) rtol=1e-10
        g=cfg["greenland"]
        f=(t,v)->R.greenland_rhs(v,g["temperature"];c=g["c"],b=g["b"],alpha=g["alpha"],beta=g["beta"])
        eq=g["c"]*g["temperature"]+g["b"]
        rate=g["alpha"]*g["temperature"]+g["beta"]
        truth=eq+(g["initial_volume"]-eq)*exp(-rate*g["duration"])
        errors=[abs(R.rk4(f,g["initial_volume"],0.,dt,Int(g["duration"]/dt))[end]-truth) for dt in g["steps"]]
        @test all(15 .< errors[1:3]./errors[2:4] .< 19)
        @test R.greenland_rhs(eq,g["temperature"];c=g["c"],b=g["b"],alpha=g["alpha"],beta=g["beta"]) == 0
        @test R.thermal_expansion(0.,1e-25) == 0
        @test R.thermal_expansion(1e24,1e-25) ≈ .1
        @test R.fast_ice_loss(2.;threshold=2.,rate=.001) == 0
        @test R.fast_ice_loss(3.;threshold=2.,rate=.001) == .001
        @test R.accumulate_storage([.001,-.001],.0) ≈ [.001,0]
        @test R.antarctic_ocean_temperature(-4.;a=1.,b=0.) < -1.8
    end
    @testset "Spatial accounting and reference periods" begin
        components=[.1 .2; .2 .3]; factors=ones(2,2)
        local_sl=R.local_sea_level(factors,components,[.001,-.001],[2000,2010],2000)
        @test local_sl ≈ [.3 .51; .3 .49]
        # Area-weighted mean fingerprints of1 conserve global component sum.
        factors=[.5 1.5;1.5 .5]
        @test vec(mean(R.local_sea_level(factors,components,zeros(2),[2000,2010],2000),dims=1)) ≈ vec(sum(components,dims=1))
        @test R.rebase(1995:2014,collect(1.:20.),1995,2014) |> mean ≈ 0 atol=1e-14
        @test_throws ArgumentError R.rebase(2000:2010,zeros(11),1995,2014)
        @test_throws ArgumentError R.rebase([2000,2002],[0.,1.],2000,2002)
    end
    @testset "Extreme levels and flood integration" begin
        for shape in [-.2,0.,.2], p in [.001,.2,.9,.999]
            d=(location=1.,scale=.3,shape=shape)
            x=R.gev_quantile(p;d...)
            @test R.gev_cdf(x;d...) ≈ p atol=1e-13
        end
        for shape in [-.2,0.,.2]
            d=(location=1.,scale=.3,shape=shape)
            a=R.gev_quantile(.001;d...); b=R.gev_quantile(.999;d...)
            @test R.simpson(x->R.gev_pdf(x;d...),a,b,4096) ≈ .998 rtol=1e-8
        end
        @test R.simpson(x->x^3,0.,2.,10) ≈ 4.
        edges=[0.,1.,2.,5.]; areas=[1.,1.,3.]
        kw=(min_elevation=0.,capital_density=1e6,population_density=100.,mortality=.01,value_of_life=1e5,resilience=.2)
        damage=w->R.flood_damage(w,edges,areas;kw...)
        @test damage(0.) == 0
        # Independent high-resolution integral over uniform elevation density.
        direct=.8R.simpson(e->1e6*(1.7-e)/(1+1.7-e)+1e5,0.,1.7,1000)
        @test damage(1.7) ≈ direct rtol=1e-11
        @test all(diff(damage.([0.,.5,1.,2.,3.,5.,10.])) .> 0)
        @test R.flood_damage(1.,edges,areas;merge(kw,(min_elevation=1.,))...) == 0
        # Thresholded integral cannot exceed the unprotected integral.
        d=(location=1.,scale=.3,shape=.1)
        unprotected=R.expected_flood_loss(damage,d;lower=-2.,upper=20.,panels=8192)
        protected=R.expected_flood_loss(damage,d;lower=2.,upper=20.,panels=8192)
        @test 0 < protected < unprotected
        @test R.expected_flood_loss(x->0.,d;lower=-2.,upper=20.) == 0
        @test_throws ArgumentError R.simpson(identity,0.,1.,3)
    end
    @testset "Cost accounting and optimization" begin
        proactive=R.relocation_cost(1.,100.,2.,1000.)
        @test proactive ≈ 262.5
        @test R.relocation_cost(1.,100.,2.,1000.;reactive=true) == 5proactive
        @test R.inundation_cost(1.,10.,100.;depreciation=1.) == 10
        @test R.inundation_cost(1.,10.,100.) == 85
        @test R.protection_cost(2.,3.,10.).construction == 180
        @test R.wetland_loss(2.,1.,100.,.005) == 25
        @test R.wetland_loss(2.,1.,100.,.005;protected=true) == 100
        years=2010:2110
        pv=R.present_value(ones(101),years)
        ratio=1/1.04
        @test pv ≈ (1-ratio^101)/(1-ratio) rtol=1e-13
        @test R.present_value(ones(101),years;rate=0.) == 101
        @test R.present_value([100.],[2020]) ≈ 100/1.04^10
        costs=[1. 3.;2. 2.;5. 1.]
        selected=R.choose_adaptation(costs,[2010,2011])
        independent=[1+3/1.04,2+2/1.04,5+1/1.04]
        @test selected.choice == argmin(independent)
        @test selected.value ≈ minimum(independent)
        @test R.choose_adaptation(ones(2,2),[2010,2011]).choice == 1
        @test_throws DomainError R.inundation_cost(-1.,10.,100.)
    end
    @testset "Ensemble and regional arithmetic" begin
        @test R.warming_bin.([1.5,1.50001,2.5,2.50001,3.5,3.50001]) == [1,2,2,3,3,4]
        @test_throws DomainError R.warming_bin(NaN)
        rows=hcat(collect(1:100),3 .*collect(1:100))
        a,ia=R.subsample_joint(MersenneTwister(cfg["seed"]),rows,10)
        b,ib=R.subsample_joint(MersenneTwister(cfg["seed"]),rows,10)
        @test ia == ib && a == b && length(unique(ia)) == 10
        @test a[:,2] == 3a[:,1]
        s=R.conditional_summary([1.,2.,3.,4.],[10.,20.,30.,40.])
        @test all(x.n == 1 for x in s)
        @test s[2].quantiles == [20.,20.,20.]
        @test isnan(R.conditional_summary([1.],[10.])[2].quantiles[1])
        r=R.regional_percentages([1.,9.],[100.,300.])
        @test r.global_percent == 2.5
        @test r.excess ≈ [-1.5,.5]
        @test sum(r.excess.*[100.,300.]) ≈ 0
    end
end

counts=Test.get_test_counts(suite)
mkpath(joinpath(ROOT,"results"))
open(joinpath(ROOT,"results","julia_tests.toml"),"w") do io
    TOML.print(io,Dict("passed"=>counts[1]+counts[5],"failed"=>counts[2]+counts[6],
                      "errors"=>counts[3]+counts[7],"broken"=>counts[4]+counts[8],
                      "scope"=>"Manufactured component verification; no target ensemble"))
end
