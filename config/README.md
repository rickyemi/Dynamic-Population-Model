# Configuration

`config.example.toml` is tracked; copy it to `config.toml`, which is gitignored, so your local
paths never reach the repository.

```bash
cp config/config.example.toml config/config.toml
```

## Precedence

Lowest to highest:

1. **Module defaults** in the `CONFIGURATION` section of each pipeline module. These mirror the
   notebook's configuration cell, so a notebook run and a bare `dpm` run behave the same.
2. **`config/config.toml`**, if present. Relative paths here resolve against the repository root,
   so `data/raw` works on any machine.
3. **`DPM_*` environment variables**: `DPM_DATA_DIR`, `DPM_OUT_DIR`, `DPM_AUTHOR`, `DPM_PRODUCT`,
   and `DPM_CONFIG` to point at a different config file. Useful in CI and scheduled runs.
4. **Command line arguments**, which always win. Relative paths here resolve against your current
   directory, the way every other command line tool behaves.

No config file is needed to run anything: `dpm self-test` works on a fresh clone.

## A note on `product`

Leave it unset. The product is read from the `Model Group` column and cross-checked against the
file name, so the label on the output cannot disagree with the data it came from. Setting it here
only overrides the label, and a value that contradicts the file raises rather than mislabelling the
output.
