using DelimitedFiles, Statistics, TOML, Random, LinearAlgebra
include(joinpath(@__DIR__,"..","src","RecoveredModels.jl"))
include(joinpath(@__DIR__,"..","src","Reproduction.jl"))
const M=RecoveredModels
const R=Reproduction
const ROOT=normpath(joinpath(@__DIR__,".."))
function savecsv(name,header,rows)
    open(joinpath(ROOT,"results",name),"w") do io
        println(io,join(header,","))
        for row in rows; println(io,join(row,",")); end
    end
end

rows=[]
for ecs in (1.5,3.0,4.5), kap in (0.25,0.55,2.0)
    s=M.climate_system(ecs=ecs,diffusivity=kap,cells=160)
    state=M.climate_run(s,fill(3.7,201);substeps=8)
    for j in 1:201
        push!(rows,(ecs,kap,j-1,M.global_temperature(s,state[:,j]),
            M.ocean_heat(s,state[:,j])/1e22,M.ocean_heat(s,state[:,j];mixed_depth=57.5)/1e22))
    end
end
savecsv("climate_step_sensitivity.csv",["ecs_K","diffusivity_cm2_s","year_after_step","temperature_K","effective_heat_1e22J","water_heat_1e22J"],rows)

rows=[]
for cells in (40,80,160,320)
    s=M.climate_system(cells=cells)
    # One percent CO2 growth per year implies a linear radiative-forcing ramp.
    q=3.7.*log2.(1.01.^(0:140))
    state=M.climate_run(s,q;substeps=8)
    push!(rows,(cells,M.global_temperature(s,state[:,71]),M.ocean_heat(s,state[:,71])/1e22,
        M.global_temperature(s,state[:,141]),M.ocean_heat(s,state[:,141])/1e22))
end
savecsv("climate_grid_convergence.csv",["cells","temperature_year70_K","heat_year70_1e22J","temperature_year140_K","heat_year140_1e22J"],rows)

p=M.dais_parameters()
req=M.bisect(r->M.dais_radius_rhs(r,-18.,0.,0.,.72,p),1.5e6,2.1e6)
v0=M.dais_geometry(req,0.,p).volume
rows=[]
for rule in (:paper,:local_height), warming in (0.,2.,4.,6.)
    # Prescribed Antarctic warming experiments; not globally calibrated scenarios.
    rhs=(t,r)->M.dais_radius_rhs(r,-18.0+warming*min(t/100,1),0.,0.,.72,p;runoff_rule=rule)
    rr=R.rk4(rhs,req,0.,.25,800)
    for j in 1:4:length(rr)
        v=M.dais_geometry(rr[j],0.,p).volume
        push!(rows,(string(rule),warming,(j-1)*.25,rr[j],v/1e15,(v0-v)*p.rhoi/p.rhow/3.62e14))
    end
end
savecsv("dais_warming_sensitivity.csv",["runoff_rule","antarctic_warming_K","year","radius_m","volume_1e15m3","mass_equivalent_sea_level_m"],rows)

rows=[]
for dt in (1.,.5,.25,.125)
    rhs=(t,r)->M.dais_radius_rhs(r,-18.0+6*min(t/100,1),0.,0.,.72,p)
    rr=R.rk4(rhs,req,0.,dt,Int(200/dt))
    push!(rows,(dt,rr[end],M.dais_geometry(rr[end],0.,p).volume/1e15))
end
savecsv("dais_time_convergence.csv",["step_years","radius_200_m","volume_200_1e15m3"],rows)

rng=MersenneTwister(20251035)
rows=[]
for p in M.SOCIO_PRIORS
    x=[M.truncated_normal(rng,p.mean,p.sd,p.lo,p.hi) for j in 1:20000]
    push!(rows,(p.name,p.mean,p.sd,p.lo,p.hi,mean(x),std(x),quantile(x,.05),median(x),quantile(x,.95)))
end
savecsv("socioeconomic_prior_check.csv",["parameter","normal_mean","normal_sd","lower","upper","sample_mean","sample_sd","q05","q50","q95"],rows)
open(joinpath(ROOT,"results","recovered_benchmarks.toml"),"w") do io
    TOML.print(io,Dict("dais_equilibrium_radius_m"=>req,"dais_equilibrium_volume_m3"=>v0,
        "shaffer2014_printed_volume_m3"=>24.78e15,"relative_volume_discrepancy"=>v0/24.78e15-1,
        "scope"=>"Methodological benchmark and sensitivity experiments; not Wong2025 numerical reproduction"))
end
println("Recovered mechanism diagnostics completed; alternatives are not target reproductions.")
