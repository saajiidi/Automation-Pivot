import pandas as pd
import os

source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
target = r"g:\Github\Automation Pivot\data\22_25.parquet"

print(f"Reading {source}...")
df = pd.read_excel(source)
print(f"Read {len(df)} rows.")

print(f"Saving to {target}...")
df.to_parquet(target, index=False)
print("Conversion complete.")
