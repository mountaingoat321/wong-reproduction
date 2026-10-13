module SeaLevelCoupling
using ..PaleoDAIS
const D=PaleoDAIS

"""Antarctic volume driven by other sea-level components and shore feedback.
All inputs share calendar-year knots. `other` is change in metres from the
first knot. B17 Sect3.3 specifies shore factors -1 for AIS and +1 for others.
Continuous feedback is a derived coupling; lagged forcing is a separate
annual-input alternative motivated by B17 Sect3.2.3. Neither asserts recovery
of the original integrator. Volume is measured in 1e15m3.
"""
function antarctic_path(years,air,ocean,other;initial_radius,initial_sea,
                        p=D.M.dais_parameters(),lambda=0.,threshold=-15.,
                        fingerprint=-1.,dt=.25,mode=:continuous)
    n=length(years)
    n==length(air)==length(ocean)==length(other) || throw(DimensionMismatch())
    all(diff(years).>0) && dt>0 || throw(ArgumentError("invalid time grid"))
    mode in (:continuous,:lagged) || throw(ArgumentError("unknown coupling"))
    abs(other[1])<1e-10 || throw(ArgumentError("other components must start at zero"))
    v0=D.M.dais_geometry(initial_radius,initial_sea,p).volume/1e15
    v=zeros(n);v[1]=v0
    for j in 1:n-1
        duration=years[j+1]-years[j]
        interp(x,t)=x[j]+(x[j+1]-x[j])*t/duration
        breaks=[0.,duration]
        if mode==:continuous
            for gate in (-p.h0/p.c,threshold)
                if (air[j]-gate)*(air[j+1]-gate)<0
                    push!(breaks,duration*(gate-air[j])/(air[j+1]-air[j]))
                end
            end
        end
        sort!(breaks);value=v[j]
        for k in 1:length(breaks)-1
            left,right=breaks[k:k+1]
            temperature(t)=mode==:continuous ? interp(air,t) : air[j]
            subsurface(t)=mode==:continuous ? interp(ocean,t) : ocean[j]
            sea(t,x)=initial_sea+(mode==:continuous ? interp(other,t)+fingerprint*(v0-x)*D.SLE_PER_VOLUME :
                                      other[j]+fingerprint*(v0-v[j])*D.SLE_PER_VOLUME)
            runoff=p.h0+p.c*temperature((left+right)/2)>0
            fast=lambda>0 && temperature((left+right)/2)>threshold
            function slow(t,x)
                level=sea(t,x);r=D.radius_from_volume(x,level,p)
                (D.M.dais_accumulation(r,temperature(t),p;runoff_active=runoff)+
                 D.M.dais_discharge(r,level,subsurface(t),p))/1e15
            end
            count=ceil(Int,(right-left)/dt);h=(right-left)/count
            for step in 1:count
                value=D.cutoff_step(slow,left+(step-1)*h,value,h,fast ? lambda/D.SLE_PER_VOLUME : 0.)
            end
        end
        v[j+1]=value
    end
    ais=(v0.-v).*D.SLE_PER_VOLUME
    (volume=v,antarctic=ais,shore=initial_sea.+other.+fingerprint.*ais)
end

"""Explicit normal-rate LWS alternatives with mean .30 and SD .18 mm/yr.
The covariance convention is an assumption: independent annual rates versus
a single uncertain rate shared by every future year. Inputs are standard
normal variates; output starts at zero and sums annual rates, in metres.
"""
function landwater(z;mode=:independent,mean_rate=.00030,sd_rate=.00018)
    mode in (:independent,:common) || throw(ArgumentError("unknown rate covariance"))
    rates=mean_rate.+sd_rate.*(mode==:common ? fill(z[1],length(z)) : z)
    vcat(0.,cumsum(rates))
end
end
