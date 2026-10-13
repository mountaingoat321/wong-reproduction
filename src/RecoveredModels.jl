module RecoveredModels

using LinearAlgebra, Random

# Independently transcribed mathematics, not a port of any existing software.
# Provenance, corrections and limits: docs/RECOVERED_SPECIFICATIONS.md.
const SECONDS_PER_YEAR = 365.25*86400

"""DOECLIM equations 2.3.8--16 and Table 2.3, Tanaka (2008).
States: land air, ocean surface, then cell-centred interior ocean anomalies (K).
Time: yr; forcing: W/m²; diffusivity input: cm²/s. Bottom is insulated.
Finite volumes replace the published analytical diffusion series.
"""
function climate_system(;ecs=3.0, diffusivity=0.55, cells=80, depth=4000.0)
    ecs > 0 && diffusivity >= 0 && cells >= 2 && depth > 0 || throw(DomainError(ecs))
    f=0.29; fs=0.95; b=1.3; ratio=1.43; cl=0.52; cs=7.8; cv=0.13
    tl=ratio*ecs/(ratio*f+(1-f)*b); ts=tl/ratio
    delta=1-b/ratio
    lambda_l=(3.7/tl-1.59*delta/f)/(1-0.31*delta/f)
    exchange=1.59-0.31*lambda_l
    exchange >= 0 || throw(DomainError(ecs,"negative calibrated land-ocean exchange"))
    lambda_s=3.7/ts+exchange/(1-f)*(ratio-b)
    dz=depth/cells; kap=diffusivity*1e-4*SECONDS_PER_YEAR
    d=zeros(cells+2); lo=zeros(cells+1); hi=zeros(cells+1)
    d[1]=-(lambda_l+exchange/f)/cl; hi[1]=exchange*b/(f*cl)
    lo[1]=exchange/((1-f)*cs)
    d[2]=-(lambda_s+exchange*b/(1-f)+2fs*cv*kap/dz)/cs
    hi[2]=2fs*cv*kap/(dz*cs)
    lo[2]=2kap/dz^2; d[3]=-3kap/dz^2; hi[3]=kap/dz^2
    for i in 4:cells+2
        lo[i-1]=kap/dz^2
        d[i]=-(i==cells+2 ? 1 : 2)*kap/dz^2
        i<cells+2 && (hi[i]=kap/dz^2)
    end
    forcing=zeros(cells+2); forcing[1]=1/cl; forcing[2]=1/cs
    mass=vcat(f*cl,(1-f)*cs,fill((1-f)*fs*cv*dz,cells))
    (A=Tridiagonal(lo,d,hi),forcing=forcing,mass=mass,land_fraction=f,
     ocean_fraction=fs,marine_air_factor=b,cv=cv,dz=dz,
     lambda_land=lambda_l,lambda_sea=lambda_s,exchange=exchange,
     equilibrium_land=tl,equilibrium_sea=ts)
end

global_temperature(sys,x)=sys.land_fraction*x[1]+(1-sys.land_fraction)*sys.marine_air_factor*x[2]

