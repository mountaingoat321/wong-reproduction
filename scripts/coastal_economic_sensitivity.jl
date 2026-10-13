# Invoked by coastal_coupled_experiments.jl --economic-priors [--pilot].
# This conditional six-path sensitivity does not define a target joint ensemble.
using Random
function economic_sensitivity(years,coasts,economies,sealevel,design,members;pilot=false)
    started=time();rng=MersenneTwister(20251047);M=RecoveredModels
    prefix="coastal_economic"*(pilot ? "_pilot" : "")
    priors=M.SOCIO_PRIORS
    draws=vcat([[p.mean for p in priors]],[[M.truncated_normal(rng,p.mean,p.sd,p.lo,p.hi) for p in priors] for _ in 1:16])
    pilot && (draws=draws[1:3];members=members[1:2])
    # Four common positive-probability coast draws per region; separate from
    # the number of economic draws and climate paths.
    design=design[design[:,2].<=4,:]
    keys=sort(unique([(String(r[3]),String(r[4])) for r in eachrow(design)]))
    quad=G.quadrature(12);checks=[]
    function perturb(eco,p)
        income=eco.income./eco.income[1];density=eco.popscale./eco.popscale[1]
        merge(eco,(land=eco.land.*(p[2]/5.376),
            wetland=eco.wetland.*income.^(p[4]-1.16).*density.^(p[3]-.47)))
    end
    open("results/"*prefix*"_parameters.csv","w") do io
        println(io,"economic_sample,"*join([p.name for p in priors],","))
        for (j,p) in enumerate(draws);println(io,join((j-1,p...),","));end
    end
    central=Dict()
    open(".local/"*prefix*"_cases.csv","w") do io
        println(io,"economic_sample,sample,coast_id,country,incremental_pv_USD2019PPP,difference_from_central_USD2019PPP,strategy,return_period")
        for (j,p) in enumerate(draws)
            ec=Dict(c=>perturb(e,p) for (c,e) in economies)
            kw=(movefactor=p[1],vslel=p[5],vslmult=p[6])
            baseline=Dict()
            for key in keys
                b=G.choose_path(years,zeros(length(years)),ec[key[2]],coasts[key];quad=quad,kw...)
                baseline[key]=R.present_value(b.path.total,years)
            end
            for (mi,member) in enumerate(members), (ki,key) in enumerate(keys)
                result=G.choose_path(years,sealevel[member],ec[key[2]],coasts[key];quad=quad,kw...)
                pv=R.present_value(result.path.total,years);inc=pv-baseline[key]
                if j==1;central[(member,key)]=inc;end
                delta=inc-central[(member,key)]
                println(io,join((j-1,member,key...,inc,delta,result.candidate.strategy,result.candidate.return_period),","))
                if mi<=2 && ki<=2
                    fine=G.choose_path(years,sealevel[member],ec[key[2]],coasts[key];quad=G.quadrature(24),kw...)
                    finepv=R.present_value(fine.path.total,years)
                    rel=abs(finepv-pv)/max(1.,abs(pv));same=fine.choice==result.choice
                    @assert rel<1e-6 && same
                    push!(checks,(j-1,member,key...,rel,same))
                end
            end
            flush(io);println("Economic draw ",j-1,"/",length(draws)-1," across ",length(members)," purpose paths; elapsed ",round(time()-started,digits=1));flush(stdout)
        end
    end
    # At the declared central parameters the experiment must exactly recover
    # the corresponding independently saved base-pilot coastal costs.
    reference=readdlm(".local/coastal_coupled_pilot_cases.csv",',',Any;skipstart=1)
    differences=Float64[]
    for row in eachrow(reference)
        key=(Int(row[1]),(String(row[2]),String(row[3])))
        haskey(central,key) || continue
        push!(differences,abs(central[key]-Float64(row[6]))/max(1.,abs(Float64(row[6]))))
    end
    @assert length(differences)==length(members)*length(keys) && maximum(differences)<1e-10
    open("results/"*prefix*"_refinement.csv","w") do io
        println(io,"economic_sample,sample,coast_id,country,relative_quadrature_difference,same_policy")
        for row in checks;println(io,join(row,","));end
    end
    open("results/"*prefix*"_run.toml","w") do io
        TOML.print(io,Dict("seed"=>20251047,"economic_draws"=>length(draws)-1,"purpose_paths"=>length(members),
            "unique_coasts"=>length(keys),"draws_per_region"=>4,"wall_seconds"=>time()-started,
            "maximum_central_recovery_relative_difference"=>maximum(differences),
            "scope"=>"NON-REPRODUCTION: independent marginal socioeconomic priors; fixed six purpose paths and alternative geography",
            "assumptions"=>"Independent six marginal truncated normals; movefactor/VSL direct; dvbm scales existing land values relative5.376; wetland elasticities perturb post2010 income/density growth relative provider baseline; initial wetland values unchanged",
            "raw_cases"=>".local/"*prefix*"_cases.csv","completed"=>true))
    end
end
