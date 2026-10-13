# Consistency of the independently assembled historical budget, not a holdout.
# Church–White also enters the Antarctic boundary forcing. No rejection weights
# or target posterior are inferred from this comparison.
using DelimitedFiles,Statistics,TOML
include("../src/Reproduction.jl");include("../src/IceModels.jl")
include("../src/PaleoDAIS.jl");include("../src/RecoveredModels.jl")
include("../src/ScenarioDesign.jl")
const D=PaleoDAIS;const M=RecoveredModels;const I=IceModels
function main()
    started=time();pilot="--pilot" in ARGS
    prefix="sea_level_hindcast"*(pilot ? "_pilot" : "")
    years=collect(1990.5:2009.5);reference=findall(1995.5 .<=years.<=2004.5)
    center(v)=v.-mean(v[reference])
    slope(v)=sum((years.-mean(years)).*v)/sum(abs2,years.-mean(years))
    midpoint(v,start)=[(v[floor(Int,y)-start+1]+v[floor(Int,y)-start+2])/2 for y in years]
    observed=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)
    cw=readdlm("inputs/church_white2011.csv",',',Float64;skipstart=1)
    obs=center(cw[1990.5 .<=cw[:,1].<=2009.5,2])
    forcing=readdlm("inputs/ssp_forcing.csv",',',Any;skipstart=1)
    history=forcing[(forcing[:,1].=="ssp245").&(forcing[:,2].<=2021),:]
    paleo=readdlm("inputs/dais_alternative_forcing.csv",',',Float64;skipstart=1)
    fit=TOML.parsefile("results/dais_conditional_best.toml")
    p=M.dais_parameters(gamma=fit["gamma"],alpha=fit["alpha"])
    ais(dt)=D.run(paleo,years;dt=dt,p=p,lambda=fit["lambda_m_yr"],threshold=fit["threshold_degC"])
    av=ais(5.);antarctic=center(-av.volume.*D.SLE_PER_VOLUME)
    adiff=maximum(abs.(antarctic-center(-ais(10.).volume.*D.SLE_PER_VOLUME)))
    @assert adiff<1e-5
    posterior=Dict(c=>readdlm("results/ice_"*c*"_posterior.csv",',',Float64;skipstart=1) for c in ("glaciers","greenland"))
    coefficient=readdlm("results/thermal_observation_fit.csv",',',Float64;skipstart=1)[2,4]
    summary=[];series=[];checks=[]
    for (name,suffix) in (("Had4_heat",""),("Had5_heat","_hadcrut5"),("Had4_noheat","_temperature_only"))
        climate=readdlm("results/coupled_emissions_stratified"*suffix*"_parameters.csv",',',Float64;skipstart=1)
        selected=readdlm("results/sea_level_stratified"*suffix*"_parameters.csv",',',Float64;skipstart=1)
        ids=pilot ? [1,125,250] : collect(1:250)
        weights=climate[ids,end-2];weights/=sum(weights)
        totals=Dict(depth=>zeros(length(ids),length(years)) for depth in (2000,4057))
        for (row,j) in enumerate(ids)
            ice=Dict()
            for (c,col) in (("glaciers",2),("greenland",3))
                q=posterior[c][Int(selected[j,col]),3:6];start=c=="glaciers" ? 1990 : 1961
                offset=c=="glaciers" ? mean(observed[1850 .<=observed[:,1].<=1870,2]) : 0.
                t=observed[observed[:,1].>=start,2].-offset
                h=c=="glaciers" ? I.glaciers(t,q...) : I.greenland(t,q...)
                ice[c]=center(midpoint(h,start))
            end
            q=climate[j,4:6];f=Float64.(history[:,3])+(q[3]-1)*Float64.(history[:,5])
            hist=M.climate_observables(M.climate_system(ecs=q[1],diffusivity=q[2],cells=80),f)
            fine=pilot ? M.climate_observables(M.climate_system(ecs=q[1],diffusivity=q[2],cells=160),f) : nothing
            for (depth,k) in ((2000,2),(4057,3))
                thermal=center(coefficient*1e22.*midpoint(hist.heat[k,:],1750))
                storage=center(.0003 .* years)
                total=ice["glaciers"]+ice["greenland"]+antarctic+thermal+storage
                @assert abs(mean(total[reference]))<1e-12
                totals[depth][row,:]=1000total
                if pilot
                    ft=center(coefficient*1e22.*midpoint(fine.heat[k,:],1750))
                    diff=maximum(abs.(ft-thermal));@assert diff<.001
                    push!(checks,(name,j,depth,diff,adiff))
                end
            end
        end
        for depth in (2000,4057)
            v=totals[depth]
            quantile(x,q)=ScenarioDesign.weighted_quantile(x,weights,q)
            median=[quantile(v[:,k],.5) for k in eachindex(years)]
            rates=[slope(v[j,:]) for j in axes(v,1)]
            push!(summary,(name,depth,length(ids),slope(obs),quantile(rates,.05),quantile(rates,.5),quantile(rates,.95),
                           sqrt(mean(abs2,median-obs)),mean(median-obs)))
            for k in eachindex(years)
                push!(series,(name,depth,years[k],obs[k],quantile(v[:,k],.05),median[k],quantile(v[:,k],.95)))
            end
        end
    end
    function save(suffix,header,rows)
        open("results/"*prefix*suffix,"w") do io
            println(io,header);for r in rows;println(io,join(r,","));end
        end
    end
    save("_summary.csv","climate,heat_depth_m,members,observed_trend_mm_yr,model_trend_q05_mm_yr,model_trend_median_mm_yr,model_trend_q95_mm_yr,median_RMSE_mm,median_bias_mm",summary)
    save("_quantiles.csv","climate,heat_depth_m,year,observed_mm,model_q05_mm,model_median_mm,model_q95_mm",series)
    pilot && save("_refinement.csv","climate,sample,heat_depth_m,heat_80_160_cell_difference_m,AIS_dt10_dt5_difference_m",checks)
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("wall_seconds"=>time()-started,"completed"=>true,"pilot"=>pilot,
            "AIS_refinement_m"=>adiff,"reference"=>"1995.5–2004.5 arithmetic mean, model and observations separately",
            "heat_depth_note"=>"4057 label means4057.5m including57.5m mixed layer",
            "weights"=>"Saved prior emissions-stratum weights; no new calibration or rejection weighting",
            "scope"=>"NON-REPRODUCTION: conditional historical budget consistency,1990.5–2009.5",
            "dependence"=>"ChurchWhite enters AIS boundary forcing; known observed Had4 forces ice; fixed AIS point fit; independent component marginals; heat coefficients estimated through2015; no independent holdout",
            "assumptions"=>"Midpoint linear interpolation; constant historical LWS .3mm/yr; peripheral-ice overlap retained; no stochastic residual trajectories or missing joint covariance invented"))
    end
    println(prefix," complete in ",time()-started," seconds")
end
main()
