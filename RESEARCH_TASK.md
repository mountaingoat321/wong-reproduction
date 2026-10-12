# Independent Reproduction of Coastal Adaptation and Damage Costs at Different Global Warming Thresholds

## Project objective

The goal of this project is to independently recreate the scientific and computational results of Wong et al. (2025), **"Coastal adaptation and damage costs at different global warming thresholds,"** published in *npj Natural Hazards*:

https://www.nature.com/articles/s44304-025-00089-0

Independently implement the integrated climate, sea-level, and coastal impacts modeling framework described in the publication, its supplementary materials, and relevant scientific literature. Use your implementation to reproduce the manuscript's numerical results and figures.

The project has two equally important objectives:

1. **Scientific reproduction:** Determine whether the published results can be independently reproduced from their scientific specifications, including the governing equations, model parameters, uncertainty distributions, numerical procedures, and input assumptions.

2. **Evaluation of AI research capabilities:** Assess how successfully an AI research agent can translate published scientific documentation into a functioning computational model, identify missing information, make and justify scientific implementation decisions, verify calculations, and critically evaluate discrepancies.

Prioritize scientific correctness, transparency, and reproducibility over superficial agreement with the published figures.

Do not treat visual similarity to published results as sufficient evidence of successful reproduction.

## 1. Independence and permitted sources

Use the published manuscript, supplementary materials, cited methodological papers, equations, parameter tables, and other written scientific descriptions as the specifications for your implementation.

**Do not consult or use the authors' original source code, model implementations, computational notebooks, plotting scripts, simulation outputs, processed results, or published figure data, including those hosted on GitHub or Zenodo.**

You may consult written scientific descriptions of the underlying models, including peer-reviewed methodological publications and supplementary documentation. Do not inspect source-code files or use existing implementations of the specific models being reconstructed, even when publicly available.

Published figures may be inspected to understand the quantities being presented and to compare your independently generated results with the publication. Do not digitize published figures to create input data or numerical results.

Distinguish carefully between:

- Scientific documentation specifying a model.
- Independent observational or exogenous input data required to run the model.
- Authors' model-generated outputs or processed results, which must not be reused.

Publicly available independent observational, geographic, socioeconomic, and climate-forcing datasets may be used where scientifically necessary, provided that they are not copied from the authors' simulation outputs or reproduction data products. Document their original provenance, versions, processing methods, and any differences from those used in the publication.

If an essential input dataset is unavailable except through the authors' prohibited output or data repository, report that limitation explicitly. Do not silently substitute simulated data or invent values.

You may use ordinary numerical, optimization, statistical, and plotting libraries, but not existing implementations of the specific scientific models being independently reconstructed.

## 2. Scientific model reconstruction

The publication uses an integrated modeling framework connecting greenhouse gas emissions, climate response, sea-level change, and coastal impacts.

Reconstruct the following components as faithfully as the written scientific documentation permits.

### A. Emissions and climate modeling

Reconstruct the documented emissions-generation and climate-modeling methodology, including the Simple Nonlinear Earth System Model (SNEASY), as applicable.

Document and implement:

- Greenhouse gas emissions pathways and their parameterization.
- Carbon-cycle response and atmospheric CO2 concentrations.
- Non-CO2 radiative forcing assumptions.
- Global mean surface temperature response.
- Ocean heat uptake.
- Uncertain model parameters and their specified distributions.
- Calibration methods and initial conditions.
- Temporal resolution and integration methods.

Determine how the study generates its ensemble of plausible emissions and climate trajectories.

Reproduce the climate quantities required by downstream sea-level calculations, including the 2100 global warming levels used for temperature-threshold classification.

### B. Sea-level projections

Independently reconstruct the sea-level modeling methodology described for MimiBRICK and the associated literature.

Identify and implement the documented contributions from:

- Ocean thermal expansion.
- Greenland Ice Sheet.
- Antarctic Ice Sheet.
- Glaciers and ice caps.
- Land-water storage.
- Other contributions explicitly included in the publication.

Document the physical and statistical relationships used to connect global surface temperature and ocean heat uptake to global mean sea-level change.

