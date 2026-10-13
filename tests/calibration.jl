using Test, LinearAlgebra, Random, Statistics, TOML
include(joinpath(@__DIR__,"..","src","Calibration.jl"))
const C=Calibration
suite=@testset "Independent calibration likelihood and sampler" begin
    residual=[.2,-.1,.4,.3,-.2];sd=[.02,.05,.03,.04,.06]
    for rho in (0.0,.5,.95)
        sigma=.12; n=length(residual)
        covariance=[sigma^2/(1-rho^2)*rho^abs(i-j) for i in 1:n,j in 1:n]+Diagonal(sd.^2)
        dense=-.5*(n*log(2pi)+logdet(covariance)+dot(residual,covariance\residual))
        @test C.ar1_loglikelihood(residual,sigma,rho,sd)≈dense atol=1e-12
    end
    result=C.metropolis(x->-sum(abs2,x)/2,[1.0,-1.0],[.3,.3],MersenneTwister(875);
        warmup=2000,draws=12000)
    @test maximum(abs.(mean(result.samples,dims=1)))<.08
    @test maximum(abs.(var(result.samples,dims=1).-1))<.12
    @test .1<result.acceptance<.7
    # Uniform physical priors require Jacobians in transformed coordinates.
    logistic(z)=1/(1+exp(-z))
    density(z)=log(logistic(z[1]))+log1p(-logistic(z[1]))
    uniform=C.metropolis(density,[0.0],[.3],MersenneTwister(341);
        warmup=2000,draws=12000,adapt_window=1000,proposal_scale=1.8)
    x=logistic.(uniform.samples[:,1])
    @test abs(mean(x)-.5)<.03
    @test abs(var(x)-1/12)<.015
end
open("results/calibration_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>Test.get_test_counts(suite)[1],"failed"=>0,"errors"=>0))
end
