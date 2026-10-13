using DelimitedFiles,Statistics,TOML
include("../src/RecoveredModels.jl")
include("../src/CarbonCycle.jl")
const C=CarbonCycle
emissions,_=readdlm("inputs/gcb2023_emissions.csv",',',Any;header=true)
temperature,_=readdlm("inputs/hadcrut4.csv",',',Float64;header=true)
observations,_=readdlm("inputs/noaa_co2.csv",',',Float64;header=true)
years=collect(1850:2021)
e=emissions[1850 .<=emissions[:,1].<=2021,:]
number(x)=x=="" ? 0.0 : Float64(x)
q=number.(e[:,2])+number.(e[:,3])-number.(e[:,4])
@assert Int.(temperature[:,1])==years
t=temperature[:,2].-mean(temperature[1:30,2])
obs=observations[observations[:,1].<=2021,:]
fit=obs[:,1].<=2005;hold=obs[:,1].>2005
idx=Int.(obs[:,1]).-years[1].+1
function simulate(beta,q10,eta;substeps=8)
    p=C.parameters(beta=beta,q10=q10,exchange=eta)
    x=C.prescribed_run(q,t;p=p,substeps=substeps)
    parts=[C.partition(x[1,i],p) for i in eachindex(years)]
    co2=[part.co2 for part in parts]
    ocean=[parts[i].mixed+sum(x[2:4,i]) for i in eachindex(years)]
    (co2=co2,ocean=ocean,carbon=x)
end
function minimize(f,lo,hi;tol=1e-5)
    ratio=(sqrt(5)-1)/2;c=hi-ratio*(hi-lo);d=lo+ratio*(hi-lo)
    fc=f(c);fd=f(d)
    while hi-lo>tol
        if fc<fd;hi=d;d=c;fd=fc;c=hi-ratio*(hi-lo);fc=f(c)
        else;lo=c;c=d;fc=fd;d=lo+ratio*(hi-lo);fd=f(d);end
    end
    (lo+hi)/2
end
open("results/carbon_conditional_fit.csv","w") do io
open("results/carbon_conditional_trajectories.csv","w") do tio
    println(io,"q10,exchange_m_yr,fitted_beta,training_co2_rmse_ppm,holdout_co2_rmse_ppm,holdout_bias_ppm,ocean_1994_GtC,ocean_flux_1980s_GtC_yr,ocean_flux_1990s_GtC_yr,beta_boundary_hit,max_mass_error_GtC,substep_refinement_co2_ppm")
    println(tio,"q10,exchange_m_yr,beta,year,co2_ppm,ocean_carbon_GtC")
    for q10 in (1.,2.,3.),eta in (10.,16.87,30.)
        objective=beta->sum(abs2,simulate(beta,q10,eta).co2[idx[fit]]-obs[fit,2])
        beta=minimize(objective,0.,2.)
        run=simulate(beta,q10,eta);fine=simulate(beta,q10,eta;substeps=16)
        rmse(mask)=sqrt(mean(abs2,run.co2[idx[mask]]-obs[mask,2]))
        inventory(y)=run.ocean[y-years[1]+1]
        cumulative=vcat(0.,cumsum((q[1:end-1]+q[2:end])/2))
        balance=maximum(abs.(vec(sum(run.carbon,dims=1)).-sum(C.initial_state()).-cumulative))
        println(io,join((q10,eta,beta,rmse(fit),rmse(hold),mean(run.co2[idx[hold]]-obs[hold,2]),
            inventory(1994),(inventory(1990)-inventory(1980))/10,(inventory(2000)-inventory(1990))/10,
            beta<1e-4||beta>1.9999,balance,maximum(abs.(run.co2-fine.co2))),","))
        for i in eachindex(years);println(tio,join((q10,eta,beta,years[i],run.co2[i],run.ocean[i]),","));end
        println("Carbon conditional fit: Q10=",q10," exchange=",eta," beta=",beta," held-out RMSE=",rmse(hold));flush(stdout)
    end
end
end
