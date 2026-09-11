# Dynamic Population Model, relapse calculation and population extrapolation

Python replacements for two manually maintained Excel deliverables in the Disease Progression Model
(DPM) reporting chain. Both read the DPM exports directly, apply the documented rules without
transcription, and write dated, versioned output workbooks.

**Author:** YO · **Pipeline version:** 3.0 · **Status:** Implemented

---

## What this does

| Workflow | Reads | Writes |
|---|---|---|
| **1. Relapse calculation** | `Detailed Results ALL.T DIFF_ALL` tab of a DPM export | `DetailedModelResults_Relapse_Calculations.xlsx`, with the source tab plus rebuilt `Pivot and Calcs` and `Detailed Results` tabs |
| **2. Population extrapolation** | `PopExtractionInputs_GT.xlsx` and the Workflow 1 output | `PopExtrapolationRes_<Product>_<DDMonYYYY>_<HHMMSS>.xlsx`, four tabs |

The two workflows communicate through a file on disk, not through Python objects. Either runs on
its own, and Workflow 2 can be pointed at a workbook produced weeks earlier.

### Workflow 1, in brief

Builds the relapse pivot and the master model pivot from the export, aligns them row for row on
gateway, stacked type, birth cohort, mortality model and ERR, then applies:

```
(CF1-CF2)        S = master ALL.T - relapse ALL.T
CF1-BC1-CF1+CF2  T = master DIFF_ALL - S
Mean             relapse rows take T via XLOOKUP on the key; all others keep the webtool mean
```

Both pivot blocks carry four `EXACT()` checks confirming they stayed aligned. These are written as
live Excel formulas and colour coded, green for TRUE and red for FALSE.

### Workflow 2, in brief

```
Mean.extrapolated = round( (Male x (1 - female_prop) + Female x female_prop)
                           x sum.births / pop_size , 0 )
```

The sex-weighted mean is a rate per simulated person; multiplying by the real births in each birth
cohort and dividing by the simulated population size rescales it to the actual population. Totals
per model are then compared across the relapse and no relapse arms.

---

## Repository layout

```
├── notebooks/
│   └── Relapse_Calculation_and_PopExtrapolation.ipynb   the documented, runnable notebook
├── src/
│   └── relapse_popextrapolation.py                      command line equivalent, generated from
│                                                        the notebook so the two cannot drift
├── data/
│   ├── README.md                                        where to put your exports
│   └── examples/
│       └── DetailedModelResults_Relapse_Calculations.xlsx   a Workflow 1 output, input 2 of
│                                                            Workflow 2
├── requirements.txt
├── CHANGELOG.md
└── README.md
```

---

## Requirements

- **Python 3.11 or later.** Windows 64-bit, macOS or Linux.
- **Packages:** `pandas`, `numpy`, `openpyxl`. Add `notebook` to run the `.ipynb`.
- **No** add-ins, macros, database connections or internet access at run time.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS, Linux
pip install -r requirements.txt
```

---

## Input requirements

### File and tab names

| Item | Requirement |
|---|---|
| Workflow 1 input | Any `.xlsx` carrying a `Detailed Results ALL.T DIFF_ALL` tab. Title in row 1, column headers in row 2 |
| Workflow 2 input 1 | `PopExtractionInputs_GT.xlsx`, tabs `Parameters` (Name / Value pairs) and `Births` (Country, Year, Births) |
| Workflow 2 input 2 | The Workflow 1 output, tab `Detailed Results` |

### Model naming

| Field | Convention | Example |
|---|---|---|
| `Model Group` | `<Product>_<analyst initials>` | `Grizzly_XL_YO` |
| Relapse model name | contains `Relapse` | `Master Model G10 Grizzly XL Relapse_TwoAge_B01` |
| Master model name | no relapse wording | `Master Model G10 Grizzly XL_TwoAge_5a_6a_14b_15a_B01` |
| Birth cohort | last 4 characters of the model name, ending in 2 digits | `_B01` |
| Mortality model | `<Source>_<Sex>_<Year>` | `JAGS_Male_2000` |

The product is read from `Model Group`, so `Grizzly_XL_YO` gives `Grizzly_XL` and `Velo Max YO`
gives `Velo_Max`. Matching is whitespace agnostic: `Grizzly XL`, `Grizzly_XL` and `grizzly xl` are
treated as the same product. Nothing in the code is specific to any one product.

---

## Usage

### Notebook

Open `notebooks/Relapse_Calculation_and_PopExtrapolation.ipynb`, set the folder in the
configuration cell of each workflow, then Run All.

### Command line

```bash
# Both workflows, defaults from the CONFIGURATION section of the module
python src/relapse_popextrapolation.py --workflow both --dir "C:/path/to/exports"

