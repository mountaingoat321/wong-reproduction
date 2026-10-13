using TOML, DelimitedFiles, Random, Statistics
include("../src/RecoveredModels.jl")
const M=RecoveredModels
joint="--joint-heat" in ARGS
had5="--hadcrut5" in ARGS
had5 && !joint && error("HadCRUT5 experiment requires --joint-heat")
stem=had5 ? "climate_hadcrut5" : joint ? "climate_joint" : "climate"
output(suffix)="results/"*stem*suffix
cfg=TOML.parsefile("config/"*stem*"_calibration.toml")
status=TOML.parsefile(output("_mcmc_status.toml"))
status["convergence_criteria_met"] || error("Calibration convergence criteria not met; do not silently propagate.")
posterior,_=readdlm(output("_posterior.csv"),',',Float64;header=true)
forcing,_=readdlm("inputs/ssp_forcing.csv",',',Any;header=true)
obs,_=readdlm("inputs/"*(had5 ? "hadcrut5_5010.csv" : "hadcrut4.csv"),',',Float64;header=true)
rng=MersenneTwister(cfg["seed"]+100)
n=1000;indices=randperm(rng,size(posterior,1))[1:n]
parameters=posterior[indices,3:2+length(cfg["parameter_names"])]
open(output("_projection_parameters.csv"),"w") do io
    println(io,"posterior_row,",join(cfg["parameter_names"],","))
    for j in 1:n;println(io,join(vcat(indices[j],parameters[j,:]),","));end
end
function summarize(io,label,years,x)
    for j in eachindex(years)
        println(io,join(vcat([label,years[j]],quantile(x[:,j],[.05,.5,.95])),","))
    end
