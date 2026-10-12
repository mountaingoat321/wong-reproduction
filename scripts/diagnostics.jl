using TOML, DelimitedFiles, Statistics
include(joinpath(@__DIR__,"..","src","Reproduction.jl"))
const R=Reproduction
const ROOT=normpath(joinpath(@__DIR__,".."))
const cfg=TOML.parsefile(joinpath(ROOT,"config","validation.toml"))
function savecsv(name, header, rows)
    open(joinpath(ROOT,"results",name),"w") do io
        println(io,join(header,","))
        for row in rows; println(io,join(row,",")); end
    end
end

rows=[]; e=cfg["emissions"]
for gamma in e["decline_rates"], dt in e["steps"]
    q=e["peak_rate"]
    for j in 1:round(Int,e["duration"]/dt)
        u=exp(-gamma*j*dt)
        q-=dt*2e["peak_rate"]*gamma*u/(1+u)^2
    end
    exact=2e["peak_rate"]/(1+exp(min(700.,gamma*e["duration"])))
    push!(rows,(gamma,dt,q/e["peak_rate"],exact/e["peak_rate"],gamma*dt/4))
end
savecsv("emissions_limit.csv",["decline_per_year","step_years","remaining_fraction","continuous_fraction","endpoint_error_prediction"],rows)
_,q=R.emissions(0,300,1.,0.,0,.07)
savecsv("emissions_curve.csv",["years_after_peak","annual_recurrence","continuous_logistic"],[(i,q[i+1],2/(1+exp(.07i))) for i in 0:300])

g=cfg["greenland"]; rows=[]
eq=g["c"]*g["temperature"]+g["b"]; rate=g["alpha"]*g["temperature"]+g["beta"]
truth=eq+(g["initial_volume"]-eq)*exp(-rate*g["duration"])
f=(t,v)->R.greenland_rhs(v,g["temperature"];c=g["c"],b=g["b"],alpha=g["alpha"],beta=g["beta"])
for dt in g["steps"]
    v=R.rk4(f,g["initial_volume"],0.,dt,Int(g["duration"]/dt))[end]
    push!(rows,(dt,v,truth,abs(v-truth)))
end
savecsv("greenland_convergence.csv",["step_years","volume_m_sle","exact_m_sle","absolute_error_m"],rows)

d=cfg["diffusion"]; rows=[]
for n in d["cells"]
    dz=d["depth"]/n; dt=d["duration"]/n^2; z=((1:n).-0.5).*dz
    t=sin.(pi.*z./(2d["depth"])); maxbalance=0.
    for j in 1:n^2
        updated,flux=R.diffuse_step(t,0.,d["diffusivity"],dz,dt)
        maxbalance=max(maxbalance,abs(sum(updated-t)*dz-dt*flux)); t=updated
    end
    exact=sin.(pi.*z./(2d["depth"])).*exp(-d["diffusivity"]*(pi/(2d["depth"]))^2*d["duration"])
    push!(rows,(n,dt,maximum(abs.(t-exact)),maxbalance))
end
savecsv("diffusion_convergence.csv",["cells","step_s","max_error_k","max_balance_error_k_m"],rows)

f=cfg["flood"]
savecsv("flood_fixture.csv",["lower_m","upper_m","area_km2","capital_usd_km2","people_km2","vsl_usd","mortality","resilience"],[(f["band_edges"][i],f["band_edges"][i+1],f["band_areas"][i],f["capital_density"],f["population_density"],f["value_of_life"],f["mortality"],f["resilience"]) for i in eachindex(f["band_areas"])])
savecsv("gev_fixture.csv",["location_m","scale_m","shape","lower_m","upper_m"],[(f["gev_location"],f["gev_scale"],f["gev_shape"],f["surge_lower"],f["surge_upper"])])
dist=(location=f["gev_location"],scale=f["gev_scale"],shape=f["gev_shape"])
damage=w->R.flood_damage(w,f["band_edges"],f["band_areas"];min_elevation=0.,capital_density=f["capital_density"],population_density=f["population_density"],mortality=f["mortality"],value_of_life=f["value_of_life"],resilience=f["resilience"])
rows=[]
for n in [256,512,1024,2048,4096,8192]
    v=R.expected_flood_loss(damage,dist;lower=f["surge_lower"],upper=f["surge_upper"],panels=n)
    push!(rows,(n,v))
end
savecsv("flood_convergence.csv",["panels","expected_loss_usd_per_year"],rows)
savecsv("flood_damage.csv",["water_height_m","damage_usd"],[(h,damage(h)) for h in 0:.05:5])
rows=[]
for crest in 0.:.25:4.
    v=R.expected_flood_loss(damage,dist;lower=crest,upper=f["surge_upper"],panels=8192)
    push!(rows,(crest,v))
end
savecsv("protection_sensitivity.csv",["crest_m","expected_loss_usd_per_year"],rows)

a=cfg["anto"]
savecsv("anto_transform.csv",["temperature_c","ocean_temperature_c","freezing_c"],[(t,R.antarctic_ocean_temperature(t;a=a["a"],b=a["b"],freezing=a["freezing"]),a["freezing"]) for t in -8.:.02:4.])

# Manufactured two-period cost menu; no claim that these are actual coastal costs.
menu=[1. 9.;6. 2.]; years=[2010,2060]
fixed=R.choose_adaptation(menu,years)
revisable=R.present_value(vec(minimum(menu,dims=1)),years)
annual=R.present_value(ones(10),2010:2019)
savecsv("decision_sensitivity.csv",["quantity","value"],[("fixed_strategy_pv",fixed.value),("revisable_strategy_pv",revisable),("ten_annual_unit_payments_pv",annual),("ten_units_paid_at_start_pv",10.),("ten_units_paid_at_end_pv",10/1.04^9)])

# Published summary arithmetic only. The16 second-bin exceedances are derived
# from250 total minus125 highest minus109 third-bin minus0 lowest.
counts=[202,2264,2145,389]; tails=[0,16,109,125]; printed=[0,1,5,32]
savecsv("published_table_audit.csv",["bin","published_count","tail_count_audited","tail_percent_calculated","tail_percent_printed"],[(i,counts[i],tails[i],100tails[i]/counts[i],printed[i]) for i in 1:4])
println("Generated manufactured diagnostics and a separate printed-table arithmetic audit.")
