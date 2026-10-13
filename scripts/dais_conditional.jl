using DelimitedFiles,Statistics,Random,TOML,SHA
include("../src/PaleoDAIS.jl")
const D=PaleoDAIS
c=TOML.parsefile("config/dais_conditional.toml")
forcing=readdlm("inputs/dais_alternative_forcing.csv",',',Float64;skipstart=1)
times=sort(unique(vcat([-118000.,-18000.,-4000.],collect(1961.5:1.:2009.5),collect(1992.:1.:2009.))))
reference=map(t->findfirst(==(t),times),collect(1961.5:1.:1990.5))
idx(t)=findfirst(==(t),times)
function evaluate(x;dt=c["maximum_step_years"])
    gamma,alpha,lambda,threshold=x
    z=D.run(forcing,times;p=D.M.dais_parameters(gamma=gamma,alpha=alpha),dt=dt,
        initial_radius=c["initial_radius_m"],lambda=lambda,threshold=threshold)
    sle=(mean(z.volume[reference]).-z.volume).*D.SLE_PER_VOLUME
    predictions=vcat(sle[1:3],sle[idx(2002.5)]-sle[idx(1992.5)])
    residual=(predictions.-[5.5,-11.35,-2.63,.00197])./[.95,2.23,.68,.00046]
    score=sum(abs2,residual)
    windows=(3.6<=predictions[1]<=7.4,abs(residual[2])<=2,abs(residual[3])<=2,abs(residual[4])<=2)
    (score=score,predictions=predictions,windows=windows,z=z)
end
function main()
if "--check-saved" in ARGS
    saved=TOML.parsefile("results/dais_conditional_best.toml")
    @assert saved["forcing_sha256"]==bytes2hex(sha256(read("inputs/dais_alternative_forcing.csv")))
    x=[saved[k] for k in ("gamma","alpha","lambda_m_yr","threshold_degC")]
    fine=evaluate(x;dt=5.);coarse=evaluate(x;dt=10.)
    @assert maximum(abs.(fine.predictions-saved["window_predictions_m"]))<1e-8
    @assert maximum(abs.(fine.predictions-coarse.predictions))<1e-5
    println("Saved conditional Antarctic point fit and step refinement verified; not target posterior.")
    return
end
started=time();rng=MersenneTwister(c["seed"])
n="--pilot" in ARGS ? c["pilot_samples"] : c["samples"]
bounds=hcat(c["gamma_bounds"],c["alpha_bounds"],c["lambda_bounds_m_yr"],c["threshold_bounds_degC"])
unit=zeros(n,4)
for j in 1:4;unit[:,j]=(randperm(rng,n).-rand(rng,n))./n;end
parameters=bounds[1,:]'.+unit.*(bounds[2,:]-bounds[1,:])'
rows=[];scores=fill(Inf,n)
for i in 1:n
    result=evaluate(parameters[i,:]);scores[i]=result.score
    push!(rows,(i,parameters[i,:]...,result.predictions...,result.score,result.windows...,all(result.windows)))
    if i%32==0;println("Completed ",i," samples in ",round(time()-started,digits=2)," seconds");flush(stdout);end
end
prefix="--pilot" in ARGS ? "dais_conditional_pilot" : "dais_conditional"
open("results/"*prefix*"_samples.csv","w") do io
    println(io,"sample,gamma,alpha,lambda_m_yr,threshold_degC,LIG_m,LGM_m,mid_Holocene_m,1992_2002_m,window_chisq,LIG_pass,LGM_pass,MH_pass,modern_pass,all_windows_pass")
    for row in rows;println(io,join(row,","));end
end
refinements=[];best=argmin(scores);x=copy(parameters[best,:]);result=evaluate(x;dt=10.)
# Deterministic bounded coordinate search refines a conditional best fit.
# It neither assigns probabilities nor uses any published model outputs.
steps=(bounds[2,:]-bounds[1,:])./16
evaluations=0
for iteration in 1:60
    improved=false
    for j in 1:4,direction in (-1,1)
        trial=copy(x);trial[j]=clamp(x[j]+direction*steps[j],bounds[1,j],bounds[2,j])
        trial[j]==x[j] && continue
        candidate=evaluate(trial;dt=10.);evaluations+=1
        if candidate.score<result.score;x=trial;result=candidate;improved=true;end
    end
    !improved && (steps./=2)
    if iteration%10==0;println("Conditional optimizer iteration ",iteration," chi-square ",result.score);flush(stdout);end
    maximum(steps./(bounds[2,:]-bounds[1,:]))<1e-5 && break
end
for i in sortperm(scores)[1:min(n,16)]
    a=evaluate(parameters[i,:];dt=50.);b=evaluate(parameters[i,:];dt=10.)
    push!(refinements,(i,a.score,b.score,maximum(abs.(a.predictions-b.predictions)),maximum(abs.(a.z.volume-b.z.volume))*D.SLE_PER_VOLUME))
end
fine=evaluate(x;dt=5.)
open("results/"*prefix*"_refinement.csv","w") do io
    println(io,"sample,chisq_dt50,chisq_dt10,max_window_difference_m,max_SLE_difference_m")
    for row in refinements;println(io,join(row,","));end
end
open("results/"*prefix*"_best.toml","w") do io
    TOML.print(io,Dict("gamma"=>x[1],"alpha"=>x[2],"lambda_m_yr"=>x[3],"threshold_degC"=>x[4],
        "window_predictions_m"=>fine.predictions,"window_chisq"=>fine.score,"all_windows_pass"=>all(fine.windows),
        "maximum_dt10_dt5_window_difference_m"=>maximum(abs.(result.predictions-fine.predictions)),
        "scope"=>"Conditional point fit; NOT a posterior, target calibration, or independent validation",
        "forcing_sha256"=>bytes2hex(sha256(read("inputs/dais_alternative_forcing.csv"))),
        "latin_hypercube_samples"=>n,"optimizer_evaluations"=>evaluations,"wall_seconds"=>time()-started))
end
z=fine.z
open("results/"*prefix*"_modern_rates.csv","w") do io
    println(io,"year,mass_loss_Gt_yr,role")
    # Integrate each calendar year under the midyear-interpolated forcing.
    for year in 1992:2008
        loss=(z.volume[idx(Float64(year))]-z.volume[idx(year+1.)])*D.SLE_PER_VOLUME*362500
        println(io,join((year,loss,year>=2003 ? "withheld_after_cumulative_constraint" : "overlaps_cumulative_constraint"),","))
    end
end
println("Best conditional fit: ",x," windows ",fine.predictions," chi-square ",fine.score,"; not target posterior")
end
main()
