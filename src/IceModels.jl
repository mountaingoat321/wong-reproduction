module IceModels
using ..Reproduction
const R=Reproduction

"""Exact GIC solution for linearly interpolated annual temperature.
Temperature is relative to 1850--1870; sea-level volume in m. The origin of
S0 is set explicitly by the caller. Extinction is absorbing; no ice is regrown
after zero volume. This convention resolves the nonunique n<1 boundary.
"""
function glaciers(temperature,beta,volume,exponent,initial)
    0<=beta && volume>=initial && volume>0 && 0<exponent<=1 || throw(DomainError(volume))
    s=zeros(length(temperature));s[1]=initial
    for i in 2:length(s)
        if s[i-1]>=volume;s[i]=volume;continue;end
        integral=(temperature[i-1]+temperature[i])/2+.15
        if exponent==1
            s[i]=volume-(volume-s[i-1])*exp(-beta/volume*integral)
        else
            power=1-exponent
            start=(1-s[i-1]/volume)^power
            u0=temperature[i-1]+.15;u1=temperature[i]+.15
            maximum_integral=max(0.,integral,u0>0 && u1<0 ? -u0^2/(2*(u1-u0)) : 0.)
            if start-power*beta/volume*maximum_integral<=0
                s[i]=volume;continue
            end
            x=start-power*beta/volume*integral
            s[i]=x<=0 ? volume : volume*(1-x^(1/power))
        end
    end
    s
end

"""SIMPLE Greenland change relative to the caller's initial year.
d=V0-b and k=-c expose an exact non-identifiability of V0 and b in rate data.
a and b are inverse-response coefficients in units 0.001/yr/K and 0.001/yr.
Temperature is relative to 1961--1990. Four RK4 steps per year by default.
"""
function greenland(temperature,d,k,a,b;substeps=4,initial=0.0)
    min(k,a,b)>=0 || throw(DomainError(k))
    minimum(a.*temperature.+b)>=0 || throw(DomainError(b,"negative relaxation rate"))
    s=zeros(length(temperature));s[1]=initial;h=1/substeps
    for i in 2:length(s)
        x=s[i-1]
        rhs=(u,v)->(d+k*(temperature[i-1]+u*(temperature[i]-temperature[i-1]))-v)*
                   .001*(a*(temperature[i-1]+u*(temperature[i]-temperature[i-1]))+b)
        for j in 0:substeps-1
            t=j*h;v1=rhs(t,x);v2=rhs(t+h/2,x+h*v1/2)
            v3=rhs(t+h/2,x+h*v2/2);v4=rhs(t+h,x+h*v3)
            x+=h/6*(v1+2v2+2v3+v4)
        end
        s[i]=x
    end
    s
end

"""Induced prior density of V0-b for independent B17 uniforms:
V0 in [7.16,7.56]m and b in [5.888,8.832]m. No posterior table values used.
"""
function greenland_difference_prior(d)
    max(0.,min(7.56,8.832+d)-max(7.16,5.888+d))/(.4*2.944)
end
end
