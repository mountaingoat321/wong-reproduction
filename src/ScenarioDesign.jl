module ScenarioDesign
"""Minimum-relative-entropy weights subject to one event probability.
For a uniform empirical prior, the minimizing weights are constant within
each event class. This is a mathematical alternative, NOT Darnell's missing
expert-density prescription, and imposes no SSP4-6.0 mode.
"""
function budget_weights(within,probability)
    0<probability<1 || throw(DomainError(probability))
    n=length(within);inside=count(within)
    0<inside<n || throw(ArgumentError("both budget classes must be sampled"))
    [flag ? probability/inside : (1-probability)/(n-inside) for flag in within]
end

"""Generalized inverse of the weighted empirical CDF; no interpolation."""
function weighted_quantile(values,weights,p)
    length(values)==length(weights) && 0<=p<=1 || throw(ArgumentError("invalid weighted quantile"))
    all(weights.>=0) && sum(weights)>0 || throw(DomainError(weights))
    order=[i for i in sortperm(values) if weights[i]>0]
    cumulative=cumsum(weights[order]);target=p*cumulative[end]
    # Select the left side of an exact CDF jump within floating-point error.
    index=clamp(searchsortedfirst(cumulative,target-8eps(cumulative[end])),1,length(order))
    values[order[index]]
end
end
