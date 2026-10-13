using TOML,DelimitedFiles,Statistics,Random
include("../src/Reproduction.jl")
include("../src/IceModels.jl")
include("../src/RecoveredModels.jl")
const I=IceModels;const M=RecoveredModels
cfg=TOML.parsefile("config/ice_calibration.toml")
observed,_=readdlm("inputs/hadcrut4.csv",',',Float64;header=true)
mass,_=readdlm("inputs/ice_mass_balance.csv",',',Any;header=true)
forcing,_=readdlm("inputs/ssp_forcing.csv",',',Any;header=true)
climate,_=readdlm("results/climate_joint_projection_parameters.csv",',',Float64;header=true)
climcfg=TOML.parsefile("config/climate_joint_calibration.toml")
n=size(climate,1);rng=MersenneTwister(cfg["seed"]+200)
model(component,t,p;initial=nothing)=component=="glaciers" ?
    I.glaciers(t,p[1],p[2],p[3],isnothing(initial) ? p[4] : initial) :
    I.greenland(t,p[1:4]...;initial=isnothing(initial) ? 0. : initial)
function quantiles(io,prefix,x)
    for j in axes(x,2)
        println(io,join(vcat(prefix(j),quantile(x[:,j],[.05,.5,.95])),","))
    end
end
parameters=Dict();states=Dict();offsets=Dict();histyears=Dict()
open("results/ice_hindcast.csv","w") do io
open("results/ice_holdout.csv","w") do hio
open("results/ice_projection_parameters.csv","w") do pio
    println(io,"component,year,observed_loss_Gt_yr,obs_sd_Gt_yr,q05_Gt_yr,median_Gt_yr,q95_Gt_yr")
    println(hio,"component,year,observed_loss_Gt_yr,predictive_q05_Gt_yr,predictive_median_Gt_yr,predictive_q95_Gt_yr")
    println(pio,"sample,component,posterior_row,climate_posterior_row")
    for component in ("glaciers","greenland")
        stem="results/ice_"*component
        TOML.parsefile(stem*"_mcmc_status.toml")["convergence_criteria_met"] || error("Unconverged ice chain")
        posterior,_=readdlm(stem*"_posterior.csv",',',Float64;header=true)
        indices=randperm(rng,size(posterior,1))[1:n];p=posterior[indices,3:8]
        parameters[component]=p
        years=collect(cfg[component]["initial_year"]:2021);histyears[component]=years
        offset=component=="glaciers" ? mean(observed[1850 .<=observed[:,1].<=1870,2]) : 0.
        offsets[component]=offset
        t=observed[observed[:,1].>=years[1],2].-offset
        state=zeros(n,length(t));rates=zeros(n,length(t)-1)
        records=mass[(mass[:,1].==component).&(mass[:,2].<=cfg["holdout_end"]),:]
        train=findall(y->y<=cfg["fit_end"],records[:,2]);hold=findall(y->y>cfg["fit_end"],records[:,2])
        predicted=zeros(n,length(hold))
        for j in 1:n
            state[j,:]=model(component,t,p[j,:]);rates[j,:]=diff(state[j,:]).*cfg["gt_per_m_sle"]
            sigma=p[j,5];rho=p[j,6];m=0.;v=sigma^2/(1-rho^2)
            for k in train
                residual=-records[k,4]-rates[j,Int(records[k,2])-years[1]+1]
                gain=v/(v+records[k,5]^2)
                m=rho*(m+gain*(residual-m));v=rho^2*(1-gain)*v+sigma^2
            end
            r=m+sqrt(v)*randn(rng)
            for (kk,k) in enumerate(hold)
                kk>1 && (r=rho*r+sigma*randn(rng))
                predicted[j,kk]=rates[j,Int(records[k,2])-years[1]+1]+r+records[k,5]*randn(rng)
            end
            println(pio,join((j,component,indices[j],Int(climate[j,1])),","))
        end
        states[component]=state
        for k in axes(records,1)
            q=quantile(rates[:,Int(records[k,2])-years[1]+1],[.05,.5,.95])
            println(io,join(vcat([component,records[k,2],-records[k,4],records[k,5]],q),","))
        end
        quantiles(hio,j->[component,records[hold[j],2],-records[hold[j],4]],predicted)
    end
end
end
end
thermal,_=readdlm("results/thermal_observation_fit.csv",',',Float64;header=true)
coefficient=thermal[findfirst(==(2000),thermal[:,1]),4]
open("results/ice_scenario_quantiles.csv","w") do io
    println(io,"scenario,component,year,q05_change_m,median_change_m,q95_change_m")
    for scenario in ("ssp119","ssp126","ssp245","ssp370","ssp460","ssp585")
        rows=forcing[forcing[:,1].==scenario,:];years=Int.(rows[:,2])
        future=findall(y->y>=2021,years);tref=findall(y->1961<=y<=1990,years)
        thermal_projection=zeros(n,length(future))
        projections=Dict(c=>zeros(n,length(future)) for c in ("glaciers","greenland"))
        for j in 1:n
            theta=climate[j,2:end]
            s=M.climate_system(ecs=theta[1],diffusivity=theta[2],cells=climcfg["cells"])
            response=M.climate_observables(s,Float64.(rows[:,3])+(theta[3]-1)*Float64.(rows[:,5]))
            # The future uses the same observational datum as the conditional
            # historical fit. Only the first (2021) boundary value is observed.
            t=response.temperature.-mean(response.temperature[tref]).+theta[4]
            for component in ("glaciers","greenland")
                tf=t[future].-offsets[component];tf[1]=observed[end,2]-offsets[component]
                ref=findfirst(==(2010),histyears[component])
                x=model(component,tf,parameters[component][j,:];initial=states[component][j,end])
                projections[component][j,:]=x.-states[component][j,ref]
            end
            h=response.heat[2,:]
            thermal_projection[j,:]=coefficient*1e22.*(h[future].-h[findfirst(==(2010),years)])
        end
        for component in ("glaciers","greenland")
            quantiles(io,j->[scenario,component,years[future[j]]],projections[component])
        end
        quantiles(io,j->[scenario,"thermal_0_2000m",years[future[j]]],thermal_projection)
        println("Conditional ice/thermal alternatives: ",scenario);flush(stdout)
    end
end
