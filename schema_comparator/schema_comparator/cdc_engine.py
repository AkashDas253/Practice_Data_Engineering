from dataclasses import dataclass
from typing import List
import duckdb
import pyarrow as pa
from schema_comparator.readers import get_reader

@dataclass
class CDCResult:
    count_inserts: int
    count_updates: int
    count_deletes: int
    count_unchanged: int
    delta_table: pa.Table

def compute_cdc(source_a: str, source_b: str, primary_keys: List[str]) -> CDCResult:
    conn = duckdb.connect()
    
    rel_a = get_reader(source_a).get_relation(conn)
    rel_b = get_reader(source_b).get_relation(conn)

    rel_a.create_view("table_a")
    rel_b.create_view("table_b")

    cols_a = rel_a.columns
    cols_b = rel_b.columns
    non_key_cols = [c for c in cols_a if c in cols_b and c not in primary_keys]

    key_join = " AND ".join([f"a.{k} = b.{k}" for k in primary_keys])
    
    # Hash expressions for fast comparison
    if non_key_cols:
        concat_a = ", ".join([f"COALESCE(CAST(a.{c} AS VARCHAR), '')" for c in non_key_cols])
        concat_b = ", ".join([f"COALESCE(CAST(b.{c} AS VARCHAR), '')" for c in non_key_cols])
        payload_hash_a = f"md5(concat({concat_a}))"
        payload_hash_b = f"md5(concat({concat_b}))"
    else:
        payload_hash_a = "'1'"
        payload_hash_b = "'1'"

    cdc_query = f"""
    WITH diff_matrix AS (
        SELECT 
            COALESCE(a.{primary_keys[0]}, b.{primary_keys[0]}) AS _pk,
            CASE 
                WHEN a.{primary_keys[0]} IS NULL THEN 'INSERT'
                WHEN b.{primary_keys[0]} IS NULL THEN 'DELETE'
                WHEN {payload_hash_a} != {payload_hash_b} THEN 'UPDATE'
                ELSE 'UNCHANGED'
            END AS _change_type,
            b.*
        FROM table_a a
        FULL OUTER JOIN table_b b ON {key_join}
    )
    SELECT * FROM diff_matrix
    """
    
    res_relation = conn.sql(cdc_query)
    delta_table = res_relation.to_arrow_table()

    counts = conn.sql("""
        SELECT _change_type, COUNT(*) as cnt 
        FROM res_relation 
        GROUP BY _change_type
    """).fetchall()

    counts_dict = {row[0]: row[1] for row in counts}

    return CDCResult(
        count_inserts=counts_dict.get("INSERT", 0),
        count_updates=counts_dict.get("UPDATE", 0),
        count_deletes=counts_dict.get("DELETE", 0),
        count_unchanged=counts_dict.get("UNCHANGED", 0),
        delta_table=delta_table
    )