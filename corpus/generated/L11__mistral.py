import polars as pl

def compare_snapshots(snapshot1_path, snapshot2_path, diff_path):
    # Load snapshots
    snapshot1 = pl.read_csv(snapshot1_path)
    snapshot2 = pl.read_csv(snapshot2_path)

    # Ensure both snapshots have the same columns
    snapshot1 = snapshot1.drop_nulls()
    snapshot2 = snapshot2.drop_nulls()

    # Merge the snapshots and compute the differences
    merged_snapshot = snapshot1.merge(snapshot2, on='key')
    added = merged_snapshot.filter(pl.col('_ merged').eq(1) & snapshot1.filter(pl.col('key').is_null()).shape.rows > 0)
    removed = merged_snapshot.filter(pl.col('_ merged').eq(2) & snapshot2.filter(pl.col('key').is_null()).shape.rows > 0)
    changed = merged_snapshot.filter(pl.col('_ merged').eq(3) & (snapshot1['value'] != snapshot2['value']))

    # Save the differences to a CSV file
    added.write_csv(diff_path + '_added.csv')
    removed.write_csv(diff_path + '_removed.csv')
    changed.write_csv(diff_path + '_changed.csv')

# Example usage
compare_snapshots('snapshot1.csv', 'snapshot2.csv', 'comparison_result')
