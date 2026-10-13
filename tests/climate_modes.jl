using Test,LinearAlgebra,TOML
include("../src/RecoveredModels.jl")
const M=RecoveredModels
suite=@testset "Exact finite-volume climate propagation" begin
    for (ecs,kap) in ((.8,.1),(3.,.55),(8.,3.5))
        s=M.climate_system(ecs=ecs,diffusivity=kap,cells=20)
        q=3.7.*(1 .- exp.(-(0:30)./10))
        exact=M.climate_observables(s,q)
        # Independent dense block exponential: augmented state [x,Q,Qdot].
        n=length(s.forcing);b=zeros(n+2,n+2)
        b[1:n,1:n]=Matrix(s.A);b[1:n,n+1]=s.forcing;b[n+1,n+2]=1
        transition=exp(b);x=zeros(n)
        for i in 2:length(q)
            extended=transition*vcat(x,q[i-1],q[i]-q[i-1]);x=extended[1:n]
        end
        @test exact.temperature[end]≈M.global_temperature(s,x) rtol=2e-11
        @test exact.final_state≈x rtol=2e-11 atol=1e-12
        @test exact.heat[1,end]≈M.ocean_heat_to_depth(s,x,700.)/1e22 rtol=2e-11
        errors=Float64[]
        for steps in (4,8,16)
            cn=M.climate_run(s,q;substeps=steps)
            push!(errors,abs(M.global_temperature(s,cn[:,end])-exact.temperature[end]))
        end
        @test 3.9<errors[1]/errors[2]<4.1
        @test 3.9<errors[2]/errors[3]<4.1
        @test M.climate_observables(s,zeros(5)).temperature==zeros(5)
    end
end
c=Test.get_test_counts(suite)
open("results/climate_modes_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>c[1]+c[5],"failed"=>c[2]+c[6],"errors"=>c[3]+c[7]))
end
