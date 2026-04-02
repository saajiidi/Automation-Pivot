import pandas as pd
import sys

source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
target = r"g:\Github\Automation Pivot\data\22_25.parquet"

try:
    print(f"Loading workbook engine: {source}")
    xlsx = pd.ExcelFile(source)
    sheet_names = xlsx.sheet_names
    print(f"Sheets identified: {sheet_names}")

    combined_dfs = []
    for sheet in sheet_names:
        print(f"Processing sheet: {sheet}...")
        df = pd.read_excel(xlsx, sheet_name=sheet)
        if not df.empty:
            df["_source_sheet"] = str(sheet)
            # Ensure every single cell is treated as a string to bypass pyarrow schema inference failures
            df = df.astype(str)
            combined_dfs.append(df)
            print(f"  Added {len(df)} rows.")

    if not combined_dfs:
        print("Error: No data to process.")
        sys.exit(1)

    print("Merging all gathered data...")
    full_df = pd.concat(combined_dfs, ignore_index=True)
    
    print(f"Final dataset: {len(full_df)} rows, {len(full_df.columns)} columns.")
    print(f"Serializing to Parquet: {target}...")
    full_df.to_parquet(target, index=False, engine='pyarrow')
    print("Consolidated ALL-SHEETS Parquet conversion complete.")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
