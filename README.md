# ChemPy in Pyodide on GitHub Pages

A starter project that builds pure-Python wheels for ChemPy and its supporting packages,
then deploys those wheels and an interactive smoke-test page to GitHub Pages.
Pyodide's existing WebAssembly builds supply NumPy, SciPy, SymPy, and Matplotlib.

## Deploy

1. Create a GitHub repository with `main` as its default branch.
2. Copy these files into the repository, preserving `.github/workflows/deploy.yml`.
3. Under **Settings > Pages > Build and deployment**, select **GitHub Actions**.
4. Commit and push to `main`, or invoke **Actions > Build ChemPy wheels and deploy to Pages > Run workflow**.
5. Open the deployment URL from the `deploy` job. Project sites normally use
   `https://OWNER.github.io/REPOSITORY/`.

No repository secret, custom domain, or server-side process is required.

## What the workflow does

- Builds/downloads exact pinned wheels in `wheel-requirements.txt`.
- Rejects wheels with native platform tags, because regular Linux wheels do not run in Pyodide.
- Writes `wheels.json` listing the real filenames produced by the build.
- Deploys `index.html`, `wheels.json`, and `wheels/` as a single Pages artifact.
- Loads Pyodide 0.29.5 from a versioned CDN in the browser.
- Installs locally hosted wheels with `micropip.install(..., deps=False)`.
- Attempts two basic ChemPy checks: formula parsing and balancing water synthesis.

## Limits and caveats

- This is a **starter**, not a verified complete ChemPy port. Successful wheel
  packaging does not imply every ChemPy API works under WebAssembly.
- Runtime dependency resolution is deliberately disabled to avoid native backends
  and notebook dependencies. If a runtime import raises `ModuleNotFoundError`, add
  the relevant pure-Python wheel to `wheel-requirements.txt` or load a Pyodide package.
- The page will report whether its smoke tests pass, but GitHub Actions currently
  validates only packaging, not real-browser execution. A failing browser test is
  displayed on the deployed page and can be diagnosed in the browser console.
- PuLP is included for imports, but its bundled native executable solvers cannot
  run in the browser. Some complex reaction-balancing operations will need a
  browser-compatible optimization backend.
- Pyodide is downloaded from jsDelivr; GitHub Pages hosts the pure-Python wheels.
  For fully self-hosted/offline operation, you would need to host Pyodide assets too.
- The `pulp` wheel is relatively large, approximately 16 MB. Its Python API
  can import, but solver availability is a separate issue.
- All execution occurs on the browser's main thread. Consider moving it to a
  Web Worker for a real classroom application.

## Files

- `.github/workflows/deploy.yml`: GitHub Actions build and deployment.
- `wheel-requirements.txt`: pins for packages to package as universal wheels.
- `scripts/build_manifest.py`: verifies pure wheels and generates the manifest.
- `site/index.html`: the Pyodide demonstration page.

## Local packaging test

The GitHub workflow is intended to run online on a GitHub-hosted runner.
To create the artifacts locally, run:

```bash
python -m pip install -U pip setuptools wheel packaging
mkdir -p dist/wheels
python -m pip wheel --no-deps -w dist/wheels -r wheel-requirements.txt
python scripts/build_manifest.py dist/wheels dist/wheels.json
cp site/index.html dist/index.html
touch dist/.nojekyll
python -m http.server 8000 --directory dist
```

Visit `http://localhost:8000/`. Browser network access is required for Pyodide's CDN.
