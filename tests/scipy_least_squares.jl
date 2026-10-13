using Test
include("../src/SciPyLeastSquares.jl")
const S=SciPyLeastSquares
@testset "SciPy optimizer bridge and constrained solutions" begin
    a=S.fit(u->[u[1]-.35,2*(u[2]+.3),3*(u[3]-1.4)],[.8,.8,.2])
    @test a.u≈[.35,0.,1.] atol=1e-7
    @test a.objective≈1.8 atol=1e-9
    @test a.residual_evaluations>=a.iterations
    b=S.fit(u->[10*(u[2]-u[1]^2),1-u[1]],[.05,.9])
    @test b.u≈[1.,1.] atol=1e-4
    @test b.objective<1e-8
    @test b.stop!="evaluation_limit"
end
