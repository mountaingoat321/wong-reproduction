# Project instructions

This repository prepares an independent scientific reproduction of Wong et al.
(2025). The user has authorized Git and private GitHub setup. Scientific work
awaits separate instructions from the user.

## Scope and precedence

- Keep all project writes, outputs, temporary files, caches, and any future local
  installations inside `/data/data2/ludtke/wong-reproduction`. Check resolved
  paths before writing through symlinks.
- Do not modify system-wide installations or other users' files.
- Do not consult the Wong authors' original implementation, outputs, or plotting
  scripts. Do not retrieve their code repositories or generated results.
- Limit the current stage to project initialization and Git/GitHub setup. Do not
  begin the scientific reproduction or main simulations.
- The user authorized an initial commit and a private GitHub repository at
  `mountaingoat321/wong-reproduction`, connected as `origin`, with the initial
  commit pushed there. Keep the repository private.
- Configure Git only within this repository. Use the author name Sophia Ludtke
  and an email confirmed by GitHub verification or supplied by the user. Do not
  infer an email or change global settings.
- Never write credentials into project documentation, code, logs, or Git history.

Read and follow [AGENTS.upstream.md](AGENTS.upstream.md), Brad Lipovsky's original
research instructions, and the complete
[academic style guide](brad-lipovsky-academic-style-guide.md). The project scope
above implements the user's instructions and takes precedence over the upstream
instruction to commit and push notebooks. The current publication authorization
covers only project initialization files. Preserve notebook figures and outputs
when notebooks are introduced; later publication follows the user's scope.
The style guide is at the repository root; its example `outputs/` path does not
apply here. Source revision and checksums are recorded in [README.md](README.md).

## Research practice

- Keep analyses and code minimal, direct, and readable. Add functions,
  dependencies, and directories only when the investigation requires them.
- Prefer small functions and plain data. This is an initial investigation of the
  physics; avoid frameworks and unnecessary compatibility machinery.
- Start from first principles. Do not invent physics or silently introduce
  heuristic constraints, constitutive laws, or parameter values.
- Record assumptions, units, geometry, initial and boundary conditions, and each
  model's predicted observable in [ASSUMPTIONS.md](ASSUMPTIONS.md).
- Separate observations, calculations, inferences, and speculative mechanisms.
  Identify the evidence and uncertainty supporting each scientific claim.
- State physical assumptions before equations, define symbols near first use,
  and explain the physical meaning and limiting behavior of each relation.
- Use SI units unless a documented convention requires another unit; record
  conversions and nondimensional definitions explicitly.
- Record the exact paper citation and reproduction targets before modeling.
  Unspecified information remains unresolved until supported by evidence.

## Files and tools

Use `.local/` for tool checks, temporary files, caches, and any future local
dependencies. Set tool-specific depot, cache, and output paths explicitly; for
Julia, disable startup and history files when checking the environment. Keep
large raw data and simulation intermediates in the ignored paths listed in
`.gitignore`. Preserve small, curated scientific outputs and notebook contents.

Git ignore rules match names and paths, not file size or secret contents. Review
the files to be staged for sensitive material and large intermediates before
committing. Add dependencies only when their scientific purpose is known, and
record versions when they are introduced.
