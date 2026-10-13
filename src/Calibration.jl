module Calibration
using LinearAlgebra, Random, Statistics

"""Gaussian AR1 process plus independent, known, heteroskedastic observation
noise. Scalar Kalman filter gives the exact marginal likelihood in O(n).
sigma is the innovation standard deviation; the initial process is stationary.
"""
function ar1_loglikelihood(residual,sigma,rho,observation_sd)
    length(residual)==length(observation_sd) || throw(DimensionMismatch())
    sigma>0 && abs(rho)<1 && all(observation_sd.>=0) || throw(DomainError(sigma))
    m=0.0; variance=sigma^2/(1-rho^2); value=0.0
    for i in eachindex(residual)
        total=variance+observation_sd[i]^2; innovation=residual[i]-m
        value-=0.5*(log(2pi*total)+innovation^2/total)
        gain=variance/total
        m=rho*(m+gain*innovation)
        variance=rho^2*(1-gain)*variance+sigma^2
    end
    value
end

"""Random-walk Metropolis. Covariance adapts only during discarded warmup;
production transition kernel is fixed. Caller supplies scientific log density.
"""
function metropolis(logdensity,initial,scales,rng;warmup=3000,draws=6000,
                    adapt_window=warmup,proposal_scale=2.38)
    d=length(initial); theta=copy(initial); logp=logdensity(theta)
    isfinite(logp) || throw(ArgumentError("initial state has zero density"))
    proposal=Matrix(Diagonal(scales)); history=zeros(warmup,d)
    samples=zeros(draws,d); values=zeros(draws); accepted=0; warm_accepted=0
    for i in 1:warmup+draws
        candidate=theta+proposal*randn(rng,d); lp=logdensity(candidate)
        if log(rand(rng))<lp-logp
            theta=candidate; logp=lp
            if i<=warmup; warm_accepted+=1; else; accepted+=1; end
        end
        if i<=warmup
            history[i,:]=theta
            if i>=500 && i%250==0
                covariance=cov(history[max(1,i-adapt_window+1):i,:])
                proposal=Matrix(cholesky(Symmetric(proposal_scale^2/d*covariance+
                    1e-4*Diagonal(scales.^2))).L)
            end
        else
            samples[i-warmup,:]=theta; values[i-warmup]=logp
        end
    end
    (samples=samples,logdensity=values,acceptance=accepted/draws,
     warmup_acceptance=warm_accepted/warmup)
end
end
