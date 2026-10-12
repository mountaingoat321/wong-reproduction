module Reproduction

using LinearAlgebra, Random, Statistics

# Scholarly equation provenance and domains: docs/SPECIFICATION.md.
# No parameter below is calibrated implicitly. Float64 numerical operators.

function emissions(firstyear::Int, lastyear::Int, q0, growth, peak::Int, decline)
    firstyear <= peak <= lastyear || throw(ArgumentError("peak must lie on the annual grid"))
    q0 >= 0 && growth >= 0 && decline > 0 || throw(DomainError((q0,growth,decline)))
    years = collect(firstyear:lastyear)
    q = zeros(length(years)); q[1] = q0
    for i in 2:length(years)
        t = years[i]
        if t <= peak
            q[i] = q[i-1] + growth*(peak-t)
        else
            # exp(-x) avoids overflow; algebraically identical to W25 Eq.1.
            u = exp(-decline*(t-peak))
            q[i] = q[i-1] - 2*q[peak-firstyear+1]*decline*u/(1+u)^2
        end
    end
    years, q
end

function co2_forcing(c, c0; doubling=3.7)
    c > 0 && c0 > 0 || throw(DomainError((c,c0)))
    doubling*log2(c/c0) # W/m2, U10
end

function npp(c, beta; baseline=60.0, c0=280.0)
    c > 0 && c0 > 0 || throw(DomainError((c,c0)))
    baseline*(1+beta*log(c/c0)) # Gt C/year, R08 Eq.2; not a carbon-cycle closure
end

function respiration(detritus, soil, a1, a2, q10, temperature)
    min(detritus,soil,a1,a2) >= 0 && q10 > 0 || throw(DomainError(q10))
    (a1*detritus+a2*soil)*q10^(temperature/10) # Gt C/year, R08 Eq.3
end

"""Cell-centred ocean diffusion: top Dirichlet, bottom zero flux; BE in seconds.
Returns new cell temperatures and top heat flux divided by volumetric heat capacity.
The latter has units K m/s, so sum(T)*dz changes by dt*flux exactly to roundoff.
"""
function diffuse_step(t::AbstractVector, surface, diffusivity, dz, dt)
    n = length(t)
    n >= 2 && dz > 0 && dt > 0 && diffusivity >= 0 || throw(ArgumentError("invalid column"))
    r = diffusivity*dt/dz^2
    d = fill(1+2r,n); d[1] = 1+3r; d[end] = 1+r
    rhs = Float64.(t); rhs[1] += 2r*surface
    updated = Tridiagonal(fill(-r,n-1),d,fill(-r,n-1)) \ rhs
    flux = 2diffusivity*(surface-updated[1])/dz
    updated, flux
end

function glacier_rhs(s, temperature; beta, equilibrium_temperature=-0.15, volume, exponent)
    volume > 0 && s <= volume && beta >= 0 && exponent > 0 || throw(DomainError(s))
    beta*(temperature-equilibrium_temperature)*(1-s/volume)^exponent
end

function greenland_rhs(v, temperature; c, b, alpha, beta)
    rate = alpha*temperature+beta
    rate >= 0 || throw(DomainError(rate,"negative inverse relaxation time"))
    (c*temperature+b-v)*rate
end

function rk4(f, y0, t0, dt, n::Int)
    dt > 0 && n >= 0 || throw(ArgumentError("invalid integration interval"))
    y = Float64(y0); out = [y]
    for j in 0:n-1
        t = t0+j*dt
        k1 = f(t,y); k2 = f(t+dt/2,y+dt*k1/2)
        k3 = f(t+dt/2,y+dt*k2/2); k4 = f(t+dt,y+dt*k3)
        y += dt*(k1+2k2+2k3+k4)/6
        isfinite(y) || error("nonfinite ODE state")
        push!(out,y)
    end
    out
end

thermal_expansion(heat_change, coefficient_m_per_joule) = heat_change*coefficient_m_per_joule

