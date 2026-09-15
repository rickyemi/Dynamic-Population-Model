# Data dictionary

Every column the pipelines read from the DPM exports and write to their outputs.

## Read from a DPM export

| Column | Type | Meaning | Used for |
|---|---|---|---|
| `Model Group` | text | `<Product>_<analyst initials>` | Product resolution and the requirement check |
| `Model Name` | text | Full model identifier | Gateway, birth cohort, sub question, swept probability, relapse or master |
| `Mortality Model` | text | `<Source>_<Sex>_<Year>`, e.g. `JAGS_Male_2000` | Sex and mortality model year |
| `ERR` | number | Excess relative risk | Facet and join key; normalised to two decimals |
| `Age Range` | text | e.g. `68 - 72` | Filter. Spacing preserved: it is a printed range, not an identifier |
| `Node` | text | `ALL.T` (survivors) or `DIFF_ALL` (difference) | Filter and pivot value |
| `Mean` | number | Model result for that node | Every downstream calculation |
| `95% PI` | number | Lower posterior bound | Tipping point interval curves |
| *(unnamed)* | number | Upper posterior bound. The DPM leaves the header blank; renamed `95% PI2` by position | Tipping point interval curves |

## Derived inside the pipelines

| Column | Derivation | Notes |
|---|---|---|
| `Gateway` | `G10` or `G25` found in the model name | Panel and join key |
| `Birth.Cohort` | Last 2 characters of the model name, as an integer | `Total` rows carry the string `Total` |
| `SubQ` | `_5a_`, `_6a_`, `_14b_` or `_15a_` tag in the model name | Selects the transition |
| `Prob` | Trailing token of the model name | The swept probability, stored as a fraction |
| `Relapse.Status` | `Relapse` when the group or name matches "relapse" and not a negated form, else `No Relapse` | Strict two-level categorical |
| `Mean.extrapolated` | `round((Male x (1 - female_prop) + Female x female_prop) x sum.births / pop_size, 0)` | Whole survivors |

## Written to `Pivot and Calcs`

| Column | Formula in the sheet | Meaning |
|---|---|---|
| `Relapse Key` | `=G5&F5&E5` | Model name, ERR, mortality model |
| `Gateway` | `=IF(ISNUMBER(SEARCH("G10",G5)),"G10","G25")` | |
| `Stacked Type` | `=IF(ISNUMBER(SEARCH("AllAge",G5)),"AllAge","TwoAge")` | |
| `Birth Cohort` | `=RIGHT(G5,3)` | e.g. `B01` |
| `ALL.T` | value | Max of Mean at the `ALL.T` node, whole numbers |
| `DIFF_ALL` | value | Max of Mean at the `DIFF_ALL` node, whole numbers |
| `(CF1-CF2)` | `=ROUND(P5-H5,0)` | Survivors no relapse against survivors 50% relapse |
| `CF1-BC1-CF1+CF2` | `=ROUND(Q5-S5,0)` | Adjusted `DIFF_ALL` |
| Checks, `V:Y` | `=EXACT(B5,J5)` and three like it | Row alignment; green TRUE, red FALSE |

## Written to `Detailed Results`

| Column | Source | Notes |
|---|---|---|
| `Mean_Webtool` | The export's original `Mean` | Kept so the adjustment is auditable |
| `Key` | `=B3&D3&C3` | Model name, ERR, mortality model |
| `Mean` | Value: relapse rows take the adjusted result, others keep the webtool mean | Written as a **value**, since pandas reads an uncalculated formula as empty and Workflow 2 depends on this column |
| `QC` | `=ROUND(IF(ISNUMBER(SEARCH("Relapse",J3)),XLOOKUP(...),I3),0)` | The same rule as a live formula, so opening in Excel cross-checks `Mean` |

## Written to the extrapolation results workbook

| Tab | Contents |
|---|---|
| `Metadata` | Author, initials, version, environment, filters, objective, inputs, outputs, generated key takeaway |
| `Results from Python` | Every row, both arms, all birth cohorts plus `Total` |
| `Relapse` | The relapse arm, all cohorts plus `Total` |
| `No Relapse and final Results` | No relapse totals with `Relapse_Mean.extrapolated`, `Delta` and `To Paste in Table B2` |

`To Paste in Table B2` renders as `219,825(3954)`: the relapse total, with the gap to the no relapse
total in brackets. `Delta` is no relapse minus relapse, so the bracketed figure is its negative.
Set `PASTE_SIGNED = True` for `(+3954)`.
