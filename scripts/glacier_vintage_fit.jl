using DelimitedFiles,Statistics,TOML
include("../src/Reproduction.jl");include("../src/IceModels.jl")
const I=IceModels
"""Grid-bracketed scalar least squares, independent of an assumed posterior."""
function scalarfit(f,lo,hi)
    grid=collect(range(lo,hi,length=161));values=f.(grid);j=argmin(values)
    a=grid[max(1,j-1)];b=grid[min(length(grid),j+1)];ratio=(sqrt(5)-1)/2
    c=b-ratio*(b-a);d=a+ratio*(b-a);fc=f(c);fd=f(d)
    for _ in 1:65
        if fc<fd;b=d;d=c;fd=fc;c=b-ratio*(b-a);fc=f(c)
        else;a=c;c=d;fc=fd;d=a+ratio*(b-a);fd=f(d);end
    end
    candidates=[lo,hi,(a+b)/2];x=candidates[argmin(f.(candidates))]
    x,f(x)
end
function main()
    started=time();op58="--op58" in ARGS;prefix=op58 ? "glacier_op58" : "glacier_vintage"
    obs=readdlm(op58 ? "inputs/dyurgerov_meier2005_op58.csv" : "inputs/dyurgerov2005_global.csv",',',Float64;skipstart=1)
    years=collect(1961:2021);fit=Int.(obs[:,1]).<=1995;hold=.!fit
    records=readdlm("inputs/ice_mass_balance.csv",',',Any;skipstart=1)
    newer=records[(records[:,1].=="glaciers").&(records[:,2].>=2004).&(records[:,2].<=2020),:]
    summaries=[];grids=[];paths=[];checks=[]
    for (name,file) in (("HadCRUT4","hadcrut4"),("HadCRUT5","hadcrut5_5010"))
        t=readdlm("inputs/"*file*".csv",',',Float64;skipstart=1)
        temperature=t[1961 .<=t[:,1].<=2021,2].-mean(t[1850 .<=t[:,1].<=1870,2])
        function calculate(beta,volume,exponent,initial)
            s=I.glaciers(temperature,beta,volume,exponent,initial)
            (state=s,rate=1000diff(s))
        end
        truth=.0012
        synthetic=calculate(truth,.4,.775,0.).rate[1:35]
        recovered,_=scalarfit(b->sum(abs2,calculate(b,.4,.775,0.).rate[1:35]-synthetic),0.,.041)
        @assert abs(recovered-truth)<1e-10
        push!(checks,(name,abs(recovered-truth)))
        fits=[]
        for volume in (.3,.4,.5),exponent in (.55,.775,1.),initial in (-.0041,0.,.0041)
            beta,objective=scalarfit(b->mean(abs2,calculate(b,volume,exponent,initial).rate[1:35]-obs[fit,2]),0.,.041)
            p=calculate(beta,volume,exponent,initial)
            idx=Int.(obs[:,1]).-1960
            rmse=sqrt(mean(abs2,p.rate[idx[hold]]-obs[hold,2]))
            # Newer observations have different spatial coverage: this is a
            # contextual extrapolation check, not an exact matched-data score.
            ni=Int.(newer[:,2]).-1960;measured=-Float64.(newer[:,4])/362.5
            modern=sqrt(mean(abs2,p.rate[ni]-measured))
            row=(name,beta,volume,exponent,initial,sqrt(objective),rmse,modern)
            push!(grids,row);push!(fits,(objective=objective,row=row,p=p))
        end
        best=fits[argmin([f.objective for f in fits])]
        x=Float64.(obs[fit,1]).-1961;A=hcat(ones(length(x)),x);trend=A\obs[fit,2]
        predicted=trend[1].+trend[2].*(obs[hold,1].-1961)
        trendrmse=sqrt(mean(abs2,predicted-obs[hold,2]))
        push!(summaries,(best.row...,trendrmse,minimum(f.row[7] for f in fits),maximum(f.row[7] for f in fits)))
        for i in 1:length(years)-1
            push!(paths,(name,years[i],best.p.rate[i],best.p.state[i+1]-best.p.state[1]))
        end
        println(name," best conditional grid point: ",best.row," held-out trendRMSE=",trendrmse);flush(stdout)
    end
    function save(name,header,rows)
        open("results/"*prefix*"_"*name*".csv","w") do io
            println(io,header);for row in rows;println(io,join(row,","));end
        end
    end
    header="temperature,beta_m_K_yr,volume_m,exponent,initial1961_m,training_RMSE_mm_yr,holdout1996_2003_RMSE_mm_yr,context2004_2020_RMSE_mm_yr"
    save("grid",header,grids)
    save("fits",header*",holdout_trend_RMSE_mm_yr,grid_holdout_min_RMSE_mm_yr,grid_holdout_max_RMSE_mm_yr",summaries)
    save("hindcast","temperature,year,sea_level_rate_mm_yr,cumulative_since1961_m",paths)
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("wall_seconds"=>time()-started,"observational_source"=>(op58 ? "DyurgerovMeier2005OP58p117roundedtable" : "NSIDCSupplement2005Appendix6spreadsheet"),"grid_points"=>54,"training_years"=>"1961–1995","holdout_years"=>"1996–2003",
            "maximum_noise_free_beta_error"=>maximum(x[2] for x in checks),
            "scope"=>"NON-REPRODUCTION: scalar pointfits conditional on27B17physicalgridpoints pertemperaturevintage; no AR1 likelihood or posterior",
            "initial_condition"=>"Independent1961origin for B17S0bounds; not established target initialization; V0 numerical prior reused with reference qualification",
            "observable"=>"Annual SLR increments indexed by starting year under linearlyinterpolatedtemperature; no invented annual observationalSD",
            "coverage"=>"DM05includes peripheral glaciers and provider785000km2 extrapolation; GlaMBIEcontext uses362.5Gt/mm conversion"))
    end
end
main()
