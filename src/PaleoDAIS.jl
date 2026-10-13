module PaleoDAIS
include("RecoveredModels.jl")
const M=RecoveredModels
const SLE_PER_VOLUME=57/24.78 # m per 1e15m3, S14 p1810
ocean_temperature(air)=0.00690air^2+0.439air+6.39 # S14 Eq15

"""Invert the verified S14 volume geometry. Volume is in 1e15m3.
Newton iterations are numerical choices, not fitted physical parameters.
"""
function radius_from_volume(v,sea,p=M.dais_parameters();guess=p.radius0)
    v>0 || throw(DomainError(v,"ice volume must remain positive"))
    radius=guess
    for j in 1:30
        g=M.dais_geometry(radius,sea,p)
        residual=g.volume/1e15-v
        abs(residual)<1e-11 && return radius
        change=residual/(g.dr/1e15)
        radius-=clamp(change,-radius/2,radius/2)
    end
    error("Antarctic volume inversion did not converge")
end

rk4(f,t,v,h)=begin
    a=f(t,v);b=f(t+h/2,v+h*a/2);c=f(t+h/2,v+h*b/2);d=f(t+h,v+h*c)
    v+h*(a+2b+2c+d)/6
end

"""Resolve a constant fast-loss flux that switches off below a volume cutoff.
At the cutoff, opposing vector fields imply a sliding solution: fast loss
balances positive slow accumulation up to its maximum rate. This is an
explicit mathematical continuation of the discontinuous ODE, not recovered
author timestep logic. Slow dynamics may still take volume below the cutoff.
"""
function cutoff_step(f,t,v,h,loss;cutoff=18.,depth=0)
    loss==0 && return rk4(f,t,v,h)
    depth<35 || error("Unresolved fast-dynamics cutoff event")
    tolerance=1e-10
    if abs(v-cutoff)<=tolerance
        v=cutoff
        # Split any change of the boundary's attracting/sliding regime.
        for level in (0.,loss)
            g0=f(t,cutoff)-level;g1=f(t+h,cutoff)-level
            if g0*g1<0
                event=M.bisect(q->f(t+q,cutoff)-level,0.,h;xtol=1e-9)
                if 1e-7<event<h-1e-7
                    w=cutoff_step(f,t,v,event,loss;cutoff=cutoff,depth=depth+1)
                    return cutoff_step(f,t+event,w,h-event,loss;cutoff=cutoff,depth=depth+1)
                end
            end
        end
        middle=f(t+h/2,cutoff)
        0<=middle<=loss && return cutoff
        active=middle>loss
    else
        active=v>cutoff
    end
    rhs=(tt,x)->f(tt,x)-(active ? loss : 0.)
    final=rk4(rhs,t,v,h)
    if (v-cutoff)*(final-cutoff)<0 && abs(v-cutoff)>tolerance
        event=M.bisect(q->rk4(rhs,t,v,q)-cutoff,0.,h;xtol=1e-9)
        return cutoff_step(f,t+event,cutoff,h-event,loss;cutoff=cutoff,depth=depth+1)
    end
    final
end

"""Integrate with all forcing knots and known temperature gates resolved.
Input columns: CE year, Antarctic sea-level air temperature (degC), sea level
(m). The state is ice volume; prescribed sea level enters radius inversion.
This avoids numerical differentiation of the externally supplied sea level.
"""
function run(forcing,output_times;p=M.dais_parameters(),dt=10.,initial_radius=1.8636e6,
             lambda=0.,threshold=-15.,air_offset=0.,ocean_rule=:polynomial)
    dt>0 && lambda>=0 || throw(ArgumentError("invalid step or loss"))
    times=forcing[:,1];airs=forcing[:,2].+air_offset;seas=forcing[:,3]
    issorted(times) && all(diff(times).>0) || error("forcing knots must increase")
    out=sort(unique(Float64.(output_times)))
    times[1]<=out[1]<=out[end]<=times[end] || error("output beyond forcing")
    events=Float64[]
    for gate in (-p.h0/p.c,threshold), j in 1:length(times)-1
        if (airs[j]-gate)*(airs[j+1]-gate)<0
            push!(events,times[j]+(gate-airs[j])/(airs[j+1]-airs[j])*(times[j+1]-times[j]))
        end
    end
    breaks=sort(unique(vcat(times,out,events)))
    values=zeros(length(out));radii=similar(values);out_index=1;forcing_index=1
    v=M.dais_geometry(initial_radius,seas[1],p).volume/1e15
    if out[1]==times[1];values[1]=v;radii[1]=initial_radius;out_index+=1;end
    for j in 1:length(breaks)-1
        left=breaks[j];right=breaks[j+1]
        while forcing_index<length(times)-1 && times[forcing_index+1]<=left
            forcing_index+=1
        end
        k=forcing_index;slope_air=(airs[k+1]-airs[k])/(times[k+1]-times[k])
        slope_sea=(seas[k+1]-seas[k])/(times[k+1]-times[k])
        air(t)=airs[k]+slope_air*(t-times[k])
        sea(t)=seas[k]+slope_sea*(t-times[k])
        # One-sided endpoint evaluations preserve the branch on this interval.
        runoff=p.h0+p.c*air((left+right)/2)>0
        fast=lambda>0 && air((left+right)/2)>threshold
        ocean(t)=ocean_rule==:polynomial ? ocean_temperature(air(t)) :
            ocean_rule==:fixed ? p.ocean0 : throw(ArgumentError("unknown ocean rule"))
        function slow(t,x)
            r=radius_from_volume(x,sea(t),p)
            (M.dais_accumulation(r,air(t),p;runoff_active=runoff)+M.dais_discharge(r,sea(t),ocean(t),p))/1e15
        end
        n=ceil(Int,(right-left)/dt);h=(right-left)/n
        for step in 1:n
            v=cutoff_step(slow,left+(step-1)*h,v,h,fast ? lambda/SLE_PER_VOLUME : 0.)
        end
        if out_index<=length(out) && right==out[out_index]
            values[out_index]=v;radii[out_index]=radius_from_volume(v,sea(right),p);out_index+=1
        end
    end
    out_index==length(out)+1 || error("incomplete output")
    (time=out,volume=values,radius=radii)
end
end
