import pandas as pd
source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
target = r"g:\Github\Automation Pivot\data\22_25.parquet"

print(f"Reading ALL sheets from {source}...")
# sheet_name=None reads all sheets into a dictionary
all_sheets = pd.read_excel(source, sheet_name=None)

combined_df = []
for sheet_name, df in all_sheets.items():
    print(f"Adding sheet: {sheet_name} ({len(df)} rows)")
    df["_source_sheet"] = sheet_name
    combined_df.append(df)

full_df = pd.concat(combined_df, ignore_index=True)
print(f"Total rows: {len(full_df)}")

print(f"Saving to {target}...")
full_df.to_parquet(target, index=False)
print("Consolidated conversion complete.")
