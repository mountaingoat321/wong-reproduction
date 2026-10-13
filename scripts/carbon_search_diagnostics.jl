using DelimitedFiles,Statistics
include("../src/RecoveredModels.jl")
include("../src/CarbonCycle.jl")
const C=CarbonCycle
e=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
e=e[1850 .<=e[:,1].<=2021,:];number(x)=x=="" ? 0. : Float64(x)
q=number.(e[:,2])+number.(e[:,3])-number.(e[:,4])
mlo=readdlm("inputs/noaa_mlo_co2.csv",',',Float64;skipstart=1)
law=readdlm("inputs/law_dome2006_calibration.csv",',',Any;skipstart=1)
ages=Float64.(law[:,1]);lawco2=Float64.(law[:,2]);mi=Int.(mlo[:,1]).-1849
train=mlo[:,1].<=2005;hold=mlo[:,1].>2005
interpolate(v,t)=begin k=floor(Int,t)-1849;v[k]+(t-floor(t))*(v[k+1]-v[k]) end
searches=readdlm("results/carbon_vintage_free_searches.csv",',',Any;skipstart=1)
open("results/carbon_search_predictions.csv","w") do io
    println(io,"case,start,objective,holdout_RMSE_ppm,holdout_bias_ppm,LawDome_RMSE_ppm,ocean1994_GtC,max_newton_bisection_difference_ppm,substep_difference_ppm")
    for row in eachrow(searches)
        name=String(row[1]);input=startswith(name,"HadCRUT5") ? "hadcrut5_5010" : "hadcrut4"
        t=readdlm("inputs/"*input*".csv",',',Float64;skipstart=1)[:,2];t.-=mean(t[1:30])
        kwargs=(beta=Float64(row[5]),c0=Float64(row[6]),q10=Float64(row[7]),exchange=Float64(row[8]))
        p=C.parameters(;kwargs...,fast_equilibrium=true);reference=C.parameters(;kwargs...)
        a=C.prescribed_run(q,t;p=p);b=C.prescribed_run(q,t;p=reference);fine=C.prescribed_run(q,t;p=p,substeps=16)
        parts=[C.partition(x,p) for x in a[1,:]];co2=[x.co2 for x in parts]
        c_reference=[C.partition(x,reference).co2 for x in b[1,:]]
        c_fine=[C.partition(x,p).co2 for x in fine[1,:]]
        lawerror=[interpolate(co2,age) for age in ages]-lawco2
        objective=mean(abs2,co2[mi[train]]-mlo[train,2])+(endswith(name,"joint") ? mean(abs2,lawerror) : 0.)
        @assert abs(objective-Float64(row[3]))<1e-8
        @assert maximum(abs.(co2-c_reference))<1e-6 && maximum(abs.(co2-c_fine))<.001
        k=1994-1849;ocean=parts[k].mixed+sum(a[2:4,k])
        println(io,join((name,row[2],objective,sqrt(mean(abs2,co2[mi[hold]]-mlo[hold,2])),
            mean(co2[mi[hold]]-mlo[hold,2]),sqrt(mean(abs2,lawerror)),ocean,
            maximum(abs.(co2-c_reference)),maximum(abs.(co2-c_fine))),','))
    end
end
println("Replayed all12 searches; objective, chemistry and time-step checks pass.")