Pay particular attention to uncertainty and nonlinear or threshold-dependent responses, including the representation of potentially rapid Antarctic ice-sheet changes.

Implement the documented procedure for translating component-specific global sea-level contributions into local relative sea-level change using geographic fingerprints and other specified effects.

Record all reference periods, units, spatial resolutions, time horizons, and parameter assumptions.

### C. Coastal impacts and adaptation modeling

Independently reconstruct the coastal economic modeling framework described for MimiCIAM and its underlying scientific references.

The implementation should calculate adaptation decisions, adaptation costs, and residual economic damages for individual coastal segments.

Reconstruct the documented model behavior for:

- Seawall construction and maintenance.
- Planned relocation and retreat.
- No-adaptation alternatives.
- Permanent inundation.
- Extreme coastal flooding.
- Loss of property and capital.
- Potential mortality and associated economic valuations.
- Wetland losses.
- Economic optimization of adaptation decisions.

Implement the documented cost functions, protection levels, local hazard distributions, and optimization procedures.

Represent the distinction between adaptation expenditures and residual damages correctly, including their combination into total modeled economic costs.

The publication describes approximately 12,148 coastal segments, a 2010–2150 analysis horizon, 10-year computational steps, and adaptation decisions across three periods. Reproduce these specifications and their precise implementation as supported by the written scientific documentation.

Reconstruct the least-cost adaptation decision process, including the documented foresight assumptions, discounting, and updating of adaptation decisions over time.

Use the documented socioeconomic assumptions, including SSP-based population, GDP, and capital-value trajectories.

Explicitly distinguish model assumptions about economically optimal adaptation from predictions of actual human adaptation behavior.

## 3. Ensemble generation and uncertainty

Reconstruct the probabilistic experimental design used in Wong et al.

The published study describes a larger ensemble of 100,000 potential states of the world and a 5,000-member analysis ensemble.

Determine from the scientific documentation:

- How uncertain parameters are distributed and sampled.
- Which uncertainties are correlated.
- How emissions and climate trajectories are generated.
- How climate projections are coupled to sea-level projections.
- How sea-level trajectories are coupled to coastal economic outcomes.
- How the 5,000-member analysis ensemble is selected.
- Whether ensemble members are assigned probabilities or weights.
- How socioeconomic scenarios are paired with climate and sea-level trajectories.

Do not substitute arbitrary uncertainty distributions for undocumented published distributions.

Where exact probabilistic specifications are missing, clearly identify the missing information and document any scientifically justified approximation.

Reproduce the classification of ensemble members into the study's four global warming categories:

- Warming at or below 1.5°C.
- Warming above 1.5°C and at or below 2.5°C.
- Warming above 2.5°C and at or below 3.5°C.
- Warming above 3.5°C.

Use the publication's specified temperature reference period and endpoint definitions.

Reconstruct the reported ensemble statistics, including medians, quantiles, credible intervals, and threshold-conditioned distributions.

Use independent random samples and record random seeds so that the calculations are reproducible. Do not expect an independently sampled ensemble to match individual original realizations.

Where exact reproduction requires undocumented posterior samples, calibration results, or probability distributions, distinguish this limitation from errors in the model implementation.

## 4. Feasibility assessment and scientific documentation

Before beginning large-scale computation, analyze the scientific documentation and create a structured model-reconstruction plan.

Identify:

1. Every major model component and its dependencies.
2. The mathematical equations and computational procedures governing each component.
3. Required parameters and their documented values or distributions.
4. Required initial and boundary conditions.
5. Required observational and socioeconomic input datasets.
6. Spatial and temporal discretizations.
7. Numerical integration, sampling, and optimization methods.
8. Quantities passed between model components.
9. Important undocumented or ambiguous implementation details.
10. The published figures and results dependent on each component.

Create a traceable scientific specification mapping each implementation decision to a publication, equation, table, or documented methodological statement.

**Do not invent scientific equations, parameter values, calibration results, or assumptions to force agreement with the published figures.**

When information is incomplete:

