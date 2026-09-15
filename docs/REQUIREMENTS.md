# Input requirements

Each pipeline numbers its own requirements, which is why "Model Group" is Requirement 2 for tipping
point and Requirement 3 for dual use. Every one is checked before any calculation runs, and a
failure names the file and what was expected.

## Relapse calculation and population extrapolation

| # | Requirement | Checked how |
|---|---|---|
| 1 | Workflow 1 input carries a `Detailed Results ALL.T DIFF_ALL` tab, title in row 1, headers in row 2 | Header row located by searching for `Model Group`, so a shifted title is tolerated |
| 2 | Workflow 2 input 1 is `PopExtractionInputs_GT.xlsx` with tabs `Parameters` (Name / Value) and `Births` (Country, Year, Births) | Missing column raises by name |
| 3 | `Model Group` reads `<Product>_<analyst initials>` | Product cross-checked against the file name, ignoring case and separators |

Model naming inside the export:

| Field | Convention | Example |
|---|---|---|
| Relapse model | name contains `Relapse` | `Master Model G10 Grizzly XL Relapse_TwoAge_B01` |
| Master model | no relapse wording | `Master Model G10 Grizzly XL_TwoAge_5a_6a_14b_15a_B01` |
| Birth cohort | last 4 characters, ending in 2 digits | `_B01` |
| Gateway | `G10` or `G25` in the name | |
| Mortality model | `<Source>_<Sex>_<Year>` | `JAGS_Male_2000` |

## Tipping point 1D plotting

| # | Requirement | Notes |
|---|---|---|
| 1 | `DetailedModelResults_<Product>_TippingPoint.xlsx` and `DetailedModelResults_<Product>_MasterModels.xlsx` | Exactly one of each in the folder, same product spelling in both |
| 2 | `Model Group` reads `<Product>_<analyst initials>` | Supplies the initials printed on the report |

Roles are additionally confirmed from the contents: a sweep file's model names end in the swept
probability, a master model file's end in a cohort tag such as `B01`. This is what catches two
workbooks saved under each other's names, which otherwise surfaces much later as
`rows have an unparseable swept probability`, because `B01` is not a number.

Separators are normalised before matching, so an export writing `JAGS Male 2000` and `DIFF ALL`
reads identically to one writing `JAGS_Male_2000` and `DIFF_ALL`. `Age Range` values keep their
spacing, because `68 - 72` is a printed range rather than an identifier.

## Dual use calculation optimizer

| # | Requirement | Notes |
|---|---|---|
| 1 | `Dual_Use_Calculations_TwoAge_B01_<Product>_<Month>_<Day>_<Year>.xlsx` | The product and run date are read from the name |
| 2 | A `Detailed Results` tab and a `MasterModels TP-ID` tab | Matched on letters and digits only, so `Raw Detailed Results` and `MasterModels TP-1D` both qualify: the digit one and the letter I are indistinguishable in most fonts |
| 3 | `Model Group` reads `<Product>_<analyst initials>` | Enforced on the master models tab, which is the one carrying the convention. A non conforming `Detailed Results` group warns rather than stopping, because the dual use runs legitimately sit in their own model group. `STRICT_MODEL_GROUP = True` makes it an error |

Required per gateway and sex: ERRs 0.05, 0.10, 1.05 and 1.10 in `Detailed Results`, and 0.05 and
0.10 in `MasterModels TP-ID`. A missing or duplicated run raises rather than silently changing a
result.
