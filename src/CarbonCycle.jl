module CarbonCycle
using LinearAlgebra
using ..RecoveredModels: bisect, global_temperature

"""Alternative closure combining S87 land pools, R08 feedbacks, T08 ocean
transport, and H99 carbonate chemistry. It is not a recovered W25 calibration.
Carbon is Gt C; time yr; concentration ppm; temperature anomaly K.
"""
function parameters(;beta=0.287,q10=2.0,exchange=19.30)
    c0=280.0; ppm_per_gtc=0.471; solubility=2.988e7
    k1=9.952e-7; k2=7.076e-10; kb=1.881e-9; kw=6.463e-15
    boron=4.09e-4; alk=2.434e-3
    h0=exp(bisect(logh->begin
        h=exp(logh)
        c0/solubility*(k1/h+2k1*k2/h^2)+boron/(1+h/kb)+kw/h-h-alk
    end,log(1e-11),log(1e-5);xtol=1e-12))
    dic0=c0/solubility*(1+k1/h0+k1*k2/h0^2)
    # m2 * m * 1000 L/m3 * 12 g/mol / 1e15 g/Gt = Gt/(mol/L).
    conversion=3.62e14*73.0*12e-12
    (beta=beta,q10=q10,depths=[73.0,479.0,1299.0,2723.0],
     exchange=[exchange,10.33,7.23],c0=c0,ppm_per_gtc=ppm_per_gtc,
     solubility=solubility,k1=k1,k2=k2,kb=kb,kw=kw,boron=boron,
     alk=alk,dic0=dic0,conversion=conversion,hydrogen0=h0,
     combined0=c0/ppm_per_gtc+conversion*dic0)
end

"""Atmosphere--mixed-ocean instantaneous chemical equilibrium at fixed
alkalinity, salinity, and temperature. Combined perturbation includes BOTH.
No finite air--sea gas-exchange time is represented.
"""
function partition(perturbation,p)
    total=p.combined0+perturbation
    total>0 || throw(DomainError(total))
    co2(h)=total/(1/p.ppm_per_gtc+p.conversion/p.solubility*(1+p.k1/h+p.k1*p.k2/h^2))
    residual(logh)=begin
        h=exp(logh)
        co2(h)/p.solubility*(p.k1/h+2p.k1*p.k2/h^2)+
            p.boron/(1+h/p.kb)+p.kw/h-h-p.alk
    end
    h=exp(bisect(residual,log(1e-11),log(1e-5);xtol=1e-12))
    concentration=co2(h)
    atmosphere=(concentration-p.c0)/p.ppm_per_gtc
    (co2=concentration,atmosphere=atmosphere,mixed=perturbation-atmosphere,hydrogen=h)
end

initial_state()=[0.0,0.0,0.0,0.0,100.0,500.0,120.0,1500.0]

function rhs(x,emissions,temperature,p)
    length(x)==8 || throw(DimensionMismatch())
    all(x[5:8].>=0) || throw(DomainError(x[5:8],"negative terrestrial carbon"))
    part=partition(x[1],p)
    npp=60*(1+p.beta*log(part.co2/p.c0))
    npp>=0 || throw(DomainError(npp))
    q=p.q10^(temperature/10)
    leaf,wood,detritus,soil=x[5:8]
    respiration=q*(45/120*detritus+15/1500*soil)
    concentrations=vcat(part.mixed,x[2:4])./p.depths
    flux=p.exchange.*(concentrations[1:3]-concentrations[2:4])
    [emissions-npp+respiration-flux[1],flux[1]-flux[2],flux[2]-flux[3],flux[3],
     35/60*npp-35/100*leaf,25/60*npp-25/500*wood,
     35/100*leaf+20/500*wood-(45/120*q+10/120)*detritus,
     5/500*wood+10/120*detritus-15/1500*q*soil]
end

function carbon_step(x,emissions,temperature,p,h)
    f(z)=rhs(z,emissions,temperature,p)
    a=f(x);b=f(x+h*a/2);c=f(x+h*b/2);d=f(x+h*c)
    x+h/6*(a+2b+2c+d)
end

"""Second-order Strang splitting: half climate CN, full carbon RK4 at
midpoint temperature, half climate CN. Emissions and external forcing are
linearly interpolated. Zero-anomaly climate and steady land pools at start.
Non-CO2 forcing must exclude CO2 already calculated from carbon concentration.
"""
function coupled_run(sys,emissions,nonco2;p=parameters(),substeps=8,
                     carbon_initial=initial_state(),climate_initial=zeros(length(sys.forcing)))
    length(emissions)==length(nonco2) || throw(DimensionMismatch())
    substeps>=1 || throw(DomainError(substeps))
    h=1/substeps; lhs=factorize(I-h/4*sys.A); right=I+h/4*sys.A
    carbon=zeros(8,length(emissions));climate=zeros(length(sys.forcing),length(emissions))
    x=copy(carbon_initial);t=copy(climate_initial);carbon[:,1]=x;climate[:,1]=t
    for i in 2:length(emissions)
        for j in 1:substeps
            fraction=(j-0.5)/substeps
            e=emissions[i-1]+fraction*(emissions[i]-emissions[i-1])
            q1=nonco2[i-1]+(j-0.75)/substeps*(nonco2[i]-nonco2[i-1])
            q2=nonco2[i-1]+(j-0.25)/substeps*(nonco2[i]-nonco2[i-1])
            forcing=3.7*log2(partition(x[1],p).co2/p.c0)
            t=lhs\(right*t+h/2*(q1+forcing)*sys.forcing)
            x=carbon_step(x,e,global_temperature(sys,t),p,h)
            forcing=3.7*log2(partition(x[1],p).co2/p.c0)
            t=lhs\(right*t+h/2*(q2+forcing)*sys.forcing)
        end
        carbon[:,i]=x;climate[:,i]=t
    end
    (carbon=carbon,climate=climate)
end
end
