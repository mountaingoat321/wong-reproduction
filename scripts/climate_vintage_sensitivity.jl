using DelimitedFiles,Statistics,Random,TOML
include("../src/RecoveredModels.jl");include("../src/Calibration.jl")
const M=RecoveredModels;const C=Calibration
function main()
    pilot="--pilot" in ARGS;prefix="climate_vintage"*(pilot ? "_pilot" : "")
    started=time();posterior=readdlm("results/climate_joint_posterior.csv",',',Float64;skipstart=1)
    old=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)
    new=readdlm("inputs/hadcrut5_5010.csv",',',Float64;skipstart=1)
    @assert old[:,1]==new[:,1] && all(new[:,3].<=new[:,2].<=new[:,4])
    forcing=readdlm("inputs/ssp_forcing.csv",',',Any;skipstart=1)
    f=forcing[(forcing[:,1].=="ssp245").&(forcing[:,2].<=2100),:];years=Int.(f[:,2])
    reference=findall(y->1961<=y<=1990,years);preindustrial=findall(y->1850<=y<=1900,years)
    fit=findall(y->y<=2005,old[:,1]);hold=findall(y->2006<=y<=2021,old[:,1])
    index=Int.(old[:,1]).-1749
    seed=20251044;rng=MersenneTwister(seed)
    proposal=sort(randperm(rng,size(posterior,1))[1:(pilot ? 32 : 1000)])
    coupled=Int.(readdlm("results/coupled_emissions_stratified_parameters.csv",',',Float64;skipstart=1)[:,3])
    selected=pilot ? proposal : sort(unique(vcat(proposal,coupled)))
    all_predictions=zeros(length(selected),length(old[:,1]));rows=[]
    for (j,row) in enumerate(selected)
        p=posterior[row,3:11]
        sys=M.climate_system(ecs=p[1],diffusivity=p[2],cells=80)
        out=M.climate_observables(sys,Float64.(f[:,3])+(p[3]-1)*Float64.(f[:,5]);depths=(3000.,))
        prediction=out.temperature[index].-mean(out.temperature[reference]).+p[4]
        all_predictions[j,:]=prediction
        likelihood(obs)=C.ar1_loglikelihood(obs[fit,2]-prediction[fit],p[5],p[6],(obs[fit,4]-obs[fit,3])/(2*1.96))
        oldll=likelihood(old);newll=likelihood(new)
        heat_change=mean(out.heat[1,1987-1749:1996-1749])-mean(out.heat[1,1957-1749:1966-1749])
        future=mean(out.temperature[2081-1749:2100-1749])-mean(out.temperature[preindustrial])
        push!(rows,(row,Int(posterior[row,1]),row in proposal,p[1],oldll,newll,newll-oldll,
            sqrt(mean(abs2,prediction[hold]-old[hold,2])),sqrt(mean(abs2,prediction[hold]-new[hold,2])),heat_change,future))
    end
    open("results/"*prefix*"_weights.csv","w") do io
        println(io,"posterior_row,chain,in_uniform_proposal,ecs_K,loglikelihood_HadCRUT4,loglikelihood_HadCRUT5,log_weight_ratio,holdout_RMSE_HadCRUT4_K,holdout_RMSE_HadCRUT5_K,heat3000_decadal_change_1e22J,ssp245_2081_2100_K")
        for row in rows;println(io,join(row,","));end
    end
    open(".local/"*prefix*"_hindcasts.csv","w") do io
        println(io,"posterior_row,year,temperature_K")
        for (j,row) in enumerate(selected)
            row in proposal || continue
            for k in eachindex(old[:,1])
                println(io,join((row,Int(old[k,1]),all_predictions[j,k]),","))
            end
        end
    end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("uniform_proposal_members"=>length(proposal),"evaluated_rows"=>length(selected),"seed"=>seed,
            "wall_seconds"=>time()-started,"scope"=>"NON-REPRODUCTION: isolated temperature-observation likelihood substitution;700mheat calibration and all physical parameters retained; importance diagnostics required",
            "heat3000_comparison"=>"Independent GK07 written1957–66 to1987–96 change12.8e22J, uncertainty at least8e22J; not a full annual dataset or a newly fitted likelihood"))
    end
end
main()
