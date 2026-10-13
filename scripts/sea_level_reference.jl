# Recover the alternative model's own 1995–2014 datum, without tuning.
# The forward experiment remains unchanged. Hindcast components and the saved
# 2010–2014 segment supply twenty annual values for an arithmetic reference.
using DelimitedFiles,TOML,Statistics
include("../src/Reproduction.jl");include("../src/IceModels.jl")
include("../src/PaleoDAIS.jl");include("../src/SeaLevelCoupling.jl")
include("../src/RecoveredModels.jl")
const D=PaleoDAIS;const M=RecoveredModels
function main()
    had5="--hadcrut5" in ARGS;onlytemp="--temperature-only" in ARGS
    @assert !(had5 && onlytemp)
    suffix=had5 ? "_hadcrut5" : onlytemp ? "_temperature_only" : ""
    climate=readdlm("results/coupled_emissions_stratified"*suffix*"_parameters.csv",',',Float64;skipstart=1)
    selected=readdlm("results/sea_level_stratified"*suffix*"_parameters.csv",',',Float64;skipstart=1)
    obs=readdlm("inputs/hadcrut4.csv",',',Float64;skipstart=1)
    forcing=readdlm("inputs/ssp_forcing.csv",',',Any;skipstart=1)
    history=forcing[(forcing[:,1].=="ssp245").&(forcing[:,2].<=2021),:]
    paleo=readdlm("inputs/dais_alternative_forcing.csv",',',Float64;skipstart=1)
    posterior=Dict(c=>readdlm("results/ice_"*c*"_posterior.csv",',',Float64;skipstart=1) for c in ("glaciers","greenland"))
    fits=Dict(k=>TOML.parsefile("results/dais_conditional"*(k=="fit512" ? "" : "_pilot")*"_best.toml") for k in ("fit512","fit64"))
    ais=Dict()
    for (key,f) in fits
        p=M.dais_parameters(gamma=f["gamma"],alpha=f["alpha"])
        ais[key]=D.run(paleo,vcat(collect(1995.:2009.),2009.5);dt=5.,p=p,lambda=f["lambda_m_yr"],threshold=f["threshold_degC"])
    end
    future=Dict{Tuple{Int,String},Vector{Float64}}()
    open(".local/sea_level_stratified"*suffix*"_paths.csv") do io
        readline(io)
        for line in eachline(io)
            r=split(line,',');r[2]=="annual_nearest_emissions" || continue
            2010<=parse(Float64,r[4])<=2014 || continue
            key=(parse(Int,r[1]),String(r[3]))
            push!(get!(future,key,Float64[]),parse(Float64,r[5]))
        end
    end
    coefficient=readdlm("results/thermal_observation_fit.csv",',',Float64;skipstart=1)[2,4]
    variants=TOML.parsefile("results/sea_level_stratified"*suffix*"_run.toml")["variants"]
    open("results/sea_level_reference"*suffix*"_offsets.csv","w") do io
        println(io,"sample,variant,mean1995_2014_relative2010_m,datum_shift_m,mean_after_rebasing_m")
        for j in axes(climate,1)
            ice=Dict()
            for (c,col) in (("glaciers",2),("greenland",3))
                p=posterior[c][Int(selected[j,col]),3:8];start=c=="glaciers" ? 1990 : 1961
                offset=c=="glaciers" ? mean(obs[1850 .<=obs[:,1].<=1870,2]) : 0.
                t=obs[obs[:,1].>=start,2].-offset
                h=c=="glaciers" ? IceModels.glaciers(t,p[1:4]...) : IceModels.greenland(t,p[1:4]...)
                ice[c]=h[1995-start+1:2010-start+1].-h[2010-start+1]
            end
            par=climate[j,4:6]
            sys=M.climate_system(ecs=par[1],diffusivity=par[2],cells=80)
            hist=M.climate_observables(sys,Float64.(history[:,3])+(par[3]-1)*Float64.(history[:,5]))
            for variant in variants
                fitkey=startswith(variant,"fit64") ? "fit64" : "fit512";f=fits[fitkey];a=ais[fitkey]
                depth=occursin("deep",variant) ? 3 : 2
                thermal=coefficient*1e22.*(hist.heat[depth,1995-1749:2010-1749].-hist.heat[depth,2010-1749])
                other=ice["glaciers"]+ice["greenland"]+thermal+.0003 .*collect(-15.:0.)
                # Linear interpolation at 2009.5 is the forward run's splice.
                first_half_year=-(other[end-1]+other[end])/2
                air=[paleo[end,2],-18+1.2obs[2010-1849,2]]
                p=M.dais_parameters(gamma=f["gamma"],alpha=f["alpha"])
                b=SeaLevelCoupling.antarctic_path([2009.5,2010.],air,D.ocean_temperature.(air),[0.,first_half_year];
                    initial_radius=a.radius[end],initial_sea=paleo[end,3],p=p,
                    lambda=f["lambda_m_yr"],threshold=f["threshold_degC"],dt=.25,
                    mode=endswith(variant,"lagged") ? :lagged : :continuous)
                past_ais=(a.volume[end].-a.volume[1:15]).*D.SLE_PER_VOLUME.-b.antarctic[end]
                values=vcat(other[1:15]+past_ais,future[(j,variant)])
                @assert length(values)==20 && future[(j,variant)][1]==0.
                datum=mean(values);check=mean(values.-datum)
                @assert abs(check)<1e-12
                println(io,join((j,variant,datum,-datum,check),","))
            end
        end
    end
end
main()