- Identify precisely what is missing.
- Search the permissible scientific literature for a documented specification.
- Distinguish a documented specification from an independent reconstruction assumption.
- State the scientific rationale for any approximation.
- Evaluate its likely effect on the results.
- Test sensitivity to consequential assumptions where feasible.
- Report when faithful reproduction is not possible.

Proceed with implementable components rather than abandoning the entire project because another component is incompletely specified.

Maintain an assumption register distinguishing documented assumptions, independently chosen numerical methods, approximations, and unresolved scientific specifications.

## 5. Numerical implementation

Implement the model in a computationally efficient language, preferably Julia or C++.

Julia is a suitable choice given the numerical and optimization requirements, but all model-specific scientific calculations must be independently implemented.

Use established general-purpose numerical and scientific libraries where appropriate.

Write clear, modular, documented research code.

Maintain identifiable computational components for:

- Climate and emissions calculations.
- Sea-level projections.
- Geographic downscaling.
- Coastal economic modeling.
- Adaptation optimization.
- Ensemble generation.
- Regional aggregation.
- Statistical analysis.
- Figure generation.

Ensure that the implementation conserves units, uses consistent reference periods, and correctly handles spatial and temporal indexing.

Record software versions, dependencies, random seeds, solver tolerances, and other computational settings affecting reproducibility.

Do not use arbitrary calibration factors to force agreement with publication results.

## 6. Validation and numerical verification

Before attempting large ensembles, verify each scientific component independently.

Use appropriate tests, including where applicable:

- Limiting-case solutions.
- Dimensional consistency.
- Conservation and accounting identities.
- Zero-forcing or zero-sea-level-change tests.
- Simple analytically tractable climate or sea-level cases.
- Monotonicity and sign checks where physically justified.
- Internal consistency of sea-level components.
- Consistency between global and spatially aggregated quantities.
- Verification of economic discounting.
- Tests of the adaptation optimization procedure.
- Convergence with numerical resolution and solver tolerances.
- Sensitivity to uncertain scientific parameters.
- Repeated-run reproducibility.

For the coastal optimization model, construct simplified test cases in which the economically preferred adaptation decision can be determined independently.

Check that changing relevant inputs produces physically and economically interpretable responses, while recognizing that not every response must be monotonic.

Document tests that pass, tests that fail, and tests that cannot be performed because of missing specifications.

Do not interpret agreement with a published aggregate statistic as proof that the underlying model is correct.

## 7. Progressive reproduction of published figures

Attempt every figure and panel in the main manuscript, followed by supplementary figures where the documentation permits.

Use a staged approach.

### Stage 1: Primary results

Prioritize reproduction of the central scientific findings:

**Figure 1: Global coastal adaptation costs and damages across warming thresholds.**

Calculate the net present value of global adaptation costs and damages for the four temperature categories.

Reproduce the reported median estimates and 5th–95th percentile intervals using the publication's 4% discount rate and monetary conventions.

**Figure 2: Global mean sea-level rise and coastal economic costs.**

Recreate the relationship between global mean sea-level change in 2100 and the net present value of coastal adaptation costs and damages, including temperature-conditioned distributions and marginal distributions where possible.

**Figure 3: Geographic inequality in coastal impacts.**

Calculate regional coastal costs and damages as a percentage of regional GDP, using the seven World Bank regions defined in the publication.

Reproduce differences among warming thresholds and examine the sensitivity to socioeconomic assumptions.

**Figure 4: Model workflow.**

Create an original schematic documenting the independently implemented modeling chain.

Label this as a conceptual schematic, not as an independently reproduced numerical model result.

### Stage 2: Supplementary results

Attempt the supplementary figures and analyses, including:

- Ensemble size and convergence tests.
- Alternative temperature-bin sample sizes.
- Comparison with established climate projections.
- Comparison with published global sea-level projections.
- Tail probabilities and high-damage outcomes.
- Alternative socioeconomic scenarios.
- Regional economic sensitivity analyses.
- Any additional supplementary panels or tables present in the publication.

First inspect the complete supplementary material and inventory every figure, panel, and table. Do not assume the examples listed here constitute the complete inventory.

