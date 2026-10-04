from schema_comparator.cdc_engine import compute_cdc

def test_cdc_counts(sample_datasets):
    path_a, path_b = sample_datasets
    cdc = compute_cdc(path_a, path_b, primary_keys=["id"])

    assert cdc.count_inserts == 1
    assert cdc.count_updates == 1
    assert cdc.count_deletes == 1
    assert cdc.count_unchanged == 1