"""Tipping point calculation and figure generation on synthetic sweeps.

The interpolation tests matter more than they look: the legacy R script assumed survivors always
fall as the swept probability rises, which reports the wrong side of the range for a rising curve.
Both directions are asserted here so that regression cannot come back unnoticed.
"""
from __future__ import annotations

import numpy as np
import pytest

from dpm import tipping_point_plotting as tp


def test_self_test(workdir):
    tp.self_test(workdir / "st")


def test_tipping_point_interpolates_the_crossing():
    """A straight line from +100 to -100 over 0 to 10 crosses at 5."""
    prob = np.array([0.0, 2.5, 5.0, 7.5, 10.0])
    values = np.array([100.0, 50.0, 0.0, -50.0, -100.0])
    label, slope = tp.tipping_point(prob, values, 0.0)
    assert not isinstance(label, str)
    assert label == pytest.approx(5.0, abs=1e-6)
    assert slope < 0


def test_falling_positive_curve_crosses_above_the_range():
    """Never reaches zero inside the sweep, and falls, so the crossing is beyond the top."""
    label, _ = tp.tipping_point(np.array([0.0, 50.0, 100.0]), np.array([900.0, 600.0, 300.0]))
    assert isinstance(label, str) and label.startswith(">")


def test_rising_positive_curve_crosses_below_the_range():
    """The direction the R original got backwards."""
    label, _ = tp.tipping_point(np.array([0.0, 2.5, 5.0]), np.array([300.0, 600.0, 900.0]))
    assert isinstance(label, str) and label.startswith("<")


def test_r_signif_rounds_to_significant_digits():
    """R's signif(), not Python's round(): signif(10.23, 3) is 10.2, round(10.23, 3) is 10.23."""
    assert tp.r_signif(10.2345, 3) == 10.2
    assert tp.r_signif(0.00123456, 3) == 0.00123
    assert tp.r_signif(0.0, 3) == 0.0


def test_separator_normalisation_handles_both_spellings():
    """Some exports write 'JAGS Male 2000', others 'JAGS_Male_2000'."""
    assert tp.normalise_separators("JAGS Male 2000") == "JAGS_Male_2000"
    assert tp.normalise_separators("JAGS_Male_2000") == "JAGS_Male_2000"
    assert tp.same_label("DIFF ALL", "DIFF_ALL")


def test_model_group_split_requires_initials():
    """Model Group must read '<Product>_<initials>'. It is Requirement 2 in this pipeline and
    Requirement 3 in the dual use one, because each tool numbers its own requirement list."""
    assert tp.split_model_group("Product_X_YO") == ("Product_X", "YO")
    assert tp.split_model_group("Grizzly XL YO") == ("Grizzly_XL", "YO")
    with pytest.raises(ValueError, match="Requirement 2"):
        tp.split_model_group("ProductX")


def test_swapped_inputs_are_rejected(workdir):
    """A MasterModels file named as a TippingPoint file must stop, not fail deep in the run."""
    folder = workdir / "swapped"
    tp.build_self_test_inputs(folder)
    tag = tp.SELF_TEST_PRODUCT
    sweeps = folder / f"DetailedModelResults_{tag}_TippingPoint.xlsx"
    masters = folder / f"DetailedModelResults_{tag}_MasterModels.xlsx"
    tmp = folder / "tmp.xlsx"
    sweeps.rename(tmp); masters.rename(sweeps); tmp.rename(masters)

    with pytest.raises(ValueError, match="do not hold what their names claim"):
        tp.resolve_inputs(folder)