function antarctic_ocean_temperature(t; a, b, freezing=-1.8)
    a > 0 || throw(DomainError(a))
    x = a*t+b-freezing
    u = x/a
    sigmoid = u >= 0 ? 1/(1+exp(-u)) : exp(u)/(1+exp(u))
    freezing+x*sigmoid # B17 Eq.6, literal expression; no invented lower clamp
end

function fast_ice_loss(temperature; threshold, rate)
    rate >= 0 || throw(DomainError(rate))
    temperature > threshold ? rate : zero(rate) # m SLE/year, extra contribution only
end

function accumulate_storage(increments, initial)
    initial .+ cumsum(increments) # annual increments supplied, never inferred
end

function local_sea_level(fingerprints, components, relative_land_trend, years, baseyear)
    size(fingerprints,2) == size(components,1) || throw(DimensionMismatch("components"))
    size(components,2) == length(years) || throw(DimensionMismatch("years"))
    size(fingerprints,1) == length(relative_land_trend) || throw(DimensionMismatch("sites"))
    fingerprints*components + relative_land_trend*transpose(years .- baseyear)
end

function rebase(years, values, lo::Int, hi::Int)
    length(years) == length(values) || throw(DimensionMismatch())
    issorted(years) && all(diff(years) .== 1) || throw(ArgumentError("complete annual grid required"))
    idx = findall(y -> lo <= y <= hi, years)
    lo <= hi && length(idx) == hi-lo+1 || throw(ArgumentError("incomplete reference window"))
    values .- mean(values[idx])
end

function gev_cdf(x; location, scale, shape)
    scale > 0 || throw(DomainError(scale))
    z = (x-location)/scale
    shape == 0 && return exp(-exp(-z))
    u = 1+shape*z
    u <= 0 && return shape > 0 ? 0.0 : 1.0
    exp(-u^(-1/shape))
end

function gev_pdf(x; location, scale, shape)
    scale > 0 || throw(DomainError(scale))
    z = (x-location)/scale
    if shape == 0
        z < -700 && return 0.0
        return exp(-z-exp(-z))/scale
    end
    u = 1+shape*z
    u <= 0 && return 0.0 # endpoint itself has zero measure in the expectation
    lt = -log(u)/shape
    lt > 700 && return 0.0
    exp((shape+1)*lt-exp(lt))/scale
end

function gev_quantile(p; location, scale, shape)
    0 < p < 1 && scale > 0 || throw(DomainError(p))
    shape == 0 ? location-scale*log(-log(p)) : location+scale*expm1(-shape*log(-log(p)))/shape
end

function simpson(f, a, b, n::Int)
    iseven(n) && n >= 2 && b >= a || throw(ArgumentError("even panel count and ordered bounds required"))
    a == b && return 0.0
    h = (b-a)/n; total = f(a)+f(b)
    for j in 1:n-1
        total += (isodd(j) ? 4 : 2)*f(a+j*h)
    end
    h*total/3
end

"""D16 Eq.11 inner integral; USD/event, area km2, elevation m.
Only retained land from min_elevation upward is exposed. For protected land,
the caller supplies its crest as the lower outer integration threshold.
"""
function flood_damage(water, edges, areas; min_elevation, capital_density,
                      population_density, mortality, value_of_life, resilience,
                      depth_scale=1.0)
    length(edges) == length(areas)+1 || throw(DimensionMismatch())
    all(diff(edges) .> 0) && all(areas .>= 0) || throw(ArgumentError("invalid hypsometry"))
    0 <= resilience <= 1 && depth_scale > 0 || throw(DomainError(resilience))
    min(capital_density,population_density,mortality,value_of_life) >= 0 || throw(DomainError(capital_density))
    damage = 0.0
    for j in eachindex(areas)
        a = max(edges[j],min_elevation); b = min(edges[j+1],water)
        b <= a && continue
        density = areas[j]/(edges[j+1]-edges[j])
        # Exact integral of depth/(depth_scale+depth), for water>=b.
        cap = (b-a)-depth_scale*log1p((b-a)/(depth_scale+water-b))
        damage += density*(capital_density*cap+(b-a)*population_density*mortality*value_of_life)
    end
    (1-resilience)*damage
