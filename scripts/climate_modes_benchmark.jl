using DelimitedFiles
include("../src/RecoveredModels.jl")
const M=RecoveredModels
data,_=readdlm("inputs/ssp_forcing.csv",',',Any;header=true)
q=Float64.(data[(data[:,1].=="ssp245").&(data[:,2].<=2021),3])
open("results/climate_modes_comparison.csv","w") do io
    println(io,"ecs_K,diffusivity_cm2_s,cn_substeps,max_temperature_difference_K,max_heat700_difference_1e22J,cn_wall_seconds,exact_wall_seconds")
    for (ecs,kap) in ((1.2,.15),(3.,.55),(6.,3.0))
        s=M.climate_system(ecs=ecs,diffusivity=kap)
        M.climate_observables(s,q);M.climate_run(s,q)
        timing=@elapsed exact=M.climate_observables(s,q)
        for steps in (4,8,16)
            cn_time=@elapsed x=M.climate_run(s,q;substeps=steps)
            t=[M.global_temperature(s,x[:,i]) for i in eachindex(q)]
            heat=[M.ocean_heat_to_depth(s,x[:,i],700.)/1e22 for i in eachindex(q)]
            println(io,join((ecs,kap,steps,maximum(abs.(t-exact.temperature)),
                maximum(abs.(heat-exact.heat[1,:])),cn_time,timing),","))
        end
    end
end
