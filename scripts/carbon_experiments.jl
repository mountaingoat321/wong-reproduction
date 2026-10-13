using DelimitedFiles,Statistics,TOML
include("../src/RecoveredModels.jl")
include("../src/Reproduction.jl")
include("../src/CarbonCycle.jl")
const M=RecoveredModels;const R=Reproduction;const C=CarbonCycle
data,_=readdlm("inputs/gcb2023_emissions.csv",',',Any;header=true)
forcing,_=readdlm("inputs/ssp_forcing.csv",',',Any;header=true)
rows=forcing[forcing[:,1].=="ssp245",:]
year=Int.(data[:,1]);@assert year==collect(1750:2022)
number(x)=x=="" ? 0.0 : Float64(x)
fossil=number.(data[:,2]);lu=number.(data[:,3]);cement=number.(data[:,4])
missing=findall(x->x=="",data[:,3]);@assert all(year[missing].<1850)
nonco2=Float64.(rows[:,3])-Float64.(rows[:,4])
sys=M.climate_system(ecs=3.,diffusivity=.55,cells=80)
baseline=nothing
open("results/carbon_historical_sensitivity.csv","w") do io
    println(io,"pre1850_land_use_GtC_yr,beta,q10,year,co2_ppm,temperature_K,carbon_balance_error_GtC")
    for prior_lu in (0.,.72141),beta in (.15,.287,.6),q10 in (1.,2.,3.)
        emissions=fossil+lu-cement;emissions[missing].+=prior_lu
        p=C.parameters(beta=beta,q10=q10)
        run=C.coupled_run(sys,emissions,nonco2[1:length(year)];p=p,substeps=8)
        cumulative=vcat(0.,cumsum((emissions[1:end-1]+emissions[2:end])/2))
        for i in eachindex(year)
            year[i]<1950 && continue
            balance=sum(run.carbon[:,i])-sum(C.initial_state())-cumulative[i]
            println(io,join((prior_lu,beta,q10,year[i],C.partition(run.carbon[1,i],p).co2,
                M.global_temperature(sys,run.climate[:,i]),balance),","))
        end
        if prior_lu==0 && beta==.287 && q10==2
            global baseline=(run=run,emissions=emissions,p=p)
        end
    end
end
open("results/carbon_emission_scenarios.csv","w") do io
    println(io,"peak_year,year,emissions_GtCO2_yr,co2_ppm,temperature_relative1850_1900_K,water_heat_change2010_1e22J,carbon_balance_error_GtC")
    ref=mean([M.global_temperature(sys,baseline.run.climate[:,i]) for i in findall(y->1850<=y<=1900,year)])
    h0=M.ocean_heat(sys,baseline.run.climate[:,2010-1749];mixed_depth=57.5)
    for peak in (2035,2070,2100)
        years,q=R.emissions(2022,2150,baseline.emissions[end]*3.664,.004,peak,.07)
        e=q/3.664
        run=C.coupled_run(sys,e,nonco2[2022-1749:end];p=baseline.p,substeps=8,
            carbon_initial=baseline.run.carbon[:,end],climate_initial=baseline.run.climate[:,end])
        cumulative=vcat(0.,cumsum((e[1:end-1]+e[2:end])/2))
        for i in eachindex(years)
            println(io,join((peak,years[i],q[i],C.partition(run.carbon[1,i],baseline.p).co2,
                M.global_temperature(sys,run.climate[:,i])-ref,
                (M.ocean_heat(sys,run.climate[:,i];mixed_depth=57.5)-h0)/1e22,
                sum(run.carbon[:,i])-sum(run.carbon[:,1])-cumulative[i]),","))
        end
    end
end
open("results/carbon_chemistry.toml","w") do io
    p=baseline.p
    fraction=(C.partition(.01,p).mixed-C.partition(-.01,p).mixed)/.02
    TOML.print(io,Dict("dic_preindustrial_mol_L"=>p.dic0,"hydrogen_preindustrial_mol_L"=>p.hydrogen0,
        "small_perturbation_mixed_fraction"=>fraction,"scope"=>"H99 chemistry with T08 transport and S87/R08 land feedback; uncalibrated alternative"))
end
println("18 historical carbon sensitivities and 3 emissions scenarios complete; all are alternatives.")
