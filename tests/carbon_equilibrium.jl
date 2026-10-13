using Test,DelimitedFiles,Statistics
include("../src/RecoveredModels.jl")
include("../src/CarbonCycle.jl")
const C=CarbonCycle
@testset "Equivalent carbonate equilibrium solvers" begin
    maximum_difference=0.
    for c0 in (275.,280.,285.,295.), perturbation in (-100.,0.,10.,100.,500.,1000.,3000.,10000.)
        p=C.parameters(c0=c0);fast=C.parameters(c0=c0,fast_equilibrium=true)
        a=C.partition(perturbation,p);b=C.partition(perturbation,fast)
        maximum_difference=max(maximum_difference,abs(a.co2-b.co2))
        @test abs(a.co2-b.co2)<1e-6
        @test abs(b.atmosphere+b.mixed-perturbation)<1e-10
        @test abs(b.co2/fast.solubility*(fast.k1/b.hydrogen+2fast.k1*fast.k2/b.hydrogen^2)+
            fast.boron/(1+b.hydrogen/fast.kb)+fast.kw/b.hydrogen-b.hydrogen-fast.alk)<1e-15
    end
    e=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
    e=e[1850 .<=e[:,1].<=2021,:];number(x)=x=="" ? 0. : Float64(x)
    q=number.(e[:,2])+number.(e[:,3])-number.(e[:,4])
    t=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)[:,2];t.-=mean(t[1:30])
    for (beta,c0,q10,exchange) in ((.67,280.,2.,16.87),(.85,284.,4.5,150.),(.3,275.,.3,1.))
        p=C.parameters(beta=beta,c0=c0,q10=q10,exchange=exchange)
        fast=C.parameters(beta=beta,c0=c0,q10=q10,exchange=exchange,fast_equilibrium=true)
        a=C.prescribed_run(q,t;p=p);b=C.prescribed_run(q,t;p=fast)
        aa=[C.partition(x,p).co2 for x in a[1,:]]
        bb=[C.partition(x,fast).co2 for x in b[1,:]]
        @test maximum(abs.(aa-bb))<1e-6
        @test maximum(abs.(a-b))<1e-6
    end
    println("Maximum isolated concentration difference (ppm): ",maximum_difference)
end
