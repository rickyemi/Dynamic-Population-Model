# Data

Standard data-science layout. Nothing here except `examples/` is tracked: model exports are product
data and change on every run.

| Folder | Holds | Tracked |
|---|---|---|
| `raw/` | DPM exports exactly as downloaded from the webtool. Never edited in place | no |
| `interim/` | Intermediate workbooks, chiefly the Workflow 1 output that Workflow 2 reads | no |
| `processed/` | Final outputs: results workbooks, QC tables, figures, export bundles | no |
| `examples/` | One small, shareable workbook so the pipelines can be tried without a real export | yes |

## Expected inputs

| File | Used by | Notes |
|---|---|---|
| `DetailedModelResults_<Product>_Relapse_Calculations.xlsx` | relapse, Workflow 1 | Tab `Detailed Results ALL.T DIFF_ALL`, title in row 1, headers in row 2 |
| `PopExtractionInputs_GT.xlsx` | relapse, Workflow 2 | Tabs `Parameters` (Name / Value) and `Births` (Country, Year, Births) |
| `DetailedModelResults_<Product>_TippingPoint.xlsx` | tipping-point | Sweep runs; model names end in the swept probability |
| `DetailedModelResults_<Product>_MasterModels.xlsx` | tipping-point | B01 master models; names end in a cohort tag |
| `Dual_Use_Calculations_TwoAge_B01_<Product>_<Month>_<Day>_<Year>.xlsx` | dual-use | Tabs `Detailed Results` and `MasterModels TP-ID` |

## Before committing anything here

Run `dpm self-test` instead of committing a real export where you can: every pipeline generates its
own synthetic inputs, so a contributor never needs product data to work on the code.

If a real workbook must be committed, confirm with the owning team that the product name and the
survivor counts may be disclosed. This repository is public. The pipelines are product agnostic, so
a de-identified export (product relabelled, means resampled) exercises exactly the same code paths.
