using DelimitedFiles,Random,Statistics,TOML
include("../src/Reproduction.jl");include("../src/RecoveredModels.jl");include("../src/ScenarioDesign.jl")
const R=Reproduction;const M=RecoveredModels;const S=ScenarioDesign
function main()
    seed=20251039;rng=MersenneTwister(seed);n=10000
    data=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
    last=data[findfirst(==(2022),data[:,1]),:]
    q0=(last[2]+last[3]-last[4])*3.664 # net fossil+land-use-minus-cement GtCO2/yr
    years=collect(2022:2150);paths=zeros(n,length(years));parameters=zeros(n,3)
    budget=zeros(n,3);trap=zeros(n);peaks=zeros(Int,n,3)
    for i in 1:n
        growth=M.truncated_normal(rng,.004,.0075,.001,Inf)
        peak=M.truncated_normal(rng,2070.,25.,2030.,2200.)
        decline=M.truncated_normal(rng,.07,.05,.001,.2)
        parameters[i,:]=[growth,peak,decline]
        peaks[i,:]=[floor(Int,peak),round(Int,peak),ceil(Int,peak)]
        for j in 1:3
            _,q=R.emissions(2022,2150,q0,growth,peaks[i,j],decline)
            @assert all(q.>=0)
            budget[i,j]=sum(q[1:79]) # annual means, 2022 through2100 inclusive
            if j==2
                paths[i,:]=q;trap[i]=budget[i,j]-(q[1]+q[79])/2
            end
        end
    end
    within=budget[:,2].<=1223.
    weights=hcat(fill(1/n,n),S.budget_weights(within,.5),S.budget_weights(within,.75))
    open("results/emissions_alternative_samples.csv","w") do io
        println(io,"sample,growth,continuous_peak_year,decline,rounded_peak_year,cumulative2022_2100_GtCO2,budget_floor_GtCO2,budget_ceil_GtCO2,trapezoid_budget_GtCO2,weight_prior,weight_budget50,weight_budget75")
        for i in 1:n
            println(io,join((i,parameters[i,:]...,peaks[i,2],budget[i,2],budget[i,1],budget[i,3],trap[i],weights[i,:]...),","))
        end
    end
    names=["documented_prior","alternative_budget50","alternative_budget75"]
    open("results/emissions_alternative_quantiles.csv","w") do io
        println(io,"distribution,year,q05_GtCO2_yr,q50_GtCO2_yr,q95_GtCO2_yr")
        for j in 1:3,k in eachindex(years)
            quantiles=[S.weighted_quantile(paths[:,k],weights[:,j],p) for p in (.05,.5,.95)]
            println(io,join((names[j],years[k],quantiles...),","))
        end
    end
    audit=Dict("scope"=>"Documented priors plus explicit entropy-constrained alternatives; not the target emissions posterior",
        "seed"=>seed,"samples"=>n,"initial_year"=>2022,"initial_emissions_GtCO2_yr"=>q0,
        "budget_period"=>"Sum annual means2022–2100 inclusive; trapezoid alternative retained",
        "prior_budget_probability"=>mean(within),"prior_peaks_after2150"=>count(peaks[:,2].>2150),
        "floor_round_budget_class_changes"=>count((budget[:,1].<=1223).!=within),
        "ceil_round_budget_class_changes"=>count((budget[:,3].<=1223).!=within),
        "trapezoid_budget_class_changes"=>count((trap.<=1223).!=within),
        "effective_weighted_sample_sizes"=>[1/sum(abs2,weights[:,j]) for j in 1:3],
        "budget_probabilities"=>[sum(weights[within,j]) for j in 1:3],
        "missing"=>"The complete target expert PDF remains unspecified. This entropy-weighting experiment does not impose the SSP4-6.0 conditional mode; the separate inversion sensitivity uses the recovered likelihood and mode with assumed PDF families. No negative emissions in recurrence.")
    open("results/emissions_design_audit.toml","w") do io;TOML.print(io,audit);end
    println(audit)
end
main()
