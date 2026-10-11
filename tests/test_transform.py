import numpy as np
import pytest
from pydantic import ValidationError

from taketwo.dataset.errors import DatasetError
from taketwo.dataset.schema import Operation, Recipe
from taketwo.dataset.storage import load
from taketwo.dataset.transform import apply_recipe, remap_interval
from taketwo.dataset.validation import validate
from taketwo.dataset.workspace import generate


def recipe(kind, start, end, value):
    return Recipe(
        seed=17,
        operations=[Operation(kind=kind, start_s=start, end_s=end, value=value, severity=2)],
    )


@pytest.mark.parametrize(
    "kind,start,end,value",
    [
        ("insert_pause", 0.5, 0.75, 0.2),
        ("shorten_pause", 0.5, 0.75, 0.25),
        ("tempo", 0.8, 1.8, 1.5),
        ("tempo", 0.8, 1.8, 0.75),
        ("gain", 0.8, 1.8, 0.5),
        ("pitch_shift", 0.8, 1.8, 2.0),
    ],
)
def test_edit_reproducibility_and_outside_samples(signal, kind, start, end, value):
    configuration = recipe(kind, start, end, value)
    left, mapping, regions = apply_recipe(signal, configuration)
    right, mapping2, regions2 = apply_recipe(signal, configuration)
    np.testing.assert_array_equal(left, right)
    np.testing.assert_array_equal(left[: round(start * 16000)], signal[: round(start * 16000)])
    np.testing.assert_array_equal(left[-3200:], signal[-3200:])
    assert mapping == mapping2 and regions == regions2
    assert np.isfinite(left).all() and np.max(np.abs(left)) < 1
    if kind == "tempo":
        assert abs(len(left) - (len(signal) - 16000 + round(16000 / value))) <= 1
        # Dominant frequency remains near 220 Hz, rather than shifting with speed.
        section = left[regions[0][0] + 512 : regions[0][1] - 512]
        frequency = np.argmax(abs(np.fft.rfft(section))) * 16000 / len(section)
        assert abs(frequency - 220) < 5


def test_sample_exact_remapping(signal):
    _, mapping, _ = apply_recipe(signal, recipe("insert_pause", 0.5, 0.75, 0.2))
    assert remap_interval(1.0, 1.5, mapping) == pytest.approx((1.2, 1.7))
    assert remap_interval(0.4, 0.6, mapping) == pytest.approx((0.4, 0.8))
    _, mapping, _ = apply_recipe(signal, recipe("tempo", 0.8, 1.8, 2.0))
    assert remap_interval(1.0, 1.4, mapping) == pytest.approx((0.9, 1.1))
    _, mapping, _ = apply_recipe(signal, recipe("shorten_pause", 0.5, 0.75, 0.5))
    assert remap_interval(1.0, 1.5, mapping) == pytest.approx((0.875, 1.375))


def test_combined_edits_and_generated_labels(imported):
    root, reference = imported
    configuration = Recipe(
        seed=12,
        operations=[
            Operation(kind="insert_pause", start_s=0.5, end_s=0.75, value=0.2, severity=1),
            Operation(kind="tempo", start_s=0.8, end_s=1.3, value=1.5, severity=3),
            Operation(kind="gain", start_s=1.4, end_s=1.9, value=0.5, severity=2),
        ],
    )
    generated = generate(root, reference.id, configuration)
    state = load(root)
    assert generated.origin == "synthetic" and len(state.annotations) == 3
    assert state.pairs[0].intended_severity == 3
    assert all(
        a.source == "synthetic_recipe"
        and a.review_status == "unreviewed"
        and a.uncertainty_s is None
        and a.reviewer_id is None
        for a in state.annotations
    )
    labels = {a.category: a for a in state.annotations}
    assert labels["pause_behavior"].start_s == 0.5
    assert labels["pacing"].start_s == pytest.approx(1.0)
    assert validate(state, root, reproduce=True)["valid"]
    with pytest.raises(DatasetError, match="already exists"):
        generate(root, reference.id, configuration)


@pytest.mark.parametrize(
    "kind,start,end,value",
    [
        ("shorten_pause", 0.1, 0.4, 0.5),
        ("insert_pause", 0.1, 0.4, 0.5),
        ("gain", 0.0, 2.0, 0.5),
        ("pitch_shift", 0.0, 2.0, 2.0),
        ("tempo", 1.0, 3.0, 1.5),
        ("pitch_shift", 0.1, 0.15, 2.0),
    ],
)
def test_unreliable_transform_rejected(signal, kind, start, end, value):
    with pytest.raises(DatasetError):
        apply_recipe(signal, recipe(kind, start, end, value))


def test_output_clipping_rejected():
    x = np.full(16000, 0.5, np.float32)
    with pytest.raises(DatasetError, match="clipping"):
        apply_recipe(x, recipe("gain", 0.2, 0.8, 3.0))


def test_invalid_operations():
    with pytest.raises(ValidationError):
        recipe("tempo", 0.1, 0.5, 1.0)
    with pytest.raises(ValidationError):
        Recipe(
            seed=1,
            operations=[
                Operation(kind="gain", start_s=0.1, end_s=1.0, value=0.5, severity=1),
                Operation(kind="gain", start_s=0.5, end_s=1.5, value=0.5, severity=1),
            ],
        )
