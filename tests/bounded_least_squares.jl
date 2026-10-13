using Test
include("../src/BoundedLeastSquares.jl")
const B=BoundedLeastSquares
@testset "Bound-aware damped least squares" begin
    # Constrained solution is analytic, with one coordinate on each bound.
    x=B.fit(u->[u[1]-.35,2*(u[2]+.3),3*(u[3]-1.4)],[.8,.8,.2])
    @test x.u ≈ [.35,0.,1.] atol=1e-7
    @test x.objective ≈ .36+1.44 atol=1e-10
    @test x.stop=="projected_gradient"
    # Nonlinear valley: clipping the full Newton step is insufficient.
    y=B.fit(u->[10*(u[2]-u[1]^2),1-u[1]],[.05,.9];iterations=150)
    @test y.u ≈ [1.,1.] atol=1e-5
    @test y.objective<1e-10
    # A poor, nearly singular initial Jacobian must not terminate after one rejection.
    z=B.fit(u->[u[1]^2-.81,u[2]-u[1]],[.001,.9])
    @test z.u ≈ [.9,.9] atol=1e-6
end
