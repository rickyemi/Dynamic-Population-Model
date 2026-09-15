"""Dynamic Population Model, analysis pipelines.

Three pipelines that replace manually maintained Excel and R deliverables in the DPM reporting
chain. Each reads the model exports directly, applies the documented rules without transcription,
and writes dated, versioned output.

    from dpm import relapse_popextrapolation, tipping_point_plotting, dual_use_optimizer

The submodules are generated from the notebooks in ``notebooks/`` by ``tools/nb_to_module.py``, so
the notebook and the module cannot drift apart. Edit the notebook, then regenerate.

Importing a submodule is side effect free: nothing reads a workbook or writes a file until one of
the entry points is called.
"""

__version__ = "3.0.0"
__author__ = "YO"

__all__ = ["relapse_popextrapolation", "tipping_point_plotting", "dual_use_optimizer",
           "config", "cli", "__version__"]
