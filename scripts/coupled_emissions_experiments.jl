using DelimitedFiles,Statistics,Random,TOML
include("../src/RecoveredModels.jl");include("../src/Reproduction.jl")
include("../src/CarbonCycle.jl");include("../src/ScenarioDesign.jl")
const M=RecoveredModels;const R=Reproduction;const C=CarbonCycle;const S=ScenarioDesign
function main()
    pilot="--pilot" in ARGS;perclass=pilot ? 4 : 128
    tail="--tail-stratified" in ARGS
    substeps=tail ? 16 : 8
    prefix="coupled_emissions"*(tail ? "_stratified" : "")*(pilot ? "_pilot" : "")
    seed=tail ? 20251043 : 20251040;rng=MersenneTwister(seed);started=time()
    @assert TOML.parsefile("results/climate_joint_mcmc_status.toml")["convergence_criteria_met"]
    draws=readdlm("results/emissions_alternative_samples.csv",',',Float64;skipstart=1)
    inside=findall(draws[:,6].<=1223);outside=findall(draws[:,6].>1223)
    # Balanced conditional subsamples improve representation of the rare
    # budget event. The three probability measures receive distinct weights.
    prior_probability=length(inside)/size(draws,1)
    if tail
        sorted=outside[sortperm(draws[outside,6])]
        groups=[inside,sorted[1:end-500],sorted[end-499:end-100],sorted[end-99:end-10],sorted[end-9:end]]
        counts=pilot ? [2,2,2,1,1] : [96,64,48,32,10]
        indices=Int[];weightrows=[]
        for (g,group) in enumerate(groups)
            selected=group[randperm(rng,length(group))[1:counts[g]]]
            append!(indices,selected)
            for _ in selected
                prior=length(group)/size(draws,1)/counts[g]
                w50=g==1 ? .5/counts[g] : .5*length(group)/length(outside)/counts[g]
                w75=g==1 ? .75/counts[g] : .25*length(group)/length(outside)/counts[g]
                push!(weightrows,[prior,w50,w75])
            end
        end
        n=length(indices);weights=permutedims(hcat(weightrows...))
        @assert all(abs.(sum(weights,dims=1).-1).<1e-12)
    else
        a=inside[randperm(rng,length(inside))[1:perclass]];b=outside[randperm(rng,length(outside))[1:perclass]]
        indices=vec(permutedims(hcat(a,b)));n=length(indices)
        weights=hcat([isodd(j) ? prior_probability/perclass : (1-prior_probability)/perclass for j in 1:n],
                     fill(1/n,n),[isodd(j) ? .75/perclass : .25/perclass for j in 1:n])
    end
    posterior=readdlm("results/climate_joint_posterior.csv",',',Float64;skipstart=1)
    climate_indices=randperm(rng,size(posterior,1))[1:n]
    theta=posterior[climate_indices,3:11]
    forcing=readdlm("inputs/ssp_forcing.csv",',',Any;skipstart=1)
    sspe=readdlm("inputs/ssp_emissions.csv",',',Any;skipstart=1)
    observations=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)
    gcb=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
    histgcb=gcb[1850 .<=gcb[:,1].<=2021,:]
    number(x)=x=="" ? 0. : Float64(x) # same missing-cement convention as carbon fit
    historical_emissions=number.(histgcb[:,2])+number.(histgcb[:,3])-number.(histgcb[:,4])
    observed_reference=mean(observations[1:30,2])
    observed_temperature=observations[:,2].-observed_reference
    fits=readdlm("results/carbon_conditional_fit.csv",',',Any;skipstart=1)
    fitted=fits[findfirst(i->fits[i,1]==2 && fits[i,2]==16.87,axes(fits,1)),3]
    carbon_parameters=C.parameters(beta=fitted,q10=2.,exchange=16.87)
    carbon_history=C.prescribed_run(historical_emissions,observed_temperature;p=carbon_parameters,substeps=8)
    initial_carbon=carbon_history[:,end]
    scenarios=["ssp119","ssp126","ssp245","ssp370","ssp460","ssp585"]
    all_years=collect(1750:2150);years=collect(2021:2150)
    ssptotal=zeros(length(all_years),6);sspco2=similar(ssptotal);sspaerosol=similar(ssptotal);sspcm=similar(ssptotal)
    for (j,scenario) in enumerate(scenarios)
        f=forcing[forcing[:,1].==scenario,:];e=sspe[sspe[:,1].==scenario,:]
        @assert Int.(f[:,2])==all_years && Int.(e[:,2])==all_years
        ssptotal[:,j]=f[:,3];sspco2[:,j]=f[:,4];sspaerosol[:,j]=f[:,5];sspcm[:,j]=e[:,3]
    end
    history_index=1:(2021-1749);future_index=(2021-1749):length(all_years)
    preindustrial=findall(y->1850<=y<=1900,all_years[history_index])
    modern_reference=findall(y->1961<=y<=1990,all_years[history_index])
    raw_path=".local/"*prefix*"_paths.csv"
    endpoints=[];selected_rows=[];checks=[]
    distributions=["documented_prior","alternative_budget50","alternative_budget75"]
    open("results/"*prefix*"_quantiles.csv","w") do qio
    open(raw_path,"w") do raw
        println(raw,"sample,forcing_rule,year,emissions_GtCO2_yr,co2_ppm,temperature_1850_1900_K,temperature_1961_1990_K,heat2000_change2010_1e22J,heatfull_change2010_1e22J,nearest_SSP")
        println(qio,"forcing_rule,distribution,year,temperature_q05_K,temperature_q50_K,temperature_q95_K,co2_q05_ppm,co2_q50_ppm,co2_q95_ppm")
        for rule in ("annual_nearest_emissions","fixed_ssp245")
            temperatures=zeros(n,length(years));concentrations=similar(temperatures)
            for j in 1:n
                i=indices[j];emission=draws[i,:];par=theta[j,:]
                _,future=R.emissions(2022,2150,TOML.parsefile("results/emissions_design_audit.toml")["initial_emissions_GtCO2_yr"],emission[2],Int(emission[5]),emission[4])
                q=vcat(historical_emissions[end]*3.664,future)
                chosen=rule=="fixed_ssp245" ? fill(3,length(years)) :
                    [argmin(abs.(sspcm[future_index[k],:].-q[k])) for k in eachindex(years)]
                chosen[1]=3 # historical endpoint uses its calibrated forcing
                nonco2=[ssptotal[future_index[k],chosen[k]]-sspco2[future_index[k],chosen[k]]+
                        (par[3]-1)*sspaerosol[future_index[k],chosen[k]] for k in eachindex(years)]
                sys=M.climate_system(ecs=par[1],diffusivity=par[2],cells=80)
                historical=M.climate_observables(sys,ssptotal[history_index,3]+(par[3]-1)*sspaerosol[history_index,3])
                ref=mean(historical.temperature[preindustrial]);modern=mean(historical.temperature[modern_reference])
                offset=modern-par[4]+observed_reference
                function future_run(substeps)
                    C.coupled_run(sys,q/3.664,nonco2;p=carbon_parameters,substeps=substeps,
                        carbon_initial=initial_carbon,climate_initial=historical.final_state,carbon_temperature_offset=offset)
                end
                out=future_run(substeps)
                co2=[C.partition(out.carbon[1,k],carbon_parameters).co2 for k in eachindex(years)]
                t=[M.global_temperature(sys,out.climate[:,k]) for k in eachindex(years)]
                temperatures[j,:]=t.-ref;concentrations[j,:]=co2
                h2000=historical.heat[2,2010-1749];hfull=historical.heat[3,2010-1749]
                cumulative=vcat(0.,cumsum((q[1:end-1]+q[2:end])/2/3.664))
                mass_error=maximum(abs.(vec(sum(out.carbon,dims=1)).-sum(initial_carbon).-cumulative))
                if pilot
                    fine=future_run(2substeps)
                    fine_temp=[M.global_temperature(sys,fine.climate[:,k]) for k in eachindex(years)]
                    fine_co2=[C.partition(fine.carbon[1,k],carbon_parameters).co2 for k in eachindex(years)]
                    push!(checks,(j,rule,mass_error,maximum(abs.(t-fine_temp)),maximum(abs.(co2-fine_co2))))
                end
                y2100=findfirst(==(2100),years);window=findall(y->2081<=y<=2100,years)
                switches=count(diff(chosen).!=0)
                push!(endpoints,(j,rule,i,climate_indices[j],emission[6],temperatures[j,y2100],mean(temperatures[j,window]),co2[y2100],switches,mass_error,weights[j,:]...))
                if rule=="annual_nearest_emissions"
                    push!(selected_rows,(j,i,climate_indices[j],par...,weights[j,:]...))
                end
                for k in eachindex(years)
                    println(raw,join((j,rule,years[k],q[k],co2[k],t[k]-ref,t[k]-modern+par[4],
                        M.ocean_heat_to_depth(sys,out.climate[:,k],2000.)/1e22-h2000,
                        M.ocean_heat(sys,out.climate[:,k];mixed_depth=57.5)/1e22-hfull,scenarios[chosen[k]]),","))
                end
                if j%16==0;println(rule," ",j,"/",n," elapsed ",round(time()-started,digits=1)," seconds");flush(stdout);end
            end
            for d in 1:3,k in eachindex(years)
                tq=[S.weighted_quantile(temperatures[:,k],weights[:,d],p) for p in (.05,.5,.95)]
                cq=[S.weighted_quantile(concentrations[:,k],weights[:,d],p) for p in (.05,.5,.95)]
                println(qio,join((rule,distributions[d],years[k],tq...,cq...),","))
            end
        end
    end
    end
    function save(suffix,header,rows)
        open("results/"*prefix*suffix,"w") do io
            println(io,header);for row in rows;println(io,join(row,","));end
        end
    end
    save("_endpoints.csv","sample,forcing_rule,emission_sample,climate_posterior_row,cumulative2022_2100_GtCO2,temperature2100_K,temperature2081_2100_K,co2_2100_ppm,SSP_switches,max_mass_error_GtC,weight_prior,weight_budget50,weight_budget75",endpoints)
    save("_parameters.csv","sample,emission_sample,climate_posterior_row,ecs_K,diffusivity_cm2_s,aerosol_scale,offset_K,innovation_sd_K,rho,heat_offset_1e22J,heat_innovation_sd_1e22J,heat_rho,weight_prior,weight_budget50,weight_budget75",selected_rows)
    if pilot;save("_refinement.csv","sample,forcing_rule,max_mass_error_GtC,max_temperature_substep_difference_K,max_co2_substep_difference_ppm",checks);end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("seed"=>seed,"members"=>n,"wall_seconds"=>time()-started,"carbon_beta"=>fitted,
            "scope"=>"NON-REPRODUCTION: paired alternative climate posterior and emissions weights; conditional carbon point fit; no target joint posterior",
            "initialization"=>"Observed-temperature carbon hindcast and forcing-calibrated climate state at2021; datum transformed for carbon feedback; CO2 forcing law changes at restart without tuning",
            "carbon_q10"=>2.,"carbon_exchange_m_yr"=>16.87,"nonco2"=>"Annual absolute-distance nearest SSP total CO2 emissions versus fixedSSP245",
            "resolution"=>"80ocean cells;"*string(substeps)*"Strang/RK4 substeps per year; pilot doubled to"*string(2substeps), "raw_paths"=>raw_path,
            "sampling"=>(tail ? "Five emission-budget strata: budget event; outside through overall95th;95–99th;99–99.9th;top0.1%; exact empirical class-mass weights" : "Balanced inside/outside budget event")))
    end
end
main()
