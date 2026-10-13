using DelimitedFiles,Statistics,TOML
include("../src/Reproduction.jl")
include("../src/RecoveredModels.jl")
include("../src/CoastalPaths.jl")
include("../src/GeographicCoasts.jl")
const G=GeographicCoasts;const R=Reproduction
fine="--fine-profiles" in ARGS
binary_pilot="--binary-pilot" in ARGS
fine_all=fine && ("--all" in ARGS || binary_pilot)
fine_data=fine && !fine_all ? readdlm("inputs/sliiders_pilot_fine.csv",',',Any;header=true)[1] : nothing
segments,_=readdlm("inputs/sliiders_segments.csv",',',Any;header=true)
profiles=Dict{String,Matrix{Float64}}()
for label in ("area_km2","population_2019","capital_USD2019PPP","wetland_km2")
    d,_=readdlm("inputs/sliiders_"*label*".csv",',',Any;header=true)
    @assert d[:,1]==segments[:,1]
    profiles[label]=Float64.(d[:,2:end])
end
edges=fine_all ? vec(readdlm(".local/inputs/sliiders_fine_edges.csv",Float64)) : [0.,1.,2.,3.,5.,10.,20.]
if fine_all
    for (label,name) in (("area_km2","landarea"),("population_2019","pop_2019"),("capital_USD2019PPP","K_2019"),("wetland_km2","wetland"))
        bytes=read(".local/inputs/sliiders_"*name*"_fine.f64")
        @assert length(bytes)==8*(length(edges)-1)*size(segments,1)
        refined=Matrix(reshape(reinterpret(Float64,bytes),length(edges)-1,size(segments,1))')
        @assert all(isapprox.(sum(refined,dims=2),sum(profiles[label],dims=2);rtol=1e-8,atol=1e-5))
        profiles[label]=refined
    end
end
economics,_=readdlm("inputs/sliiders_economics.csv",',',Any;header=true)
groups=Dict{Tuple{String,String},Vector{Int}}()
for i in axes(segments,1)
    key=(String(segments[i,10]),String(segments[i,2]))
    push!(get!(groups,key,Int[]),i)
end
years=collect(2010:2100)
const ECONOMIES=Dict{Tuple{String,String},Any}()
function interpolate(y,x)
    [begin
        j=min(searchsortedlast(y,t),length(y)-1)
        x[j]+(t-y[j])/(y[j+1]-y[j])*(x[j+1]-x[j])
     end for t in years]
end
function economy(country,scenario)
    key=(country,scenario)
    haskey(ECONOMIES,key) && return ECONOMIES[key]
    rows=economics[(economics[:,1].==country).&(economics[:,2].==scenario).&(economics[:,3].=="OECD"),:]
    @assert size(rows,1)==10
    rows=rows[sortperm(Int.(rows[:,4])),:];y=Int.(rows[:,4])
    us=economics[(economics[:,1].=="USA").&(economics[:,2].==scenario).&(economics[:,3].=="OECD").&(economics[:,4].==2010),5][1]
    result=(income=interpolate(y,Float64.(rows[:,5])),popscale=interpolate(y,Float64.(rows[:,6])),
     capscale=interpolate(y,Float64.(rows[:,7])),land=interpolate(y,Float64.(rows[:,8])),
     wetland=interpolate(y,Float64.(rows[:,9])),us_income_2010=Float64(us))
    ECONOMIES[key]=result
    result
end
function coast(key)
    rows=groups[key];i=first(rows)
    @assert all(segments[j,6:9]==segments[i,6:9] for j in rows)
    total(label)=vec(sum(profiles[label][rows,:],dims=1))
    original=(edges=edges,areas=total("area_km2"),population=total("population_2019"),
     capital=total("capital_USD2019PPP"),wetland=total("wetland_km2"),
     length=sum(Float64.(segments[rows,5])),pc=Float64(segments[i,8]),mobile=Float64(segments[i,9]),
     gev=(location=Float64(segments[i,6]),scale=Float64(segments[i,7]),shape=0.0))
    if fine && !fine_all
        d=fine_data[(fine_data[:,1].==key[1]).&(fine_data[:,2].==key[2]),:]
        if size(d,1)>0
            fine_edges=vcat(Float64.(d[:,3]),Float64(d[end,4]))
            # Zarr float32 bin bounds carry harmless representational offsets.
            @assert all(isapprox.(Float64.(d[1:end-1,4]),fine_edges[2:end-1];atol=1e-5))
            return merge(original,(edges=fine_edges,areas=Float64.(d[:,5]),population=Float64.(d[:,6]),capital=Float64.(d[:,7]),wetland=Float64.(d[:,8])))
        end
    end
    original
end
valid=Tuple{String,String}[];excluded=Tuple{Tuple{String,String},String}[]
for key in sort(collect(keys(groups)))
    g=coast(key);eco=economy(key[2],"SSP2")
    reason=g.length<=0 ? "no coastline in this country" :
        any(eco.income.<=0)||any(eco.popscale.<=0)||any(eco.capscale.<=0) ? "zero socioeconomic inputs" : ""
    if isempty(reason);push!(valid,key);else;push!(excluded,(key,reason));end
end
open("results/geographic_input_exclusions.csv","w") do io
    println(io,"coast_id,country,reason,area_km2,population2019,capital_USD2019PPP,wetland_km2")
    for (key,reason) in excluded
        g=coast(key)
        println(io,join((key...,reason,sum(g.areas),sum(g.population),sum(g.capital),sum(g.wetland)),","))
    end
end
full="--all" in ARGS
limit=full ? length(valid) : 16
# Deterministic evenly spaced audit sample; never extrapolated to a global total.
indices=full ? collect(eachindex(valid)) : unique(round.(Int,range(1,length(valid);length=limit)))
if !full
    # Stress cases supplement the geographic sample before scaling up.
    scales=[coast(k).gev.scale for k in valid]
    populations=[sum(coast(k).population) for k in valid]
    indices=sort(unique(vcat(indices,argmin(scales),argmax(scales),argmax(populations))))
end
stem=full ? "geographic_global" : "geographic_pilot"
fine && (stem*="_fine")
binary_pilot && (stem*="_binary")
one_case="--ssp4-one-metre" in ARGS
scenarios=one_case ? ("SSP4",) : ("SSP2","SSP4")
endpoints=one_case ? (1.0,) : (.5,1.,2.)
one_case && (stem*="_ssp4_1m")
order=12
if "--quadrature-check" in ARGS;order=24;stem*="_q24";end
quad=G.quadrature(order)
println("Eligible coast-country units: ",length(valid),"; excluded: ",length(excluded),"; running: ",length(indices));flush(stdout)
t0=time()
outputpath=(full ? ".local/" : "results/")*stem*"_costs.csv"
open(outputpath,"w") do io
    println(io,"coast_id,country,scenario,sea2100_m,strategy,return_period,pv_USD2019PPP,no_adaptation_pv_USD2019PPP,baseline_pv_USD2019PPP,baseline_no_adaptation_pv_USD2019PPP,incremental_pv_USD2019PPP,migrants,construction_pv,maintenance_pv,retreat_pv,inundation_pv,wetland_pv,flood_pv")
    for (counter,index) in enumerate(indices)
        key=valid[index];g=coast(key)
        for scenario in scenarios
            eco=economy(key[2],scenario)
            base=G.choose_path(years,zeros(length(years)),eco,g;quad=quad)
            baseline=R.present_value(base.path.total,years)
            for high in endpoints
                sea=high.*((years.-2010)./90).^1.5
                result=G.choose_path(years,sea,eco,g;quad=quad)
                pv=R.present_value(result.path.total,years)
                component=[R.present_value(result.path.costs[:,j],years) for j in 1:6]
                println(io,join(vcat([key...,scenario,high,result.candidate.strategy,result.candidate.return_period,
                    pv,R.present_value(result.paths[1].total,years),baseline,R.present_value(base.paths[1].total,years),pv-baseline,sum(result.path.migrants)],component),","))
            end
        end
        if counter%100==0 || counter==length(indices)
            println("Completed ",counter," units in ",round(time()-t0,digits=2)," wall seconds");flush(stdout);flush(io)
        end
    end
end
open("results/"*stem*"_run.toml","w") do io
    TOML.print(io,Dict("scope"=>"NON-REPRODUCTION: SLIIDERS exposure, prescribed SLR, annual accounting and 2019 USD PPP",
        "eligible_coasts"=>length(valid),"excluded_coasts"=>length(excluded),"simulated_coasts"=>length(indices),
        "gauss_nodes_per_smooth_interval"=>order,"wall_seconds"=>time()-t0,"end_year"=>2100,
        "scenarios"=>[s*" OECD" for s in scenarios],"slr_endpoints_m"=>collect(endpoints),
        "original_elevation_resolution"=>fine))
end
