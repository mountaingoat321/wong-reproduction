module SciPyLeastSquares
"""Run the ordinary SciPy bounded solver while keeping scientific residuals
inside Julia. The reported iteration count is SciPy nfev, excluding Jacobians;
residual_evaluations records the actual total calls across the pipe.
"""
function fit(residual,start;iterations=100,trace=false)
    worker=joinpath(@__DIR__,"..","scripts","bounded_least_squares_worker.py")
    result=nothing
    open(`python3 -B $worker $(join(start,','))`,"r+") do io
        while !eof(io)
            fields=split(readline(io),',')
            if first(fields)=="E"
                u=parse.(Float64,fields[2:end]);r=residual(u)
                println(io,join(r,','));flush(io)
            elseif first(fields)=="R"
                n=length(start);u=parse.(Float64,fields[2:n+1])
                result=(u=u,objective=parse(Float64,fields[n+2]),iterations=parse(Int,fields[n+3]),
                    projected_gradient=parse(Float64,fields[n+4]),stop=String(fields[n+5]),
                    residual_evaluations=parse(Int,fields[n+6]),scaled_gradient=parse(Float64,fields[n+7]))
                break
            else
                error("Unexpected optimizer protocol message")
            end
        end
    end
    isnothing(result) && error("Optimizer closed without a result")
    result
end
end
