using DelimitedFiles,Statistics,LinearAlgebra,TOML
include("../src/RecoveredModels.jl");include("../src/CarbonCycle.jl")
const C=CarbonCycle
include("../src/BoundedLeastSquares.jl")
bounded_fit(args...;kwargs...)=BoundedLeastSquares.fit(args...;kwargs...)
function legacy_fit(residual,start;iterations=24)
    u=copy(start);r=residual(u);value=sum(abs2,r)
    for iteration in 1:iterations
        jac=zeros(length(r),length(u));delta=1e-4
        for j in eachindex(u)
            a=copy(u);b=copy(u);a[j]=max(0.,u[j]-delta);b[j]=min(1.,u[j]+delta)
            jac[:,j]=(residual(b)-residual(a))/(b[j]-a[j])
        end
        step=-(jac'jac+1e-8I)\(jac'r);accepted=false
        for factor in (1.,.5,.25,.125,.0625,.03125,.015625)
            trial=clamp.(u+factor*step,0.,1.);rr=residual(trial);v=sum(abs2,rr)
            if v<value
                change=maximum(abs.(trial-u));u=trial;r=rr;value=v;accepted=true
                change<1e-7 && return (u=u,objective=value,iterations=iteration,projected_gradient=NaN,stop="legacy_unchecked")
                break
            end
        end
        !accepted && return (u=u,objective=value,iterations=iteration,projected_gradient=NaN,stop="legacy_unchecked")
    end
    (u=u,objective=value,iterations=iterations,projected_gradient=NaN,stop="legacy_unchecked")