### Stage 3: Additional scientifically necessary tests

Where reproduction is incomplete or discrepancies are substantial, perform targeted sensitivity experiments and diagnostic calculations.

Use these experiments to determine whether discrepancies arise from:

- Missing model specifications.
- Input data differences.
- Parameter uncertainty.
- Sampling variability.
- Numerical approximations.
- Optimization differences.
- Geographic aggregation.
- Socioeconomic assumptions.
- Scientific implementation errors.

Do not alter the model solely to improve visual similarity with the publication.

## 8. Figure generation and comparison

Generate every numerical figure from saved numerical output produced by your independent implementation.

Write your own scripts to create the figures.

Do not copy, trace, digitize, or reuse the authors' original figures or plotting files.

Treat conceptual diagrams separately. Recreate diagrams only as new schematics, clearly distinguished from reproduced quantitative results.

For each numerical panel, compare your results with the published result using quantitative metrics wherever possible.

Relevant comparisons may include:

- Median and percentile estimates.
- Ensemble distributions and tail probabilities.
- Global and regional cost magnitudes.
- Temperature-bin membership and sample sizes.
- Sea-level ranges and distributions.
- Relationships between warming, sea-level change, and damages.
- Regional ranking and spatial patterns.
- Sensitivity to socioeconomic scenarios.
- Magnitude and direction of discrepancies.

Where exact published numerical values are unavailable, describe qualitative agreement without presenting visual estimates as precise measurements.

Do not claim that a panel is reproduced merely because a plot resembles the published figure.

Only call a numerical panel "independently reproduced" if the plotted data were generated by the independently implemented model and the relevant scientific and quantitative comparisons support that assessment.

## 9. Figure-by-figure reproducibility record

Maintain a complete figure-by-figure record covering every main-text and supplementary figure and panel.

For each entry, document:

1. Figure and panel identifier.
2. Scientific quantity or relationship shown.
3. Required model components.
4. Scientific documentation and parameters used.
5. Input data and their provenance.
6. Assumptions and approximations.
7. Command used to generate the numerical data.
8. Command used to generate the figure.
9. Quantitative comparison with the publication.
10. Reproduction status.
11. Explanation of discrepancies or failure.

Use these status categories:

- **Independently reproduced:** Generated by the independent implementation with scientifically justified agreement.
- **Partially reproduced:** Generated by the independent implementation, but incomplete or substantially discrepant.
- **Not reproduced:** Could not be generated or reconstructed from the available specifications.
- **Conceptual schematic:** Non-numerical diagram, not counted as a reproduced model result.

Never describe a copied published figure as an independently reproduced result.

## 10. Assessment of AI-agent performance

Because this project is also an evaluation of AI-assisted scientific research, document the agent's reconstruction process.

Include a concise research log describing:

- What scientific specifications were readily recoverable.
- Which model components required substantial interpretation.
- Which aspects of the documentation were ambiguous or incomplete.
- What independent scientific or computational decisions were made.
- What verification tests revealed errors or inconsistencies.
- Which discrepancies were resolved.
- Which discrepancies remain unexplained.
- What limitations prevented complete reproduction.

Distinguish between failure caused by inadequate scientific documentation and failure caused by computational or implementation difficulties.

Evaluate the extent to which the project successfully reconstructed a complex integrated scientific model without consulting the original implementation.

Do not overstate the independence, scientific validity, or completeness of the results.

## 11. Final scientific report

The final scientific deliverable is a compiled PDF report and its complete LaTeX source.

The report should include:

1. Abstract and statement of the reproduction objective.
2. Overview of the original scientific study.
3. Reconstruction of the model framework and governing equations.
4. Scientific assumptions and input datasets.
5. Numerical implementation and optimization methods.
6. Verification and validation results.
7. Independently generated numerical results and figures.
8. Figure-by-figure reproduction record.
9. Quantitative comparison with the publication.
10. Analysis of discrepancies and limitations.
11. Assessment of the AI-agent reconstruction process.
12. Conclusions describing what was and was not independently reproduced.
13. References and, where useful, technical appendices.

