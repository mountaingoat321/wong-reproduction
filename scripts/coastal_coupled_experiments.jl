using DelimitedFiles,Statistics,TOML
include("../src/Reproduction.jl");include("../src/RecoveredModels.jl")
include("../src/CoastalPaths.jl");include("../src/GeographicCoasts.jl")
const G=GeographicCoasts;const R=Reproduction
function main()
    pilot="--pilot" in ARGS
    scenario="--ssp2" in ARGS ? "SSP2" : "SSP4"
    perregion=pilot ? 4 : (scenario=="SSP2" ? 8 : 16)
    extension="--horizon-freeze" in ARGS ? "freeze" : "--horizon-growth" in ARGS ? "growth" : "none"
    geometric="--geometric-economy" in ARGS
    accounting="--accounting" in ARGS
    accounting && !pilot && error("Accounting diagnostic currently uses --pilot")
    prefix="coastal_coupled"*(scenario=="SSP2" ? "_ssp2" : "")*(extension!="none" ? "_2150_"*extension : "")*(geometric ? "_geometric" : "")*(accounting ? "_accounting" : "")*(pilot ? "_pilot" : "")
    started=time();years=collect(2010:(extension=="none" ? 2100 : 2150))
    design=readdlm("results/coastal_sampling_design.csv",',',Any;skipstart=1)
    design=design[design[:,2].<=perregion,:]
    keys=sort(unique([(String(r[3]),String(r[4])) for r in eachrow(design)]))
    segments=readdlm("inputs/sliiders_segments.csv",',',Any;skipstart=1)
    economics=readdlm("inputs/sliiders_economics.csv",',',Any;skipstart=1)
    comparisons=readdlm("results/geographic_full_resolution_comparison.csv",',',Any;skipstart=1)
    base=Dict((String(r[1]),String(r[2]))=>Float64(r[6]-r[8]) for r in eachrow(comparisons))
    # comparison columns: id,country,policies,coarse/fine total,coarse/fine increment.
    edges=vec(readdlm(".local/inputs/sliiders_fine_edges.csv",Float64))
    profiles=Dict{String,Matrix{Float64}}()
    for name in ("landarea","pop_2019","K_2019","wetland")
        bytes=read(".local/inputs/sliiders_"*name*"_fine.f64")
        @assert length(bytes)==8*(length(edges)-1)*size(segments,1)
        profiles[name]=Matrix(reshape(reinterpret(Float64,bytes),length(edges)-1,size(segments,1))')
    end
    coasts=Dict()
    for key in keys
        rows=findall(i->segments[i,10]==key[1] && segments[i,2]==key[2],axes(segments,1));i=first(rows)
        total(name)=vec(sum(profiles[name][rows,:],dims=1))
        coasts[key]=(edges=edges,areas=total("landarea"),population=total("pop_2019"),capital=total("K_2019"),
            wetland=total("wetland"),length=sum(Float64.(segments[rows,5])),pc=Float64(segments[i,8]),
            mobile=Float64(segments[i,9]),gev=(location=Float64(segments[i,6]),scale=Float64(segments[i,7]),shape=0.))
    end
    function economy(country)
        rows=economics[(economics[:,1].==country).&(economics[:,2].==scenario).&(economics[:,3].=="OECD"),:]
        rows=rows[sortperm(Int.(rows[:,4])),:];y=Int.(rows[:,4]);@assert length(y)==10
        function interp(col)
            [begin
                k=min(searchsortedlast(y,t),length(y)-1);a=Float64(rows[k,col]);b=Float64(rows[k+1,col]);u=(t-y[k])/(y[k+1]-y[k])
                if t>2100 && extension=="freeze"
                    b
                elseif geometric || t>2100
                    a==b==0. ? 0. : min(a,b)>0 ? a*(b/a)^u : error("nonpositive geometric input")
                else
                    a+u*(b-a)
                end
            end for t in years]
        end
        us=economics[(economics[:,1].=="USA").&(economics[:,2].==scenario).&(economics[:,3].=="OECD").&(economics[:,4].==2010),5][1]
        (income=interp(5),popscale=interp(6),capscale=interp(7),land=interp(8),wetland=interp(9),us_income_2010=Float64(us))
    end
    economies=Dict(c=>economy(c) for c in unique(last.(keys)))
    endpoints=readdlm("results/sea_level_stratified_endpoints.csv",',',Any;skipstart=1)
    endpoints=endpoints[(endpoints[:,2].=="annual_nearest_emissions").&(endpoints[:,3].=="fit512_shallow_iid"),:]
    members=Int.(endpoints[:,1])
    economic="--economic-priors" in ARGS
    if pilot || economic
        # Audit extremes and every occupied temperature category; no extrapolated
        # probability distribution is reported from this purposive pilot.
        members=sort(unique(vcat([Int(endpoints[argmin(endpoints[:,6]),1]),Int(endpoints[argmax(endpoints[:,6]),1])],
            [Int(endpoints[findfirst(==(b),endpoints[:,5]),1]) for b in unique(endpoints[:,5])])))
    end
    sealevel=Dict(i=>Float64[] for i in members)
    open(".local/sea_level_stratified_paths.csv") do io
        readline(io)
        for line in eachline(io)
            r=split(line,',');r[2]=="annual_nearest_emissions" && r[3]=="fit512_shallow_iid" || continue
            member=parse(Int,r[1]);haskey(sealevel,member) || continue
            2010<=parse(Float64,r[4])<=years[end] || continue
            push!(sealevel[member],parse(Float64,r[5]))
        end
    end
    @assert all(length(s)==length(years) && s[1]==0. && all(diff(s).>=0) for s in values(sealevel))
    if economic
        @assert scenario=="SSP4" && extension=="none" && !geometric && !accounting
        include("coastal_economic_sensitivity.jl")
        # World-age safe invocation of the independently defined experiment.
        Base.invokelatest(economic_sensitivity,years,coasts,economies,sealevel,design,members;pilot=pilot)
        return
    end
    quad=G.quadrature(12);checks=[]
    noadapt_baseline=Dict();planned_baseline=Dict()
    for key in keys
        b=G.choose_path(years,zeros(length(years)),economies[key[2]],coasts[key];quad=quad)
        if scenario=="SSP4" && extension=="none" && !geometric
            @assert isapprox(R.present_value(b.path.total,years),base[key];rtol=1e-9,atol=.001)
        else
            base[key]=R.present_value(b.path.total,years)
        end
        noadapt_baseline[key]=R.present_value(b.paths[1].total,years)
        planned_baseline[key]=b.candidate.strategy==:retreat ? sum(b.path.migrants) : 0.
    end
    # Exact previously computed1m controls check the independent input assembly.
    for key in (scenario=="SSP4" && extension=="none" && !geometric ? (first(keys),last(keys)) : ())
        g=coasts[key];eco=economies[key[2]];sea=((years.-2010)./90).^1.5
        result=G.choose_path(years,sea,eco,g;quad=quad)
        aux=Float64(design[findfirst(i->design[i,3]==key[1] && design[i,4]==key[2],axes(design,1)),6])
        got=R.present_value(result.path.total,years)-base[key]
        @assert isapprox(got,aux;rtol=1e-9,atol=.001)
    end
    open(".local/"*prefix*"_cases.csv","w") do io
        println(io,"sample,coast_id,country,strategy,return_period,incremental_pv_USD2019PPP,no_adaptation_incremental_pv_USD2019PPP,migrants,planned_migrants,incremental_planned_migrants,construction_pv,maintenance_pv,retreat_pv,inundation_pv,wetland_pv,flood_pv,absolute_pv_USD2019PPP,exclude2010_pv_USD2019PPP,exclude2010_2019_pv_USD2019PPP,constant2010_subtracted_pv_USD2019PPP")
        for (counter,member) in enumerate(members)
            sea=sealevel[member]
            for (ki,key) in enumerate(keys)
                result=G.choose_path(years,sea,economies[key[2]],coasts[key];quad=quad)
                pv=R.present_value(result.path.total,years);components=[R.present_value(result.path.costs[:,j],years) for j in 1:6]
                @assert abs(sum(components)-pv)<max(.001,abs(pv)*1e-12)
                noadapt=R.present_value(result.paths[1].total,years)-noadapt_baseline[key]
                planned=result.candidate.strategy==:retreat ? sum(result.path.migrants) : 0.
                firstdecade=findall(y->y<2020,years)
                exclude2010=pv-result.path.total[1]
                excludeinterval=pv-R.present_value(result.path.total[firstdecade],years[firstdecade])
                constant=pv-R.present_value(fill(result.path.total[1],length(years)),years)
                println(io,join((member,key...,result.candidate.strategy,result.candidate.return_period,pv-base[key],noadapt,sum(result.path.migrants),planned,planned-planned_baseline[key],components...,pv,exclude2010,excludeinterval,constant),","))
                if pilot && ki<=2
                    fine=G.choose_path(years,sea,economies[key[2]],coasts[key];quad=G.quadrature(24))
                    fpv=R.present_value(fine.path.total,years)
                    push!(checks,(member,key...,abs(fpv-pv)/max(1.,abs(pv)),fine.choice==result.choice))
                end
            end
            flush(io);println("Completed coupled member ",counter,"/",length(members)," across ",length(keys)," sampled coasts in ",round(time()-started,digits=1)," seconds");flush(stdout)
        end
    end
    if pilot
        open("results/"*prefix*"_refinement.csv","w") do io
            println(io,"sample,coast_id,country,relative_quadrature_difference,same_policy")
            for row in checks;println(io,join(row,","));end
        end
    end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("members"=>length(members),"draws_per_region"=>perregion,"unique_coasts"=>length(keys),
            "wall_seconds"=>time()-started,"raw_cases"=>".local/"*prefix*"_cases.csv",
            "scope"=>"NON-REPRODUCTION: independently coupled alternativeSLR; uniform geography; sampled200-bin coasts;2019PPP;pairedzeroSLRbaseline",
            "scenario"=>scenario,"last_year"=>years[end],"after2100_economics"=>extension,
            "within_node_economics"=>(geometric ? "geometric" : "linear"),
            "pilot_is_purposive"=>pilot,"completed"=>true))
    end
end
main()