"""Exact modal propagation of the finite-volume climate ODE for forcing linear
between annual nodes. Positive off-diagonals admit a diagonal similarity to a
symmetric tridiagonal matrix. Projects directly to SAT and water heat; it does
not approximate the physical eigenmodes or truncate their number.
"""
function climate_observables(sys,forcing;depths=(700.0,2000.0,4057.5))
    a=sys.A; n=length(a.d)
    all(a.dl.>0) && all(a.du.>0) || throw(DomainError(a,"modal solver requires positive exchanges"))
    scale=vcat(1.0,cumprod(sqrt.(a.du./a.dl)))
    eig=eigen(SymTridiagonal(a.d,sqrt.(a.dl.*a.du)))
    lambda=eig.values; v=eig.vectors
    input=v'*(scale.*sys.forcing)
    decay=exp.(lambda)
    left=similar(lambda);right=similar(lambda)
    for i in eachindex(lambda)
        z=lambda[i]
        # Series avoid cancellation for the slow deep-ocean modes.
        if abs(z)<1e-3
            right[i]=1/2+z/6+z^2/24+z^3/120+z^4/720
            left[i]=1/2+z/3+z^2/8+z^3/30+z^4/144
        else
            right[i]=(expm1(z)-z)/z^2
            left[i]=(z*exp(z)-expm1(z))/z^2
        end
    end
    weights=zeros(1+length(depths),n)
    weights[1,1]=sys.land_fraction
    weights[1,2]=(1-sys.land_fraction)*sys.marine_air_factor
    for (j,depth) in enumerate(depths)
        weights[j+1,2]=min(depth,57.5)
        for i in 1:n-2
            weights[j+1,i+2]=sys.ocean_fraction*clamp(depth-57.5-(i-1)*sys.dz,0.0,sys.dz)
        end
        weights[j+1,:].*=3.62e14*SECONDS_PER_YEAR*sys.cv/1e22
    end
    projection=(weights./scale')*v
    out=zeros(size(weights,1),length(forcing));z=zeros(n)
    for t in 2:length(forcing)
        @. z=decay*z+input*(left*forcing[t-1]+right*forcing[t])
        mul!(view(out,:,t),projection,z)
    end
    (temperature=vec(out[1,:]),heat=out[2:end,:],final_state=(v*z)./scale)
end

"""Effective ocean-column heat in J; includes the atmospheric-equivalent part
of the published 60 m mixed-layer heat capacity. It is explicitly a heat proxy.
Use mixed_depth=57.5 to examine exclusion of its ~2.5 m atmospheric equivalent.
"""
function ocean_heat(sys,x; area=3.62e14,mixed_depth=60.0)
    area*SECONDS_PER_YEAR*sys.cv*(mixed_depth*x[2]+sys.ocean_fraction*sys.dz*sum(x[3:end]))
end

"""Heat in the water column above a specified physical depth. The 57.5 m
water-only mixed layer is followed by finite-volume interior cells; partial
cells contribute by overlap. Excludes the 2.5 m atmospheric heat equivalent.
"""
function ocean_heat_to_depth(sys,x,depth;area=3.62e14,mixed_depth=57.5)
    depth>=0 || throw(DomainError(depth))
    heat=min(depth,mixed_depth)*x[2]
    for i in 1:length(x)-2
        width=clamp(depth-mixed_depth-(i-1)*sys.dz,0.0,sys.dz)
        heat+=sys.ocean_fraction*width*x[i+2]
    end
    area*SECONDS_PER_YEAR*sys.cv*heat
end

"""Crank--Nicolson, uniform time grid and linear forcing between saved nodes.
Returns all states; initial anomaly defaults to zero. No calibration implied.
"""
function climate_run(sys,forcing;dt=1.0,substeps=4,initial=zeros(length(sys.forcing)))
    dt>0 && substeps>=1 || throw(DomainError(dt))
    h=dt/substeps; n=length(initial)
    out=zeros(n,length(forcing)); out[:,1]=initial
    lhs=factorize(I-h/2*sys.A); rhs=I+h/2*sys.A
    x=copy(initial)
    for t in 2:length(forcing)
        for j in 1:substeps
            q=forcing[t-1]+(forcing[t]-forcing[t-1])*(j-0.5)/substeps
            x=lhs\(rhs*x+h*q*sys.forcing)
        end
        out[:,t]=x
    end
    out
end

"""S14 Table 1. Units corrected by dimensions: mu in m, flow0 in yr^-1.
gamma=2, alpha=.35 is S14 case 4; not a target posterior estimate.
"""
dais_parameters(;gamma=2.0,alpha=0.35)=(bed=775.0,slope=6e-4,mu=8.7,
    h0=1471.0,c=95.0,precip0=0.35,kappa=0.04,nu=0.012,flow0=1.2,
    gamma=gamma,alpha=alpha,freezing=-1.8,ocean0=0.72,radius0=1.864e6,
    rhoi=917.0,rhow=1030.0,rhom=4000.0)

ice_surface(r,radius,p)=p.bed-p.slope*radius+sqrt(p.mu*(radius-r))

"""S14 Eq.13 and its independently differentiated partial derivatives.
The printed volume expression retains b0, not b0-SL, in the marine term.
"""
function dais_geometry(radius,sea,p=dais_parameters())
    radius>0 || throw(DomainError(radius))
    e1=p.rhoi/(p.rhom-p.rhoi); e2=p.rhow/(p.rhom-p.rhoi)
    rc=(p.bed-sea)/p.slope
    rc>=0 || throw(DomainError(sea,"sea level above continent centre outside reconstruction domain"))
    volume=pi*(1+e1)*(8/15*sqrt(p.mu)*radius^2.5-p.slope*radius^3/3)
    dr=pi*(1+e1)*(4/3*sqrt(p.mu)*radius^1.5-p.slope*radius^2)
    ds=0.0
    if radius>rc
        volume-=pi*e2*(2p.slope/3*(radius^3-rc^3)-p.bed*(radius^2-rc^2))
        dr-=2pi*e2*(p.slope*radius^2-p.bed*radius)
        ds=-2pi*e2*(rc^2-p.bed/p.slope*rc)
    end
    volume>0 && dr>0 || throw(DomainError(radius,"nonpositive volume or radius derivative"))
    (volume=volume,dr=dr,ds=ds,coast_radius=rc)
end

function dais_accumulation(radius,air,p=dais_parameters();runoff_rule=:paper,runoff_active=nothing)
    precipitation=p.precip0*exp(p.kappa*air)
    gradient=p.nu*sqrt(precipitation); line=p.h0+p.c*air
    edge=p.bed-p.slope*radius
    active=runoff_rule==:paper ? line>0 : runoff_rule==:local_height ? line>edge :
        throw(ArgumentError("unknown runoff rule"))
    # One-sided endpoint evaluation when a time step ends at a known event.
    runoff_active!==nothing && (active=runoff_active)
    !active && return pi*precipitation*radius^2
    # Clipping the intersection to the physical disk is a geometric extension
    # for wholly ablating/accumulating disks, not a parameter adjustment.
    width=min(radius,max(0.0,line-edge)^2/p.mu)
    rr=radius-width
    pi*precipitation*radius^2-pi*gradient*(line-edge)*(radius^2-rr^2)+
        4pi*gradient*sqrt(p.mu)*(radius*width^1.5/3-width^2.5/5)
end

function dais_discharge(radius,sea,ocean,p=dais_parameters())
    # Water depth = sea level minus bed height: sign follows S14 Eq.1.
    depth=p.slope*radius-p.bed+sea
    depth<=0 && return 0.0
    reference=p.slope*p.radius0-p.bed
    reference>0 || throw(DomainError(reference))
    speed=p.flow0*((1-p.alpha)+p.alpha*((ocean-p.freezing)/(p.ocean0-p.freezing))^2)*
        depth^p.gamma/reference^(p.gamma-1)
    -2pi*radius*p.rhow/p.rhoi*depth*speed
end

function dais_radius_rhs(radius,air,sea,sea_rate,ocean,p=dais_parameters();
                         fast_loss_m_per_year=0.0,ocean_area=3.62e14,runoff_rule=:paper,runoff_active=nothing)
    geom=dais_geometry(radius,sea,p)
    loss_volume=fast_loss_m_per_year*ocean_area*p.rhow/p.rhoi
    (dais_accumulation(radius,air,p;runoff_rule=runoff_rule,runoff_active=runoff_active)+
     dais_discharge(radius,sea,ocean,p)-loss_volume-geom.ds*sea_rate)/geom.dr
end

"""Bisection for a sign-changing scalar residual; used for equilibrium and
nonlinear mass partition, not to match published projection output.
"""
function bisect(f,lo,hi;xtol=1e-8,iterations=150)
    fl=f(lo); fh=f(hi)
    fl==0 && return lo; fh==0 && return hi
    fl*fh<0 || throw(ArgumentError("root not bracketed"))
    for j in 1:iterations
        mid=(lo+hi)/2; fm=f(mid)
        (hi-lo<=xtol || fm==0) && return mid
        if signbit(fm)==signbit(fl); lo=mid; fl=fm; else; hi=mid; end
    end
    error("bisection failed to converge")
end

const SOCIO_PRIORS=(
    (name="movefactor",mean=1.0,sd=1.0,lo=0.5,hi=3.0),
    (name="dvbm",mean=5.376,sd=2.688,lo=0.0,hi=Inf),
    (name="wvpdl",mean=0.47,sd=0.12,lo=0.0,hi=1.0),
    (name="wvel",mean=1.16,sd=0.46,lo=0.0,hi=Inf),
    (name="vslel",mean=0.47,sd=0.15,lo=0.0,hi=Inf),
    (name="vslmult",mean=200.0,sd=100.0,lo=0.0,hi=Inf))

function truncated_normal(rng,mu,sd,lo,hi)
    sd>0 && lo<hi || throw(DomainError(sd))
    while true
        x=mu+sd*randn(rng)
        lo<=x<=hi && return x
    end
end

adaptation_menu()=vcat([(strategy=:none,return_period=0)],
    [(strategy=:protect,return_period=r) for r in (10,100,1000,10000)],
    [(strategy=:retreat,return_period=r) for r in (1,10,100,1000,10000)])

function annual_high_tide(dinas_one,dinas_hundred,gtsr_hundred)
    dinas_hundred>0 && min(dinas_one,gtsr_hundred)>=0 || throw(DomainError(dinas_hundred))
    dinas_one*gtsr_hundred/dinas_hundred
end

end