# Workflow 1 only, naming the files explicitly
python src/relapse_popextrapolation.py --workflow 1 --dir ./data \
    --relapse-input  DetailedModelResults_Grizzly_Relapse_Calculations.xlsx \
    --relapse-output DetailedModelResults_Relapse_Calculations.xlsx

# Workflow 2 only
python src/relapse_popextrapolation.py --workflow 2 --dir ./data \
    --params-input   PopExtractionInputs_GT.xlsx \
    --relapse-output DetailedModelResults_Relapse_Calculations.xlsx \
    --author "YO"

python src/relapse_popextrapolation.py --help
```

### Verify the install

```bash
python src/relapse_popextrapolation.py --self-test
```

This builds synthetic exports with the same tab names, column names and naming convention as the
real files, runs both workflows over them, and asserts the results. It needs no real export, so it
is what to run first on a new machine and what a CI job should run on every commit. Expect
`Both self tests passed.`

---

## Validation built into every run

Neither workflow returns a silently wrong number; each stops with a named error instead.

| Check | Behaviour on failure |
|---|---|
| Relapse and master pivot rows line up | Raises, printing the offending rows |
| One pivot row per gateway, stacked type, birth cohort, mortality model and ERR | Raises on a duplicate webtool run |
| Every relapse key resolves in the pivot | Raises, listing unmatched keys |
| Both sexes present for the same mortality model year | Raises |
| Births cover every year in the age range | Warns, since cohort totals would be understated |
| `Relapse.Status` has both levels | Warns if either is empty, which signals a naming change |
| One Relapse total per No Relapse total | Raises on a duplicate; retries without `Model Group` before giving up |
| `Delta` reconciles to the two mean columns | Raises |

---

## Known behaviour worth understanding

- **Survivor counts are whole numbers**, rounded in the pandas frame and in the Excel formula
  together, so the sheet recalculates to the value the frame holds. `W1_WHOLE_NUMBERS = False`
  keeps full precision. Because `Mean` is what Workflow 2 reads, rounding moves the extrapolated
  totals by a fraction of a case in numbers of the order of a million.
- **`Mean` is written as a value, `QC` as the equivalent formula.** pandas reads an uncalculated
  Excel formula as empty, so the column Workflow 2 depends on has to hold a value. Opening the
  workbook in Excel then gives a free cross-check of the Python value against the Excel rule.
- **Each interpolation formula points at its own header row**, unlike the legacy workbook where
  every one pointed at row 12 including the block 22 rows below. Same numbers, no cross-block
  dependency.
- **A tipping point or comparison shown as `<` or `>`** means the curve does not cross inside the
  swept range. That is a result, not an error.

---

## Troubleshooting

| Message | Cause and fix |
|---|---|
| `Duplicate rows for the same model / sex / cohort / ERR` | A model was run twice in the webtool. The error names the offending models; delete the replicates from the export. |
| `Relapse.Status must have exactly two levels` | Model naming changed. Pass `classify_columns=("Group",)` or adjust `RELAPSE_PATTERN`. |
| `More than one Relapse total shares the same [...]` | Two relapse models collapse onto one match key. Rerun with an extra key via `match_keys`. |
| `Every 'Mean' value in 'Detailed Results' is empty` | The results workbook holds an uncalculated formula in that column. Open it in Excel, save, and rerun, or regenerate it with Workflow 1. |
| `Births missing for N year(s)` | The `Births` tab does not cover the full age range; cohort totals are understated until it does. |
| `Permission denied` when writing | An output workbook is open in Excel. Close it and rerun. |

---

## Contributing

The `.py` module is **generated from the notebook**. Change the notebook first, then regenerate,
so the two never diverge. Run `--self-test` before committing.

## Licence

No licence file is included. Model outputs and naming conventions in this repository derive from
internal work, so confirm the intended licence and the publication status of any committed data
with the owning team before adding one. Until then, default copyright applies and no reuse rights
are granted.
