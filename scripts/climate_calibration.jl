using TOML, DelimitedFiles, Statistics, Random
include(joinpath(@__DIR__,"..","src","RecoveredModels.jl"))
include(joinpath(@__DIR__,"..","src","Calibration.jl"))
const M=RecoveredModels
const C=Calibration
const ROOT=normpath(joinpath(@__DIR__,".."))
joint="--joint-heat" in ARGS
had5="--hadcrut5" in ARGS
had5 && !joint && error("HadCRUT5 experiment requires --joint-heat")
stem=had5 ? "climate_hadcrut5" : joint ? "climate_joint" : "climate"
cfg=TOML.parsefile(joinpath(ROOT,"config",stem*"_calibration.toml"))
forcing,header=readdlm(joinpath(ROOT,"inputs","ssp_forcing.csv"),',',Any;header=true)
rows=forcing[forcing[:,1].=="ssp245",:]
years=Int.(rows[:,2]); keep=years.<=cfg["end_year"]
years=years[keep]; total=Float64.(rows[keep,3]); aerosol=Float64.(rows[keep,5])
obs,_=readdlm(joinpath(ROOT,"inputs",had5 ? "hadcrut5_5010.csv" : "hadcrut4.csv"),',',Float64;header=true)
fit=(cfg["fit_start"].<=obs[:,1].<=cfg["fit_end"])
fit_idx=Int.(obs[fit,1]).-years[1].+1
reference=findall(y->1961<=y<=1990,years)
observed=obs[fit,2]; obs_sd=(obs[fit,4]-obs[fit,3])/(2*1.96)
ocean,_=readdlm(joinpath(ROOT,"inputs","noaa_ocean.csv"),',',Float64;header=true)
hobs=ocean[(ocean[:,1].==700).&(1955 .<=ocean[:,2].<2006),:]
heat_idx=Int.(floor.(hobs[:,2])).-years[1].+1
function prediction(theta;cells=cfg["cells"],substeps=cfg["substeps"])
    s=M.climate_system(ecs=theta[1],diffusivity=theta[2],cells=cells)
    q=total+(theta[3]-1)*aerosol
    if get(cfg,"integrator","crank_nicolson")=="exact_modes"
        response=M.climate_observables(s,q;depths=(700.,))
        t=response.temperature
        heat=joint ? response.heat[1,heat_idx].+theta[7] : Float64[]
    else
        x=M.climate_run(s,q;substeps=substeps)
        t=[M.global_temperature(s,x[:,j]) for j in axes(x,2)]
        heat=joint ? [M.ocean_heat_to_depth(s,x[:,i],700.)/1e22+theta[7] for i in heat_idx] : Float64[]
    end
    (temperature=t.-mean(t[reference]).+theta[4],heat=heat)
end
function logdensity(theta)
    all(cfg["lower"].<=theta.<=cfg["upper"]) || return -Inf
    p=prediction(theta)
    value=C.ar1_loglikelihood(observed-p.temperature[fit_idx],theta[5],theta[6],obs_sd)
    joint && (value+=C.ar1_loglikelihood(hobs[:,3]-p.heat,theta[8],theta[9],hobs[:,4]))
    value
end
logistic(z)=z>=0 ? 1/(1+exp(-z)) : exp(z)/(1+exp(z))
function physical(z)
    theta=vcat(exp.(z[1:2]),z[3:end])
    if joint
        theta[[5,8]]=exp.(z[[5,8]])
        theta[[6,9]]=0.999 .* logistic.(z[[6,9]])
    end
    theta
end
function jacobian(z)
    value=z[1]+z[2]
    if joint
        value+=z[5]+z[8]
        for i in (6,9)
            p=logistic(z[i]);value+=log(.999)+log(p)+log1p(-p)
        end
    end
    value
end
transformed(z)=logdensity(physical(z))+jacobian(z) # Prior remains uniform in physical units.
initial=cfg["initial"]
# Warm compile before timing; this is an observed benchmark, not an estimate.
logdensity(initial)
timing=@elapsed for j in 1:10;logdensity(initial);end
println("Likelihood wall seconds per call: ",timing/10);flush(stdout)
if "--benchmark" in ARGS;exit();end
open(joinpath(ROOT,"results",stem*"_posterior.csv"),"w") do io
    println(io,join(vcat(["chain","draw"],cfg["parameter_names"],["logdensity"]),","))
    for chain in 1:cfg["chains"]
        # Dispersed starts; all remain within the explicitly documented prior.
        start=copy(initial);start[1]=[1.8,3.0,4.5,6.0][chain];start[2]=[.3,.8,1.6,2.8][chain]
        if joint
            start[1]=[1.5,2.,2.8,4.][chain];start[2]=[.15,.3,.6,1.2][chain]
            start[7]=clamp(start[7]+mean(hobs[:,3]-prediction(start).heat),-49.,-.01)
        end
        start[1:2]=log.(start[1:2])
        if joint
            start[[5,8]]=log.(start[[5,8]])
            start[[6,9]]=log.(start[[6,9]] ./ (0.999 .- start[[6,9]]))
        end
        result=C.metropolis(transformed,start,cfg["proposal_scales"],
            MersenneTwister(cfg["seed"]+chain);warmup=cfg["warmup"],draws=cfg["draws_per_chain"],
            adapt_window=get(cfg,"adapt_window",cfg["warmup"]),proposal_scale=get(cfg,"proposal_scale",2.38))
        for j in cfg["save_every"]:cfg["save_every"]:size(result.samples,1)
            theta=physical(vec(result.samples[j,:]))
            println(io,join(vcat([chain,j],theta,[result.logdensity[j]-jacobian(vec(result.samples[j,:]))]),","))
        end
        flush(io)
        println("Chain ",chain,": acceptance=",result.acceptance,"; warmup=",result.warmup_acceptance);flush(stdout)
    end
end
println(stem," alternative posterior generated; convergence assessment required.")
