using DelimitedFiles,Statistics,TOML
include("../src/RecoveredModels.jl")
include("../src/CarbonCycle.jl")
const C=CarbonCycle
e=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
e=e[1850 .<=e[:,1].<=2021,:];number(x)=x=="" ? 0. : Float64(x)
q=number.(e[:,2])+number.(e[:,3])-number.(e[:,4])
t=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)[:,2];t.-=mean(t[1:30])
p=C.parameters(beta=.72,c0=283.5,q10=2.2,exchange=24.)
fast=C.parameters(beta=.72,c0=283.5,q10=2.2,exchange=24.,fast_equilibrium=true)
# Warm both paths before recording five serial historical integrations.
a=C.prescribed_run(q,t;p=p);b=C.prescribed_run(q,t;p=fast)
old=[@elapsed C.prescribed_run(q,t;p=p) for _ in 1:5]
new=[@elapsed C.prescribed_run(q,t;p=fast) for _ in 1:5]
aa=[C.partition(x,p).co2 for x in a[1,:]]
bb=[C.partition(x,fast).co2 for x in b[1,:]]
@assert maximum(abs.(aa-bb))<1e-6 && maximum(abs.(a-b))<1e-6
result=Dict("scope"=>"Numerical equivalence and local timing, not target calibration",
    "years"=>172,"substeps_per_year"=>8,"timing_replicates"=>5,
    "maximum_co2_difference_ppm"=>maximum(abs.(aa-bb)),
    "maximum_state_difference_GtC"=>maximum(abs.(a-b)),
    "bisection_median_seconds"=>median(old),"newton_median_seconds"=>median(new),
    "median_speedup"=>median(old)/median(new),"newton_alkalinity_tolerance_mol_L"=>1e-16,
    "bisection_remains_default"=>true)
open("results/carbon_equilibrium_comparison.toml","w") do io;TOML.print(io,result);end
TOML.print(stdout,result)
