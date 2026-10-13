using DelimitedFiles,TOML,Random,Statistics
include("../src/Reproduction.jl");include("../src/IceModels.jl")
include("../src/PaleoDAIS.jl");include("../src/SeaLevelCoupling.jl")
include("../src/RecoveredModels.jl");include("../src/ScenarioDesign.jl")
const I=IceModels;const D=PaleoDAIS;const S=SeaLevelCoupling;const M=RecoveredModels
function interpolate(years,values,t)
    years[1]<=t<=years[end] || error("interpolation outside inputs")
    j=min(searchsortedlast(years,t),length(years)-1)
    values[j]+(values[j+1]-values[j])*(t-years[j])/(years[j+1]-years[j])
end
function main()
    pilot="--pilot" in ARGS;tail="--tail-stratified" in ARGS
    had5="--hadcrut5" in ARGS
    had5 && !tail && error("The HadCRUT5 sensitivity uses --tail-stratified")
    suffix=(tail ? "_stratified" : "")*(had5 ? "_hadcrut5" : "")*(pilot ? "_pilot" : "")
    prefix="sea_level"*suffix
    source="coupled_emissions"*suffix
    paths=readdlm(".local/"*source*"_paths.csv",',',Any;skipstart=1)
    climate=readdlm("results/"*source*"_parameters.csv",',',Float64;skipstart=1)
    endpoints=readdlm("results/"*source*"_endpoints.csv",',',Any;skipstart=1)
    n=size(climate,1);seed=20251041;rng=MersenneTwister(seed);started=time()
    posterior=Dict(c=>readdlm("results/ice_"*c*"_posterior.csv",',',Float64;skipstart=1) for c in ("glaciers","greenland"))
    for c in keys(posterior)
        @assert TOML.parsefile("results/ice_"*c*"_mcmc_status.toml")["convergence_criteria_met"]
    end
    selection=Dict(c=>randperm(rng,size(posterior[c],1))[1:n] for c in ("glaciers","greenland"))
    noise=randn(rng,n,129) # uncertain annual LWS rates2021–2150
    observed=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)
    forcing=readdlm("inputs/ssp_forcing.csv",',',Any;skipstart=1)
    history=forcing[(forcing[:,1].=="ssp245").&(forcing[:,2].<=2021),:]
    hy=Int.(history[:,2]);modern=findall(y->1961<=y<=1990,hy)
    paleoforcing=readdlm("inputs/dais_alternative_forcing.csv",',',Float64;skipstart=1)
    fits=Dict(k=>TOML.parsefile("results/dais_conditional"*(k=="fit512" ? "" : "_pilot")*"_best.toml") for k in ("fit512","fit64"))
    initials=Dict()
    for (key,fit) in fits
        p=D.M.dais_parameters(gamma=fit["gamma"],alpha=fit["alpha"])
        z=D.run(paleoforcing,[2009.5];dt=5.,p=p,lambda=fit["lambda_m_yr"],threshold=fit["threshold_degC"])
        initials[key]=z.radius[end]
    end
    coefficient=readdlm("results/thermal_observation_fit.csv",',',Float64;skipstart=1)[2,4]
    grid=vcat(2009.5,collect(2010.:2150.));reference=findfirst(==(2010.),grid)
    variants=["fit512_shallow_iid","fit64_shallow_iid","fit512_deep_iid","fit512_shallow_common","fit512_shallow_iid_lagged"]
    weights=climate[:,13:15]
    summaries=[];refinements=[];parameters=[]
    open(".local/"*prefix*"_paths.csv","w") do raw
    open("results/"*prefix*"_quantiles.csv","w") do qio
        println(raw,"sample,forcing_rule,variant,year,total_m,glaciers_m,greenland_m,antarctica_m,thermal_m,landwater_m,antarctic_shore_m")
        println(qio,"forcing_rule,variant,distribution,year,q05_m,q50_m,q95_m")
        for rule in ("annual_nearest_emissions","fixed_ssp245")
            values=Dict(v=>zeros(n,length(grid)) for v in variants)
            for j in 1:n
                path=paths[(paths[:,1].==j).&(paths[:,2].==rule),:]
                y=Float64.(path[:,3]);t=Float64.(path[:,7]);t[1]=observed[end,2]
                components=Dict()
                for c in ("glaciers","greenland")
                    p=posterior[c][selection[c][j],3:8]
                    start=c=="glaciers" ? 1990 : 1961
                    offset=c=="glaciers" ? mean(observed[1850 .<=observed[:,1].<=1870,2]) : 0.
                    ht=observed[observed[:,1].>=start,2].-offset
                    h=c=="glaciers" ? I.glaciers(ht,p[1:4]...) : I.greenland(ht,p[1:4]...)
                    f=c=="glaciers" ? I.glaciers(t.-offset,p[1:3]...,h[end]) : I.greenland(t.-offset,p[1:4]...;initial=h[end])
                    all=vcat(h,f[2:end]);yy=collect(Float64(start):2150.)
                    components[c]=[interpolate(yy,all,q) for q in grid]
                    components[c].-=components[c][1]
                end
                par=climate[j,4:12]
                sys=M.climate_system(ecs=par[1],diffusivity=par[2],cells=80)
                hist=M.climate_observables(sys,Float64.(history[:,3])+(par[3]-1)*Float64.(history[:,5]))
                heat=Dict()
                for (name,k,col) in (("shallow",2,8),("deep",3,9))
                    h=hist.heat[k,:].-hist.heat[k,2010-1749]
                    yy=vcat(Float64.(hy),y[2:end]);hh=vcat(h,Float64.(path[2:end,col]))
                    heat[name]=coefficient*1e22.*[interpolate(yy,hh,q) for q in grid]
                    heat[name].-=heat[name][1]
                end
                # Observed annual forcing to2021, then datum-consistent future.
                tg=[q<=2021 ? interpolate(observed[:,1],observed[:,2],q) : interpolate(y,t,q) for q in grid]
                air=-18 .+1.2tg;air[1]=paleoforcing[end,2]
                ocean=D.ocean_temperature.(air)
                lw=Dict()
                for (name,mode) in (("iid",:independent),("common",:common))
                    rates=S.landwater(noise[j,:];mode=mode)
                    lw[name]=[q<=2021 ? .0003*(q-2009.5) : .0003*(2021-2009.5)+interpolate(y,rates,q) for q in grid]
                end
                for variant in variants
                    fitkey=startswith(variant,"fit64") ? "fit64" : "fit512";fit=fits[fitkey]
                    thermal=heat[occursin("deep",variant) ? "deep" : "shallow"]
                    storage=lw[occursin("common",variant) ? "common" : "iid"]
                    other=components["glaciers"]+components["greenland"]+thermal+storage
                    p=D.M.dais_parameters(gamma=fit["gamma"],alpha=fit["alpha"])
                    mode=endswith(variant,"lagged") ? :lagged : :continuous
                    function ais_run(dt)
                        S.antarctic_path(grid,air,ocean,other;initial_radius=initials[fitkey],initial_sea=paleoforcing[end,3],
                            p=p,lambda=fit["lambda_m_yr"],threshold=fit["threshold_degC"],dt=dt,mode=mode)
                    end
                    ais=ais_run(.25);total=other+ais.antarctic;total.-=total[reference]
                    values[variant][j,:]=total
                    if pilot
                        fine=ais_run(.125)
                        push!(refinements,(j,rule,variant,maximum(abs.(fine.antarctic-ais.antarctic))))
                    end
                    k2100=findfirst(==(2100.),grid);k2150=length(grid)
                    endpoint=endpoints[(endpoints[:,1].==j).&(endpoints[:,2].==rule),:]
                    temp=Float64(endpoint[1,6]);category=searchsortedfirst([1.5,2.5,3.5],temp)
                    triggered=any(air[k]>fit["threshold_degC"] && ais.volume[k]>=18. for k in 1:k2100)
                    push!(summaries,(j,rule,variant,temp,category,total[k2100],total[k2150],
                        (ais.antarctic[k2100]-ais.antarctic[reference]),thermal[k2100]-thermal[reference],weights[j,:]...,triggered))
                    for k in 2:length(grid)
                        fields=[components["glaciers"],components["greenland"],ais.antarctic,thermal,storage]
                        changes=[c[k]-c[reference] for c in fields]
                        @assert abs(sum(changes)-total[k])<1e-10
                        println(raw,join((j,rule,variant,grid[k],total[k],changes...,ais.shore[k]),","))
                    end
                end
                if rule=="annual_nearest_emissions"
                    push!(parameters,(j,selection["glaciers"][j],selection["greenland"][j],noise[j,1]))
                end
                if j%32==0;println(rule," sea-level ",j,"/",n," elapsed ",round(time()-started,digits=1));flush(stdout);end
            end
            for variant in variants,(d,distribution) in enumerate(("documented_prior","alternative_budget50","alternative_budget75")),k in 2:length(grid)
                q=[ScenarioDesign.weighted_quantile(values[variant][:,k],weights[:,d],p) for p in (.05,.5,.95)]
                println(qio,join((rule,variant,distribution,grid[k],q...),","))
            end
        end
    end
    end
    function save(suffix,header,rows)
        open("results/"*prefix*suffix,"w") do io
            println(io,header);for row in rows;println(io,join(row,","));end
        end
    end
    save("_endpoints.csv","sample,forcing_rule,variant,warming2100_K,warming_bin,total2100_m,total2150_m,antarctic2100_m,thermal2100_m,weight_prior,weight_budget50,weight_budget75,AIS_fast_trigger_by2100",summaries)
    save("_parameters.csv","sample,glacier_posterior_row,greenland_posterior_row,common_LWS_standard_normal",parameters)
    if pilot;save("_refinement.csv","sample,forcing_rule,variant,max_antarctic_step_difference_m",refinements);end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("members"=>n,"seed"=>seed,"wall_seconds"=>time()-started,"variants"=>variants,
            "scope"=>"NON-REPRODUCTION: alternative uncorrected component budget; independent conditional fits; source-specified Antarctic shore factors",
            "limitations"=>"No target joint posterior; peripheral-glacier overlap retained; empirical upper-ocean coefficient; alternative transient ocean polynomial and2009.5splice",
            "reference_year"=>2010,"Antarctic_shore_fingerprint"=>-1.,"raw_paths"=>".local/"*prefix*"_paths.csv"))
    end
end
main()