end
open(output("_scenario_quantiles.csv"),"w") do io
open(output("_sample_convergence.csv"),"w") do io2
    println(io,"scenario,year,q05_K,median_K,q95_K")
    println(io2,"scenario,n,q05_2081_2100_K,median_2081_2100_K,q95_2081_2100_K")
    for scenario in ("ssp119","ssp126","ssp245","ssp370","ssp460","ssp585")
        rows=forcing[forcing[:,1].==scenario,:];years=Int.(rows[:,2])
        total=Float64.(rows[:,3]);aerosol=Float64.(rows[:,5])
        reference=findall(y->1850<=y<=1900,years)
        endwindow=findall(y->2081<=y<=2100,years)
        temperatures=zeros(n,length(years));historical=zeros(n,length(years))
        heat700=zeros(n,length(years));heat2000=zeros(n,length(years));heatfull=zeros(n,length(years))
        for j in 1:n
            theta=parameters[j,:]
            s=M.climate_system(ecs=theta[1],diffusivity=theta[2],cells=cfg["cells"])
            modal=get(cfg,"integrator","crank_nicolson")=="exact_modes"
            if modal
                response=M.climate_observables(s,total+(theta[3]-1)*aerosol)
                t=response.temperature
            else
                x=M.climate_run(s,total+(theta[3]-1)*aerosol;substeps=cfg["substeps"])
                t=[M.global_temperature(s,x[:,i]) for i in eachindex(years)]
            end
            temperatures[j,:]=t.-mean(t[reference])
            if scenario=="ssp245"
                histref=findall(y->1961<=y<=1990,years)
                historical[j,:]=t.-mean(t[histref]).+theta[4]
                if modal
                    heat700[j,:]=response.heat[1,:]
                    heat2000[j,:]=response.heat[2,:]
                    heatfull[j,:]=response.heat[3,:]
                else
                    for i in eachindex(years)
                        heat700[j,i]=M.ocean_heat_to_depth(s,x[:,i],700.)/1e22
                        heat2000[j,i]=M.ocean_heat_to_depth(s,x[:,i],2000.)/1e22
                        heatfull[j,i]=M.ocean_heat(s,x[:,i];mixed_depth=57.5)/1e22
                    end
                end
            end
        end
        summarize(io,scenario,years,temperatures)
        values=vec(mean(temperatures[:,endwindow],dims=2))
        for nn in (250,500,1000)
            println(io2,join(vcat([scenario,nn],quantile(values[1:nn],[.05,.5,.95])),","))
        end
        if scenario=="ssp245"
            fit=findall(y->cfg["fit_start"]<=y<=cfg["fit_end"],obs[:,1])
            hold=findall(y->cfg["holdout_start"]<=y<=cfg["holdout_end"],obs[:,1])
            predictive=zeros(n,length(hold))
            for j in 1:n
                theta=parameters[j,:];sigma=theta[5];rho=theta[6]
                m=0.0;v=sigma^2/(1-rho^2)
                for k in fit
                    sd=(obs[k,4]-obs[k,3])/(2*1.96)
                    residual=obs[k,2]-historical[j,Int(obs[k,1])-years[1]+1]
                    gain=v/(v+sd^2)
                    m=rho*(m+gain*(residual-m));v=rho^2*(1-gain)*v+sigma^2
                end
                r=m+sqrt(v)*randn(rng)
                for (kk,k) in enumerate(hold)
                    kk>1 && (r=rho*r+sigma*randn(rng))
                    sd=(obs[k,4]-obs[k,3])/(2*1.96)
                    predictive[j,kk]=historical[j,Int(obs[k,1])-years[1]+1]+r+sd*randn(rng)
                end
            end
            open(output("_hindcast.csv"),"w") do hio
                println(hio,"year,observed_K,parameter_q05_K,parameter_median_K,parameter_q95_K")
                for k in axes(obs,1)
                    obs[k,1]>2021 && continue
                    i=Int(obs[k,1])-years[1]+1
                    println(hio,join(vcat(obs[k,1:2],quantile(historical[:,i],[.05,.5,.95])),","))
                end
            end
            open(output("_holdout.csv"),"w") do hio
                println(hio,"year,observed_K,predictive_q05_K,predictive_median_K,predictive_q95_K")
                for (kk,k) in enumerate(hold)
                    println(hio,join(vcat(obs[k,1:2],quantile(predictive[:,kk],[.05,.5,.95])),","))
                end
            end
            # Holdout validation of depth-matched heat, fitting only an additive
            # observational datum offset over 1955--2005 for 0--700m heat.
            ocean,_=readdlm("inputs/noaa_ocean.csv",',',Float64;header=true)
            hobs=ocean[ocean[:,1].==700,:]
            hfit=findall(y->1955<=y<2006,hobs[:,2])
            for j in 1:n
                offset=joint ? parameters[j,7] : mean([hobs[k,3]-heat700[j,Int(floor(hobs[k,2]))-years[1]+1] for k in hfit])
                heat700[j,:].+=offset
            end
            open(output("_heat_check.csv"),"w") do hio
                println(hio,"year,observed_1e22J,obs_se_1e22J,q05_1e22J,median_1e22J,q95_1e22J")
                for k in axes(hobs,1)
                    year=Int(floor(hobs[k,2]));year>2021 && continue
                    println(hio,join(vcat([year,hobs[k,3],hobs[k,4]],quantile(heat700[:,year-years[1]+1],[.05,.5,.95])),","))
                end
            end
            if joint
                hhold=findall(y->2006<=y<2022,hobs[:,2]);hpredictive=zeros(n,length(hhold))
                for j in 1:n
                    sigma=parameters[j,8];rho=parameters[j,9];m=0.;v=sigma^2/(1-rho^2)
                    for k in hfit
                        residual=hobs[k,3]-heat700[j,Int(floor(hobs[k,2]))-years[1]+1]
                        gain=v/(v+hobs[k,4]^2)
                        m=rho*(m+gain*(residual-m));v=rho^2*(1-gain)*v+sigma^2
                    end
                    r=m+sqrt(v)*randn(rng)
                    for (kk,k) in enumerate(hhold)
                        kk>1 && (r=rho*r+sigma*randn(rng))
                        hpredictive[j,kk]=heat700[j,Int(floor(hobs[k,2]))-years[1]+1]+r+hobs[k,4]*randn(rng)
                    end
                end
                open(output("_heat_holdout.csv"),"w") do hio
                    println(hio,"year,observed_1e22J,predictive_q05_1e22J,predictive_median_1e22J,predictive_q95_1e22J")
                    for (kk,k) in enumerate(hhold)
                        println(hio,join(vcat([floor(hobs[k,2]),hobs[k,3]],quantile(hpredictive[:,kk],[.05,.5,.95])),","))
                    end
                end
            end
            open(output("_ocean_heat.csv"),"w") do hio
                println(hio,"depth_m,year,q05_change_1e22J,median_change_1e22J,q95_change_1e22J")
                for (depth,h) in ((2000,heat2000),(4057.5,heatfull))
                    h.-=h[:,findfirst(==(2010),years)]
                    summarize(hio,depth,years,h)
                end
            end
        end
        println("Completed alternative ",scenario," with ",n," joint temperature-calibration draws");flush(stdout)
    end
end
end
