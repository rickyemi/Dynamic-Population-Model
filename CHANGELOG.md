# Changelog

All notable changes to this repository are recorded here. Versions follow the pipeline version
printed on the metadata cover sheet of each output workbook.

## [3.0] - 2026-09-04

### Added
- Workflow 1, relapse calculation: rebuilds `Pivot and Calcs` and `Detailed Results` from the DPM
  export and writes them as live Excel formulas.
- Workflow 2, population extrapolation: four-tab results workbook with a metadata cover sheet.
- `src/relapse_popextrapolation.py`, a command line equivalent of the notebook with a `--self-test`
  that runs both workflows on mock data.
- Mock data self tests for both workflows, requiring no real export.

### Changed
- Survivor counts are rounded to whole numbers in the frame and in the Excel formula together
  (`=ROUND(P5-H5,0)` rather than `=(P5-H5)`), so the sheet recalculates to the value the frame
  holds. Applies to `ALL.T`, `DIFF_ALL`, `(CF1-CF2)`, the adjusted results, `Mean_Webtool`, `Mean`
  and `QC`.
- The four `EXACT()` row-alignment checks are colour coded, green for TRUE and red for FALSE,
  through conditional formatting rather than fixed fills.

### Fixed
- Column `V` of `Pivot and Calcs` referenced the row below in the legacy workbook
  (`=EXACT(B6,J6)` on row 5), a fill-handle artefact that no visual check would catch. Now aligned.
- Master model means were pasted rounded into the legacy comparison, costing 0.02 percentage points
  on `% change`. The rounding is now applied consistently at both ends.
- Relapse status is a strict two-level categorical. The previous rule raised on any model whose
  name carried no relapse wording, which is the normal case for the no relapse arm.
