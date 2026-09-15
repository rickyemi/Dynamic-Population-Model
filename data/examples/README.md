# Example data

Small, shareable inputs so the pipelines can be run without a real export.

Prefer generating inputs over committing them: each pipeline builds its own synthetic workbooks in
its self test, which is why `dpm self-test` needs nothing in this folder.

    dpm self-test                      # all three pipelines on generated data
    dpm self-test --pipeline dual-use  # just one

Anything placed here is tracked by git and therefore public. Check before adding.
