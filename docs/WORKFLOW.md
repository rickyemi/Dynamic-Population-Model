# Workflow reference

## How the pieces connect

```
DPM webtool export
  DetailedModelResults_<Product>_Relapse_Calculations.xlsx
  └── tab: Detailed Results ALL.T DIFF_ALL
        │
        ▼  WORKFLOW 1  relapse_calculations()
  DetailedModelResults_Relapse_Calculations.xlsx
  ├── tab: Detailed Results ALL.T DIFF_ALL   (carried through untouched)
  ├── tab: Pivot and Calcs                   (rebuilt, live formulas)
  └── tab: Detailed Results                  (rebuilt, adjusted Mean)
        │
        │   +  PopExtractionInputs_GT.xlsx (Parameters, Births)
        ▼  WORKFLOW 2  pop_extrap()
  PopExtrapolationRes_<Product>_<DDMonYYYY>_<HHMMSS>.xlsx
  ├── tab: Metadata                          (author, version, inputs, key takeaway)
  ├── tab: Results from Python               (every row, both arms, all cohorts)
  ├── tab: Relapse                           (relapse arm, all cohorts plus Total)
  └── tab: No Relapse and final Results      (totals, with the comparison columns)
```

## Formula reference, Workflow 1

Written into the output workbook as live Excel formulas, so the sheet recalculates in Excel exactly
as the hand built version did. The same rules are evaluated in pandas and the two are cross checked
before the file is written.

| Sheet | Cell | Formula | Meaning |
|---|---|---|---|
| Pivot and Calcs | `A5` | `=G5&F5&E5` | Relapse key: model name, ERR, mortality model |
| Pivot and Calcs | `B5` | `=IF(ISNUMBER(SEARCH("G10",G5)),"G10","G25")` | Gateway |
| Pivot and Calcs | `C5` | `=IF(ISNUMBER(SEARCH("AllAge",G5)),"AllAge","TwoAge")` | Stacked type |
| Pivot and Calcs | `D5` | `=RIGHT(G5,3)` | Birth cohort |
| Pivot and Calcs | `S5` | `=ROUND(P5-H5,0)` | `(CF1-CF2)`, survivors no relapse against survivors 50% relapse |
| Pivot and Calcs | `T5` | `=ROUND(Q5-S5,0)` | `CF1-BC1-CF1+CF2`, adjusted DIFF_ALL |
| Pivot and Calcs | `V5:Y5` | `=EXACT(B5,J5)` and so on | Row alignment checks, colour coded |
| Detailed Results | `J3` | `=B3&D3&C3` | Key |
| Detailed Results | `L3` | `=ROUND(IF(ISNUMBER(SEARCH("Relapse",J3)),XLOOKUP(J3,'Pivot and Calcs'!A:A,'Pivot and Calcs'!T:T),I3),0)` | QC, the live version of the `Mean` rule |

## Comparison columns, Workflow 2

On the `No Relapse and final Results` tab, matched on `Group`, `Gateway`, `ERR` and
`Mortality.Model.Year`. `Name` is deliberately not a match key: the two arms are named differently.

```
No Relapse_Mean.extrapolated  the no relapse total
Relapse_Mean.extrapolated     the matching relapse total
Delta                         No Relapse - Relapse
To Paste in Table B2          "{Relapse:,}({gap})",  gap = -Delta
```

A relapse total sitting 3,954 above the no relapse total reads `219,825(3954)` with
`Delta = -3954`; an exact match reads `200,301(0)`. Set `PASTE_SIGNED = True` for `(+3954)`.
