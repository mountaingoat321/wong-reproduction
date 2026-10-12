# Scientific assumptions log

Initialized 2026-10-12. No scientific model has been implemented, no main
simulations have been run, and no model parameters or physical mechanisms have
been assumed. The entries below record unresolved information and project
constraints; they are not findings about Wong et al. (2025).

| ID | Status | Topic | Record and required resolution |
| --- | --- | --- | --- |
| S001 | Unresolved | Source identity | The user supplied only “Wong et al. (2025).” Record the title, full citation, DOI or paper URL, and version before interpreting the study. |
| S002 | Unresolved | Reproduction targets | Specify the quantities, cases, and comparison criteria to reproduce before implementation. No agreement or error tolerance has been chosen. |
| S003 | Unresolved | Physical model | Record geometry, coordinates, governing equations, constitutive laws, approximations, and their sources. No model has been selected. |
| S004 | Unresolved | Units and parameters | Record symbols, dimensions, parameter values, provenance, conversions, and any nondimensionalization. SI is the writing convention; paper-specific units remain unknown. |
| S005 | Unresolved | Initial and boundary conditions | Record conditions, domain, loading, and time interval with source locations. None have been prescribed. |
| S006 | Unresolved | Numerical method | Record discretization, solver, convergence checks, tolerances, precision, and any random seeds. No numerical scheme has been chosen. |
| S007 | Unresolved | Observables and interpretation | Define predicted observables, permissible comparison evidence, uncertainty, and the limits of inference. No scientific results are available. |
| P001 | Required by user | Independence | Do not consult the authors' original implementation, outputs, or plotting scripts. Record permitted sources used in future work. |
| P002 | Superseded in part by P003 | Initial boundary | The original initialization request prohibited remote creation and pushing until confirmation. The restrictions on writes outside the project, system installations, and starting main simulations remain in effect. |
| P003 | Required by user | Git/GitHub setup | The user subsequently authorized a local author name of Sophia Ludtke, a confirmed or user-supplied email, an initial commit containing only initialization files, and creation and initial push of the private repository `mountaingoat321/wong-reproduction`. Do not change global Git settings or begin scientific reproduction. |

For each later scientific entry, record:

- Date, stable ID, status, and the claim or assumption.
- Claim type: observation, calculation, inference, or speculative mechanism.
- Source and precise location, such as a page or equation; identify independent
  derivations explicitly.
- Geometry, equations, quantities, units, parameter values, and initial and
  boundary conditions relevant to the entry.
- Physical justification, predicted observable, uncertainty, and a test that
  could assess the assumption.
- Consequences for the reproduction and any revision with its reason.

Keep superseded entries identifiable so changes in scientific assumptions remain
traceable. Do not replace missing evidence with an unstated modeling choice.
