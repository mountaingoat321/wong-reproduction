using TOML,Statistics
include("../src/Reproduction.jl")
include("../src/RecoveredModels.jl")
include("../src/CoastalPaths.jl")
const C=CoastalPaths;const R=Reproduction
raw=TOML.parsefile("config/coastal_experiment.toml")
raw["gev"]=(;[Symbol(k)=>v for (k,v) in raw["gev"]]...)
segment=(;[Symbol(k)=>v for (k,v) in raw]...)
years=collect(2010:2150)
open("results/coastal_path_sensitivity.csv","w") do io
open("results/coastal_annual_paths.csv","w") do aio
    println(io,"income2010_USD,population_density2010_km2,sea2150_m,land_rule,maintenance_rule,strategy,return_period,total_pv_USD,no_adaptation_pv_USD,baseline_pv_USD,incremental_pv_USD,migrants_total,full_horizon_choice")
    println(aio,"income2010_USD,sea2150_m,year,strategy,return_period,construction_USD,maintenance_USD,retreat_USD,inundation_USD,wetland_USD,flood_USD,migrants,height_m,retreat_m")
    for (income0,density0) in ((5000.,20.),(15000.,200.),(40000.,2000.)),land in (:literal,:physical),maint in (:linear,:quadratic)
        # Stylized economic growth: an explicit scenario, not SSP country data.
        income=income0.*1.01.^(years.-2010);density=density0.*1.003.^(years.-2010)
        base=C.choose_path(years,zeros(141),income,density,segment;land_rule=land,maintenance_rule=maint)
        baseline=R.present_value(base.path.total,years)
        for high in (0.,.5,1.,2.)
            sea=high.*((years.-2010)./140).^1.5
            chosen=C.choose_path(years,sea,income,density,segment;land_rule=land,maintenance_rule=maint)
            pv=R.present_value(chosen.path.total,years);none=R.present_value(chosen.paths[1].total,years)
            full=argmin([R.present_value(p.total,years) for p in chosen.paths])
            println(io,join((income0,density0,high,land,maint,chosen.candidate.strategy,
                chosen.candidate.return_period,pv,none,baseline,pv-baseline,sum(chosen.path.migration),full),","))
            if land==:literal && maint==:linear
                for i in eachindex(years)
                    println(aio,join(vcat([income0,high,years[i],chosen.candidate.strategy,chosen.candidate.return_period],
                        vec(chosen.path.costs[i,:]),[chosen.path.migration[i],chosen.path.height[i],chosen.path.retreat[i]]),","))
                end
            end
        end
    end
end
end
open("results/coastal_quadrature_convergence.csv","w") do io
    println(io,"panels,total_pv_USD,choice")
    for panels in (128,256,512,1024)
        sea=2.0.*((years.-2010)./140).^1.5
        chosen=C.choose_path(years,sea,fill(15000.,141),fill(200.,141),segment;panels=panels)
        println(io,join((panels,R.present_value(chosen.path.total,years),chosen.choice),","))
    end
end
println("48 synthetic coastal scenarios completed; no global or observed segment costs inferred.")
