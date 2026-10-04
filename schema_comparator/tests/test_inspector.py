from schema_comparator.inspector import inspect_schema_drift

def test_schema_drift_detection(sample_datasets):
    path_a, path_b = sample_datasets
    drift = inspect_schema_drift(path_a, path_b)

    assert len(drift.added_columns) == 1
    assert drift.added_columns[0][0] == "new_col"
    assert len(drift.dropped_columns) == 0