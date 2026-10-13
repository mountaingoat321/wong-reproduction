using DelimitedFiles,Statistics,TOML
include("../src/PaleoDAIS.jl")
const D=PaleoDAIS
forcing=readdlm("inputs/dais_alternative_forcing.csv",',',Float64;skipstart=1)
targets=[-118000.,-18000.,-4000.,1992.5,2002.5]
times=sort(unique(vcat(collect(-238000.:1000.:0.),collect(.5:100.:1800.5),
    collect(1850.5:1.:2009.5),targets,[-218000.,2009.5])))
reference=map(t->findfirst(==(t),times),collect(1961.5:1.:1990.5))
function summarize(name,z,dt,initial_radius,gamma,alpha,lambda,threshold)
    vref=mean(z.volume[reference]);sle=(vref.-z.volume).*D.SLE_PER_VOLUME
    indices=map(t->findfirst(==(t),times),targets)
    lig,lgm,mh=sle[indices[1:3]]
    modern=sle[indices[5]]-sle[indices[4]]
    # W17F's written independent windows only; no extra process-error fit or
    # modern mass-loss likelihood. This score is a diagnostic, not a posterior.
    chisq=((lig-5.5)/.95)^2+((lgm+11.35)/2.23)^2+((mh+2.63)/.68)^2+((modern-.00197)/.00046)^2
    windows=(3.6<=lig<=7.4,-15.81<=lgm<=-6.89,-3.99<=mh<=-1.27,.00105<=modern<=.00289)
    (name,dt,initial_radius,gamma,alpha,lambda,threshold,vref,z.volume[end],lig,lgm,mh,modern,
     chisq,all(windows),minimum(z.volume),sle)
end
rows=[];trajectories=[];convergence=[]
function run_case(name;dt=10.,initial_radius=1.8636e6,gamma=2.,alpha=.35,lambda=0.,threshold=-15.)
    z=D.run(forcing,times;p=D.M.dais_parameters(gamma=gamma,alpha=alpha),dt=dt,
        initial_radius=initial_radius,lambda=lambda,threshold=threshold)
    summary=summarize(name,z,dt,initial_radius,gamma,alpha,lambda,threshold)
    push!(rows,summary[1:end-1]);sle=summary[end]
    for j in eachindex(times)
        push!(trajectories,(name,times[j],z.radius[j],z.volume[j],sle[j]))
    end
    println(name," LIG/LGM/MH/modern m = ",summary[10:13]);flush(stdout)
    z
end
started=time()
central=run_case("s14_case4")
if "--pilot" in ARGS
    fine=run_case("s14_case4_dt5";dt=5.)
    println("Maximum volume/SLE discretization difference: ",maximum(abs.(central.volume-fine.volume))," / ",D.SLE_PER_VOLUME*maximum(abs.(central.volume-fine.volume)))
else
    for (case,gamma,alpha) in ((1,1.,0.),(2,2.,0.),(3,1.,.35),(5,3.5,.45))
        run_case("s14_case"*string(case);gamma=gamma,alpha=alpha)
    end
    for dt in (20.,5.,2.5)
        z=run_case("s14_case4_dt"*string(dt);dt=dt)
        push!(convergence,(dt,maximum(abs.(z.volume-central.volume)),D.SLE_PER_VOLUME*maximum(abs.(z.volume-central.volume))))
    end
    for multiplier in (.9,1.1)
        run_case("initial_radius_"*string(multiplier);initial_radius=multiplier*1.8636e6)
    end
    for lambda in (.005,.01,.015),threshold in (-20.,-18.,-16.,-14.,-12.,-10.)
        run_case("fast_"*string(lambda)*"_"*string(threshold);lambda=lambda,threshold=threshold)
    end
    for dt in (5.,2.5)
        run_case("fast_refine_"*string(dt);dt=dt,lambda=.01,threshold=-16.)
    end
    for name in ("spratt_unshifted","waelbroeck_primary","waelbroeck_unadjusted")
        original=copy(forcing)
        global forcing=readdlm("inputs/dais_forcing_"*name*".csv",',',Float64;skipstart=1)
        run_case("forcing_"*name)
        run_case("forcing_fast_"*name;lambda=.01,threshold=-16.)
        global forcing=original
    end
end
function save(name,header,data)
    open("results/"*name,"w") do io
        println(io,header)
        for row in data;println(io,join(row,","));end
    end
end
prefix="--pilot" in ARGS ? "dais_paleo_pilot" : "dais_paleo"
save(prefix*"_metrics.csv","experiment,step_years,initial_radius_m,gamma,alpha,lambda_m_yr,threshold_degC,reference_volume_1e15m3,end_volume_1e15m3,LIG_m,LGM_m,mid_Holocene_m,1992_2002_m,window_chisq,all_windows_pass,min_volume_1e15m3",rows)
save(prefix*"_trajectories.csv","experiment,year_CE,radius_m,volume_1e15m3,sea_level_relative1961_1990_m",trajectories)
save(prefix*"_convergence.csv","step_years,maximum_volume_difference_from_dt10_1e15m3,maximum_SLE_difference_from_dt10_m",convergence)
open("results/"*prefix*"_run.toml","w") do io
    TOML.print(io,Dict("scope"=>"NON-REPRODUCTION; alternative paleo/ocean forcing; fixed S14 physical cases and fast-loss sensitivity; no target posterior", "wall_seconds"=>time()-started,"cases"=>length(rows),"maximum_step_years"=>20.,"threads"=>1))
end
