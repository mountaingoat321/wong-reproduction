module BoundedLeastSquares
using LinearAlgebra
"""Damped least squares on a unit box; report projected gradient and stop reason."""
function fit(residual,start;iterations=100,gradient_tolerance=1e-8,trace=false)
    u=clamp.(copy(start),0.,1.);r=residual(u);value=sum(abs2,r)
    damping=1e-3;lastgradient=Inf
    for iteration in 1:iterations
        jac=zeros(length(r),length(u));delta=1e-5
        for j in eachindex(u)
            a=copy(u);b=copy(u);a[j]=max(0.,u[j]-delta);b[j]=min(1.,u[j]+delta)
            jac[:,j]=(residual(b)-residual(a))/(b[j]-a[j])
        end
        gradient=jac'r;hessian=jac'jac
        active=[j for j in eachindex(u) if !((u[j]<=1e-10 && gradient[j]>0)||(u[j]>=1-1e-10 && gradient[j]<0))]
        projected=copy(gradient)
        for j in setdiff(eachindex(u),active);projected[j]=0.;end
        lastgradient=maximum(abs.(projected))
        if trace && iteration%10==0
            println("  iteration=",iteration," objective=",value," projected_gradient=",lastgradient," coordinates=",u)
            flush(stdout)
        end
        lastgradient<gradient_tolerance && return (u=u,objective=value,iterations=iteration,projected_gradient=lastgradient,stop="projected_gradient")
        accepted=false;change=0.;improvement=0.
        diagonal=max.(diag(hessian)[active],1e-6)
        for attempt in 1:16
            step=zeros(length(u));step[active]=-(hessian[active,active]+damping*Diagonal(diagonal))\gradient[active]
            normstep=maximum(abs.(step));normstep>.25 && (step*=.25/normstep)
            for power in 0:12
                trial=clamp.(u+2.0^(-power)*step,0.,1.);rr=residual(trial);v=sum(abs2,rr)
                if v<value
                    change=maximum(abs.(trial-u));improvement=value-v
                    u=trial;r=rr;value=v;accepted=true;damping=max(damping/3,1e-12)
                    break
                end
            end
            accepted && break
            damping*=10
        end
        !accepted && return (u=u,objective=value,iterations=iteration,projected_gradient=lastgradient,stop="no_descent")
        if change<1e-9 && improvement<1e-11*(1+value)
            return (u=u,objective=value,iterations=iteration,projected_gradient=lastgradient,stop="small_step_and_objective")
        end
    end
    (u=u,objective=value,iterations=iterations,projected_gradient=lastgradient,stop="iteration_limit")
end
end
