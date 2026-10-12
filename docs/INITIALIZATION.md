# Historical initialization record

The scope statements below predate the research launch and are superseded by the
current README and AGENTS.md. Retained for environment and guidance provenance.

# Wong et al. (2025): independent scientific reproduction

This repository is prepared for an independent scientific reproduction of Wong
et al. (2025). Initialization was completed on 2026-10-12. Further scientific work
awaits the user's confirmation. The exact paper title, DOI, and reproduction
targets have not yet been supplied; no physical model or parameters have been
selected.

All project writes and outputs belong inside
`/data/data2/ludtke/wong-reproduction`. No system-wide installations or other
users' files were modified. The authors' original implementation, outputs, and
plotting scripts have not been consulted. No main simulations have been started.

## Repository contents

| File | Purpose |
| --- | --- |
| [AGENTS.md](../AGENTS.md) | Applicable research instructions and the user's project constraints. |
| [AGENTS.upstream.md](../AGENTS.upstream.md) | Unmodified copy of Brad Lipovsky's source instructions. |
| [brad-lipovsky-academic-style-guide.md](../brad-lipovsky-academic-style-guide.md) | Unmodified academic writing guide. |
| [ASSUMPTIONS.md](../ASSUMPTIONS.md) | Scientific assumptions, unresolved information, and evidence requirements. |
| [.gitignore](../.gitignore) | Exclusions for credentials, local environments, build files, and large intermediates. |

Code, data, and additional directories will be added only when needed. Local
tool checks and their small outputs are retained under ignored `.local/checks/`.

## Guidance provenance

Both requested documents were retrieved and read in full from
`bradlipovsky/vdv-damage` on 2026-10-12. The `main` branch resolved to commit
`3d35f81420a744ca99360a6774d3bcbd4e123405`; both copies were downloaded from that
same revision. Only the two guidance files and the revision metadata were
retrieved from that repository.

- Requested [AGENTS.md](https://github.com/bradlipovsky/vdv-damage/blob/main/AGENTS.md);
  [fixed revision](https://github.com/bradlipovsky/vdv-damage/blob/3d35f81420a744ca99360a6774d3bcbd4e123405/AGENTS.md).
  Local file: `AGENTS.upstream.md` (1,027 bytes).
  SHA-256: `f0d220a68760daf24c41da082176a107061b0ea33eada5f3b19e0eb5d6c3c837`.
- Requested [academic style guide](https://github.com/bradlipovsky/vdv-damage/blob/main/brad-lipovsky-academic-style-guide.md);
  [fixed revision](https://github.com/bradlipovsky/vdv-damage/blob/3d35f81420a744ca99360a6774d3bcbd4e123405/brad-lipovsky-academic-style-guide.md).
  Local file: `brad-lipovsky-academic-style-guide.md` (16,676 bytes).
  SHA-256: `9856e89591c25dcdc00dda251678912fcea2fba58615ce3f5c19c76d3c5944dd`.

The local instructions adopt both documents. The user subsequently authorized
the initial commit and publication of the initialization files to a private
GitHub repository. Scientific work remains outside the current scope.

## Environment check

Checked on 2026-10-12. Versions below are observed installations, not dependency
requirements for the as-yet unspecified scientific model.

| Tool | Installed version | Check |
| --- | --- | --- |
| Julia | 1.7.2 | Starts successfully; standard-library `LinearAlgebra` calculation passed. |
| C++ (`c++`, `g++`) | GCC 8.5.0; Red Hat 8.5.0-28, build 20210514 | C++17 program using the standard library compiled and ran successfully. |
| Git | 2.43.5 | Existing local repository verified. |
| GitHub CLI (`gh`) | 2.58.0 (2024-10-01) | Authentication status and authenticated `/user` API request succeeded. |
| LaTeX / pdfLaTeX | pdfTeX 3.14159265-2.6-1.40.19; TeX Live 2018 | Minimal `article` document compiled to a one-page PDF with pdfLaTeX. |
| XeLaTeX | XeTeX 3.14159265-2.6-0.99999; TeX Live 2018 | Version command succeeded. |
| LuaLaTeX | LuaTeX 1.09.0; TeX Live 2018 | Version command succeeded. |
| latexmk | 4.65 (2019-06-18) | Version command succeeded. |
| BibTeX | 0.99d; TeX Live 2018 | Version command succeeded. |

All four requested tool categories are available. No required dependency is
missing for initialization. Optional tools not found on PATH were `juliaup`,
`clang++`, and `biber`; none was needed for these checks. Scientific package and
LaTeX manuscript dependencies remain undetermined until the model and document
requirements are known. No packages were installed or upgraded.

Julia ran with startup and history disabled, a project-local depot, and only the
standard library on its load path. C++ compiled with
`-std=c++17 -Wall -Wextra -pedantic`. pdfLaTeX used
`-no-shell-escape -interaction=nonstopmode -halt-on-error`. Temporary, cache,
depot, TeX state, and output paths for these checks were explicitly directed into
`.local/`. These were toolchain checks, not scientific simulations. Their source
files and logs are in `.local/checks/`.

## Git and GitHub

At the first environment check, the directory already contained a non-bare Git
repository, with its working tree and `.git/` both inside the project path. It
had an unborn `master` branch, no commits, and no remotes. Initialization
preserved that repository.

`gh auth status --hostname github.com` succeeded. An authenticated
`gh api user --jq .login` request verified account `mountaingoat321`. Credentials
were neither copied into the project nor included in this report.

The local Git author is Sophia Ludtke, using the email supplied by the user. The
user authorized an initial commit containing only the six initialization files
and private publication to
[mountaingoat321/wong-reproduction](https://github.com/mountaingoat321/wong-reproduction).
The publication destination is `origin`. All author and authentication-helper
configuration is repository-local; global Git settings remain unchanged.

The authenticated `user/emails` endpoint returned HTTP 404 and reported that the
current authentication lacks the required `user` scope. The user then supplied
the commit email directly. Its GitHub verification status was not established;
no email was inferred from the account name.

## Storage and next stage

Keep caches, local tools, and temporary checks in `.local/`. `.gitignore` excludes
common credential files, raw and intermediate data directories, simulation
checkpoints, binary array files, and build artifacts. Small curated figures,
PDFs, and notebooks remain eligible for version control. Git ignore rules are
based on names and paths; they cannot identify arbitrary secrets or impose a
file-size limit. Review selected files before committing.

After the user confirms the next stage, record the exact paper and target
quantities in `ASSUMPTIONS.md`, then document the physical assumptions and
equations using permitted sources. No main simulation is authorized by this
initialization step.
