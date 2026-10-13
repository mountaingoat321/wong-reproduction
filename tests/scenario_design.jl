using Test,TOML
include("../src/ScenarioDesign.jl")
const S=ScenarioDesign
suite=@testset "Constrained alternative emissions probabilities" begin
    w=S.budget_weights([true,false,false,false],.5)
    @test sum(w)≈1
    @test w[1]≈.5
    @test w[2]==w[3]==w[4]
    entropy(v)=sum(x*log(4x) for x in v)
    for perturbation in (.01,.05,-.02)
        v=copy(w);v[2]+=perturbation;v[3]-=perturbation
        @test entropy(v)>entropy(w) # a feasible perturbation raises relative entropy
    end
    @test_throws ArgumentError S.budget_weights(trues(4),.5)
    @test_throws DomainError S.budget_weights([true,false],1.1)
    @test S.weighted_quantile([4.,1.,2.],[.1,.6,.3],.5)==1.
    @test S.weighted_quantile([4.,1.,2.],[.1,.6,.3],.9)==2.
    @test S.weighted_quantile([4.,1.,2.],[.1,.6,.3],1.)==4.
    @test S.weighted_quantile([0.,1.],[0.,1.],0.)==1.
end
counts=Test.get_test_counts(suite)
open("results/scenario_design_test_summary.toml","w") do io
    TOML.print(io,Dict("passed"=>counts[1]+counts[5],"failed"=>counts[2]+counts[6],"errors"=>counts[3]+counts[7]))
end
