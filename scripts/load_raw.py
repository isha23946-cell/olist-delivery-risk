import duckdb
from pathlib import Path

con = duckdb.connect("warehouse/olist.duckdb")
for f in sorted(Path("data/raw").glob("*.csv")):
    name = "raw_" + f.stem.replace("olist_", "").replace("_dataset", "")
    con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{f}', all_varchar=true)")
    rows = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"{name}: {rows} rows")
con.close()