end

function expected_flood_loss(damage, distribution; lower, upper, panels=2048)
    simpson(s -> damage(s)*gev_pdf(s; distribution...),lower,upper,panels)
end

function relocation_cost(area, income, population_density, capital_density;
                         income_years=1.0, mobile_share=0.25,
                         capital_fraction=0.1, demolition_fraction=0.05, reactive=false)
    min(area,income,population_density,capital_density,income_years,capital_fraction,demolition_fraction) >= 0 || throw(DomainError(area))
    0 <= mobile_share <= 1 || throw(DomainError(mobile_share))
    cost = area*(income_years*income*population_density +
                 (capital_fraction*mobile_share+demolition_fraction*(1-mobile_share))*capital_density)
    reactive ? 5cost : cost
end

function inundation_cost(area, land_value, capital_density; mobile_share=0.25, depreciation=0.0)
    min(area,land_value,capital_density) >= 0 || throw(DomainError(area))
    0 <= depreciation <= 1 && 0 <= mobile_share <= 1 || throw(DomainError(depreciation))
    area*(land_value+(1-depreciation)*(1-mobile_share)*capital_density)
end

function protection_cost(length_km, height_m, coefficient; maintenance_annual=0.0)
    min(length_km,height_m,coefficient,maintenance_annual) >= 0 || throw(DomainError(height_m))
    # Construction USD, annual maintenance USD/year; timing is not conflated.
    (construction=length_km*coefficient*height_m^2, maintenance=maintenance_annual)
end

function wetland_loss(inundated_area, wetland_area, value_per_area, rate; protected=false, critical_rate=0.01)
    min(inundated_area,wetland_area,value_per_area,rate) >= 0 && critical_rate > 0 || throw(DomainError(rate))
    factor = protected || rate >= critical_rate ? 1.0 : (rate/critical_rate)^2
    value_per_area*min(inundated_area,wetland_area)*factor
end

function present_value(costs, years; rate=0.04, baseyear=2010)
    length(costs) == length(years) || throw(DimensionMismatch())
    rate > -1 && all(isfinite,costs) || throw(DomainError(rate))
    sum(costs ./ (1+rate).^(years .- baseyear))
end

function choose_adaptation(candidate_costs, years; rate=0.04, baseyear=2010)
    size(candidate_costs,2) == length(years) || throw(DimensionMismatch())
    pv = [present_value(vec(candidate_costs[i,:]),years;rate=rate,baseyear=baseyear)
          for i in axes(candidate_costs,1)]
    i = argmin(pv) # stable first candidate resolves exact ties
    (choice=i, value=pv[i], candidate_values=pv)
end

function warming_bin(t)
    isfinite(t) || throw(DomainError(t))
    t <= 1.5 ? 1 : t <= 2.5 ? 2 : t <= 3.5 ? 3 : 4
end

function subsample_joint(rng, rows::AbstractMatrix, n::Int)
    0 < n <= size(rows,1) || throw(ArgumentError("invalid subset size"))
    idx = randperm(rng,size(rows,1))[1:n]
    rows[idx,:], idx
end

function conditional_summary(temperature, costs)
    length(temperature) == length(costs) || throw(DimensionMismatch())
    all(isfinite,costs) || throw(ArgumentError("nonfinite cost"))
    bins = warming_bin.(temperature)
    [(bin=i,n=count(==(i),bins),quantiles=any(bins .== i) ?
        quantile(costs[bins .== i],[0.05,0.5,0.95]) : fill(NaN,3)) for i in 1:4]
end

function regional_percentages(costs, gdp)
    length(costs) == length(gdp) && !isempty(gdp) || throw(DimensionMismatch())
    all(gdp .> 0) || throw(DomainError(gdp))
    global_percent = 100sum(costs)/sum(gdp)
    (percent=100 .* costs ./ gdp, excess=100 .* costs ./ gdp .- global_percent,
     global_percent=global_percent)
end

end # module
