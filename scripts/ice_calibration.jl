using TOML,DelimitedFiles,Random,Statistics
include("../src/Reproduction.jl")
include("../src/IceModels.jl")
include("../src/Calibration.jl")
const I=IceModels;const C=Calibration
cfg=TOML.parsefile("config/ice_calibration.toml")
temperature,_=readdlm("inputs/hadcrut4.csv",',',Float64;header=true)
obs,_=readdlm("inputs/ice_mass_balance.csv",',',Any;header=true)
logistic(z)=z>=0 ? 1/(1+exp(-z)) : exp(z)/(1+exp(z))
function run_component(component)
    params=cfg[component]
    years=collect(params["initial_year"]:2021)
    t=temperature[Int.(temperature[:,1]).>=years[1],2]
    if component=="glaciers";t=t.-mean(temperature[1850 .<=temperature[:,1].<=1870,2]);end
    records=obs[(obs[:,1].==component).&(obs[:,2].<=cfg["holdout_end"]),:]
    fit=Float64.(records[:,2]).<=cfg["fit_end"]
    index=Int.(records[:,2]).-years[1].+1
    measured=-Float64.(records[:,4]);sd=Float64.(records[:,5])
    function predict(theta)
        state=component=="glaciers" ? I.glaciers(t,theta[1:4]...) : I.greenland(t,theta[1:4]...)
        (rates=diff(state).*cfg["gt_per_m_sle"],state=state)
    end
    function density(theta)
        all(params["lower"].<=theta.<=params["upper"]) || return -Inf
        prior=1.0
        if component=="greenland"
            theta[4]+theta[3]*minimum(t)>=0 || return -Inf
            prior=I.greenland_difference_prior(theta[1]);prior>0 || return -Inf
        end
        predicted=predict(theta).rates[index[fit]]
        log(prior)+C.ar1_loglikelihood(measured[fit]-predicted,theta[5],theta[6],sd[fit])
    end
    function physical(z)
        p=copy(z)
        component=="glaciers" && (p[1]=exp(z[1]))
        p[5]=exp(z[5]);p[6]=.999*logistic(z[6]);p
    end
    function jacobian(z)
        r=logistic(z[6])
        (component=="glaciers" ? z[1] : 0.)+z[5]+log(.999)+log(r)+log1p(-r)
    end
    transformed(z)=density(physical(z))+jacobian(z)
    open("results/ice_"*component*"_posterior.csv","w") do io
        println(io,join(vcat(["chain","draw"],params["parameter_names"],["logdensity"]),","))
        for chain in 1:cfg["chains"]
            start=copy(params["initial"])
            if component=="glaciers"
                start[1]=[.0007,.001,.002,.004][chain]
                start[2]=[.32,.38,.44,.48][chain];start[3]=[.6,.7,.85,.95][chain]
                start[1]=log(start[1])
            else
                start[1]=[-.3,0.,.3,.6][chain];start[2]=[1.,2.,2.8,3.5][chain]
            end
            start[5]=log(start[5]);start[6]=log(start[6]/(.999-start[6]))
            result=C.metropolis(transformed,start,params["proposal_scales"],
                MersenneTwister(cfg["seed"]+chain+(component=="greenland" ? 100 : 0));
                warmup=cfg["warmup"],draws=cfg["draws_per_chain"],adapt_window=cfg["adapt_window"],proposal_scale=cfg["proposal_scale"])
            for j in cfg["save_every"]:cfg["save_every"]:size(result.samples,1)
                z=vec(result.samples[j,:]);theta=physical(z)
                println(io,join(vcat([chain,j],theta,[result.logdensity[j]-jacobian(z)]),","))
            end
            flush(io);println(component," chain ",chain,": acceptance ",result.acceptance);flush(stdout)
        end
    end
end
for component in ("glaciers","greenland");run_component(component);end
