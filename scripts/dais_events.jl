using TOML
include("../src/RecoveredModels.jl")
const M=RecoveredModels
p=M.dais_parameters()
req=M.bisect(r->M.dais_radius_rhs(r,-18.,0.,0.,.72,p),1.5e6,2.1e6)
v0=M.dais_geometry(req,0.,p).volume
function run_case(warming,dt)
    air(t)=-18.0+warming*min(t/100,1)
    event=warming==0 ? Inf : 100*(-p.h0/p.c+18)/warming
    breaks=sort(unique(vcat(collect(0.:dt:200.),[100.],[event for k in 1:1 if 0<event<200])))
    radius=req;rows=[]
    for i in 1:length(breaks)-1
        t=breaks[i];h=breaks[i+1]-t
        active=p.h0+p.c*air(t+h/2)>0
        f(tt,r)=M.dais_radius_rhs(r,air(tt),0.,0.,.72,p;runoff_active=active)
        k1=f(t,radius);k2=f(t+h/2,radius+h*k1/2)
        k3=f(t+h/2,radius+h*k2/2);k4=f(t+h,radius+h*k3)
        radius+=h/6*(k1+2k2+2k3+k4)
        tt=breaks[i+1]
        if isinteger(tt)
            v=M.dais_geometry(radius,0.,p).volume
            push!(rows,(warming,tt,radius,(v0-v)*p.rhoi/p.rhow/3.62e14))
        end
    end
    radius,rows,event
end
open("results/dais_event_convergence.csv","w") do io
    println(io,"step_years,radius_200_m,volume_200_1e15m3,event_year")
    for dt in (2.,1.,.5,.25,.125)
        r,_,event=run_case(6.,dt)
        println(io,join((dt,r,M.dais_geometry(r,0.,p).volume/1e15,event),","))
    end
end
open("results/dais_event_warming.csv","w") do io
    println(io,"antarctic_warming_K,year,radius_m,mass_equivalent_sea_level_m")
    for warming in (0.,2.,4.,6.)
        _,rows,_=run_case(warming,.25)
        println(io,join((warming,0,req,0),","))
        for row in rows;println(io,join(row,","));end
    end
end
println("DAIS known runoff event resolved with one-sided stage evaluations.")
