# How to publish this to GitHub

The repository `https://github.com/rickyemi/Dynamic-Population-Model` is empty, so this is the
initial commit. Run these from the folder containing this file's parent (the repo root).

## Option A, command line

```bash
cd Dynamic-Population-Model

git init
git branch -M main
git add .
git commit -m "Add relapse calculation and population extrapolation pipeline

Notebook and command line module for the two DPM workflows, with mock-data
self tests, an example Workflow 1 output, and setup documentation."

git remote add origin https://github.com/rickyemi/Dynamic-Population-Model.git
git push -u origin main
```

Git will prompt for credentials on the push. Use a personal access token rather than a password:
GitHub, Settings, Developer settings, Personal access tokens, with `repo` scope.

## Option B, browser upload

1. Open the repository, then **uploading an existing file**.
2. Drag the whole folder in. GitHub keeps the folder structure.
3. Commit to `main`.

The browser route does not preserve an empty folder, which does not matter here since every folder
has a file in it.

## Before you push

- **Check the example workbook.** `data/examples/DetailedModelResults_Relapse_Calculations.xlsx`
  contains named product model output, and this repository is public. Confirm the product name and
  the survivor counts may be disclosed, or swap in a de-identified export.
- **Decide the licence.** No `LICENSE` file is included. Without one, default copyright applies and
  nobody may reuse the code, which may or may not be what you want.
- **Check the configuration defaults.** The `CONFIGURATION` section of `src/relapse_popextrapolation.py`
  and the two notebook config cells contain a local Windows path with a user name in it. Harmless,
  but it is a personal detail in a public repository; every value can be passed on the command line
  instead.
- **Clear notebook outputs** if any run results are stored in the `.ipynb`. The copy here has none.

## After you push

Add a short repository description and topics (`python`, `pandas`, `openpyxl`, `epidemiology`,
`excel-automation`) so the repository is findable. Consider a GitHub Action running
`python src/relapse_popextrapolation.py --self-test` on every push: it needs no data and takes
seconds.