Include tables of important model parameters and their sources.

Use generated figures produced by the independent implementation.

If an original figure from the publication is included for comparison, label it clearly as a published reference and distinguish it visually from independently generated material.

The discussion should distinguish demonstrated numerical behavior from physical interpretation and speculation.

Follow the academic writing style guide specified below.

## 12. Reproducibility and project deliverables

Provide a clean, documented procedure that:

1. Installs or verifies necessary dependencies.
2. Builds the numerical implementation.
3. Runs verification tests.
4. Generates model outputs.
5. Reproduces the ensemble analysis.
6. Generates the numerical figures.
7. Compiles the LaTeX report into a PDF.

Run this procedure and report the outcome, including any failures.

Provide sufficient information to regenerate the scientific results from the documented input data.

The project repository must contain:

- Independent model source code.
- Numerical configuration files.
- Input data provenance and acquisition instructions.
- Permitted input data where redistribution is appropriate.
- Verification and validation tests.
- Plotting and analysis scripts.
- Generated numerical results.
- Generated manuscript figures.
- Assumption and research logs.
- Figure-by-figure reproduction record.
- LaTeX report source.
- Compiled PDF report.
- A README describing the project and its reproduction commands.

If input datasets are too large to store in the repository, provide stable source references, checksums where appropriate, and scripts for obtaining and preparing them.

Do not present an unexecuted command or an untested workflow as successfully reproduced.

## 13. GitHub repository and external instructions

Create a new GitHub repository in the account currently logged in.

You are authorized to use the workspace's available SSH credentials to create the repository and push project files.

Upload the code, configurations, plotting scripts, generated numerical data, LaTeX source, compiled PDF, and associated documentation to that repository.

Follow the `AGENTS.md` instructions at:

https://github.com/bradlipovsky/vdv-damage/blob/main/AGENTS.md

Follow the academic style guide at:

https://github.com/bradlipovsky/vdv-damage/blob/main/brad-lipovsky-academic-style-guide.md

These two guidance documents are explicitly permitted sources. They do not authorize consulting the original authors' model code, simulation outputs, or plotting scripts.

Use a minimal, scientifically transparent research-code structure. Prefer direct, readable implementations over unnecessarily complicated abstractions.

## 14. Computational environment and file storage

The designated project root on Sermeq is `/data/data2/ludtke/wong-reproduction`. Store the project source, required inputs, intermediate products, numerical outputs, figures, and reports under this root. Do not relocate the project or write scientific project artifacts to the home directory.

Do not save project files to home directories.

Keep the entire project in one of the following storage locations:

`/data/data0` through `/data/data7`

Check available disk space before selecting a directory.

Use the selected directory for source code, temporary files, dependencies where practical, intermediate outputs, numerical datasets, figures, and reports.

Avoid duplicating large datasets unnecessarily.

Record the computational environment and any resource limitations affecting the experiment.

Where the complete ensemble is computationally expensive, begin with small verification runs, then progressively increase the sample size after confirming numerical correctness.

Do not replace the full experiment with a reduced ensemble without explicitly reporting the resulting limitation.

## 15. Final reporting requirements

In the final response:

- Link to the new GitHub repository.
- Link to the compiled PDF report.
- Identify which numerical figures and panels were independently reproduced.
- List every figure and panel that remains partial or unreproduced.
- Summarize the most important quantitative agreements and discrepancies.
- Explain any scientific specifications that could not be recovered.
- Report the validation and end-to-end build results.
- Describe the major limitations of the independent reconstruction.
- State what the experiment reveals about the capabilities and limitations of an AI research agent for complex scientific model reproduction.

**A scientifically honest partial reproduction is preferable to an apparently complete reproduction obtained through invented assumptions, copied results, or undocumented shortcuts.**

Begin by reviewing the publication and permitted methodological documentation, inventorying the full set of required model components and published figures, and establishing the scientific specifications. Then implement, validate, and progressively reproduce the results. Continue as far as the available documentation and computational resources permit, reporting limitations explicitly rather than concealing them.