end
function main(;forcefixed=false)
    started=time();pilot=!forcefixed && "--pilot" in ARGS;free=!forcefixed && "--free-physics" in ARGS
    revised=forcefixed || "--revised-solver" in ARGS
    solver=(free || revised) ? bounded_fit : legacy_fit
    prefix="carbon_vintage"*(free ? "_free" : revised ? "_revised" : "")*(pilot ? "_pilot" : "")
    emissions=readdlm("inputs/gcb2023_emissions.csv",',',Any;skipstart=1)
    e=emissions[1850 .<=emissions[:,1].<=2021,:];number(x)=x=="" ? 0. : Float64(x)
    q=number.(e[:,2])+number.(e[:,3])-number.(e[:,4]);years=collect(1850:2021)
    mlo=readdlm("inputs/noaa_mlo_co2.csv",',',Float64;skipstart=1)
    law=readdlm("inputs/law_dome2006_calibration.csv",',',Any;skipstart=1)
    ages=Float64.(law[:,1]);lawco2=Float64.(law[:,2]);mi=Int.(mlo[:,1]).-1849
    train=mlo[:,1].<=2005;hold=mlo[:,1].>2005
    interpolate(v,t)=begin k=floor(Int,t)-1849;v[k]+(t-floor(t))*(v[k+1]-v[k]) end
    function simulate(u,t;substeps=8)
        p=C.parameters(beta=u[1],c0=275+20u[2],q10=free ? .2+4.8u[3] : 2.,exchange=free ? .5+199.5u[4] : 16.87)
        x=C.prescribed_run(q,t;p=p,substeps=substeps)
        parts=[C.partition(x[1,i],p) for i in eachindex(years)]
        (co2=[a.co2 for a in parts],carbon=x,ocean=[parts[i].mixed+sum(x[2:4,i]) for i in eachindex(years)])
    end
    summaries=[];checks=[];searches=[]
    open("results/"*prefix*"_trajectories.csv","w") do io
        println(io,"case,year,co2_ppm,ocean_carbon_GtC")
        cases=pilot ? [("HadCRUT4_joint","hadcrut4",true)] : [("HadCRUT4_MLO_only","hadcrut4",false),("HadCRUT4_joint","hadcrut4",true),("HadCRUT5_joint","hadcrut5_5010",true)]
        for (name,input,joint) in cases
            temperature=readdlm("inputs/"*input*".csv",',',Float64;skipstart=1)
            t=temperature[:,2].-mean(temperature[1:30,2])
            residual(u)=begin
                s=simulate(u,t).co2
                modern=(s[mi[train]]-mlo[train,2])/sqrt(sum(train))
                joint ? vcat(modern,([interpolate(s,a) for a in ages]-lawco2)/sqrt(length(ages))) : modern
            end
            if pilot || forcefixed
                truth=free ? [.72,(283.5-275)/20,(2.2-.2)/4.8,(24-.5)/199.5] : [.72,(283.5-275)/20]
                synthetic=simulate(truth,t).co2
                synthetic_residual(u)=simulate(u,t).co2[1:10:end]-synthetic[1:10:end]
                recovered=solver(synthetic_residual,free ? [.5,.2,.4,.1] : [.5,.2];iterations=80)
                @assert maximum(abs.(recovered.u-truth))<1e-5
                push!(checks,("noise_free_parameter_recovery_scaled",maximum(abs.(recovered.u-truth))))
            end
            starts=free ? [[.667,.25,(v[1]-.2)/4.8,(v[2]-.5)/199.5] for v in ((1.,10.),(2.,40.),(4.,100.))] : [[.667,.25]]
            nested_objective=NaN
            if free
                nested=readdlm("results/carbon_vintage_revised_fits.csv",',',Any;skipstart=1)
                row=nested[findfirst(nested[:,1].==name),:]
                nested_start=[Float64(row[2]),(Float64(row[3])-275)/20,(2.-.2)/4.8,(16.87-.5)/199.5]
                push!(starts,nested_start);nested_objective=sum(abs2,residual(nested_start))
            end
            free && pilot && (starts=[last(starts)])
            fits=[]
            for (start_index,start) in enumerate(starts)
                println("Starting ",name," search ",start_index,"/",length(starts));flush(stdout)
                fit=solver(residual,start;iterations=(free || revised) ? 100 : 24)
                push!(fits,fit)
                println("Search objective=",fit.objective," iterations=",fit.iterations," stop=",fit.stop," projected_gradient=",fit.projected_gradient);flush(stdout)
            end
            for (k,fit) in enumerate(fits)
                push!(searches,(name,k,fit.objective,fit.iterations,fit.u[1],275+20fit.u[2],free ? .2+4.8fit.u[3] : 2.,free ? .5+199.5fit.u[4] : 16.87,fit.projected_gradient,fit.stop))
            end
            fitted=fits[argmin([fit.objective for fit in fits])]
            free && @assert fitted.objective<=nested_objective+1e-8
            u=fitted.u;s=simulate(u,t);fine=simulate(u,t;substeps=16)
            lawerror=[interpolate(s.co2,a) for a in ages]-lawco2
            cumulative=vcat(0.,cumsum((q[1:end-1]+q[2:end])/2))
            balance=maximum(abs.(vec(sum(s.carbon,dims=1)).-sum(C.initial_state()).-cumulative))
            @assert balance<1e-8 && maximum(abs.(fine.co2-s.co2))<.001
            push!(summaries,(name,u[1],275+20u[2],fitted.objective,fitted.iterations,
                sqrt(mean(abs2,s.co2[mi[train]]-mlo[train,2])),sqrt(mean(abs2,s.co2[mi[hold]]-mlo[hold,2])),
                mean(s.co2[mi[hold]]-mlo[hold,2]),sqrt(mean(abs2,lawerror)),s.ocean[1994-1849],balance,
                maximum(abs.(fine.co2-s.co2)),any(u.<1e-5)||any(u.>1-1e-5),free ? .2+4.8u[3] : 2.,free ? .5+199.5u[4] : 16.87))
            for i in eachindex(years);println(io,join((name,years[i],s.co2[i],s.ocean[i]),","));end
            println(name," beta=",u[1]," C0=",275+20u[2]," holdoutRMSE=",sqrt(mean(abs2,s.co2[mi[hold]]-mlo[hold,2])));flush(stdout)
        end
    end
    open("results/"*prefix*"_fits.csv","w") do io
        println(io,"case,beta,initial1850_co2_ppm,objective,iterations,MLO_training_RMSE_ppm,MLO_holdout_RMSE_ppm,MLO_holdout_bias_ppm,LawDome_RMSE_ppm,ocean1994_GtC,max_mass_error_GtC,substep_difference_ppm,boundary_hit,q10,thermocline_transfer_m_yr")
        for row in summaries;println(io,join(row,","));end
    end
    open("results/"*prefix*"_searches.csv","w") do io
        println(io,"case,start,objective,iterations,beta,initial1850_co2_ppm,q10,thermocline_transfer_m_yr,projected_gradient,stop")
        for row in searches;println(io,join(row,","));end
    end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("wall_seconds"=>time()-started,"cases"=>length(summaries),"pilot_checks"=>Dict(checks),
            "scope"=>"NON-REPRODUCTION: conditional point fit; equal mean-square weight for modern and LawDome groups; no posterior or age convolution",
            "free_carbon_physics"=>free,"starts"=>(free && !pilot ? 4 : 1),"revised_solver"=>(free || revised),
            "constraints"=>(free ? "U10 beta[0,1],CO2initial[275,295]ppm,Q10[.2,5],thermocline transfer[.5,200]m/yr; four starting points including nested restricted fit, not proof of global optimum" : "U10 beta[0,1],CO2initial[275,295]ppm; Q10=2,transfer16.87m/yr fixed")*"; steady1850 pools; observed-temperature forcing; holdout2006–2021"))
    end
end
# Audit the restricted model with the corrected solver before the free pilot.
if "--free-physics" in ARGS && "--pilot" in ARGS;main(forcefixed=true);end
main()
