import pandas as pd
import sys

source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
target = r"g:\Github\Automation Pivot\data\22_25.parquet"

try:
    print(f"Loading workbook: {source}")
    xlsx = pd.ExcelFile(source)
    sheet_names = xlsx.sheet_names
    print(f"Sheets found: {sheet_names}")

    combined_dfs = []
    for sheet in sheet_names:
        print(f"Reading sheet: {sheet}...")
        df = pd.read_excel(xlsx, sheet_name=sheet)
        if not df.empty:
            df["_source_sheet"] = str(sheet)
            # Standardize column types to string for mixed-type objects to avoid Parquet schema errors
            for col in df.columns:
                 if df[col].dtype == object:
                     df[col] = df[col].astype(str).replace('nan', '')
            combined_dfs.append(df)
        print(f"  Added {len(df)} rows.")

    if not combined_dfs:
        print("Error: No data found in any sheet.")
        sys.exit(1)

    print("Concatenating all sheets...")
    full_df = pd.concat(combined_dfs, ignore_index=True, sort=False)
    
    print(f"Final dataset: {len(full_df)} rows, {len(full_df.columns)} columns.")
    print(f"Writing to {target}...")
    full_df.to_parquet(target, index=False, engine='pyarrow')
    print("Consolidated Parquet conversion complete.")

except Exception as e:
    print(f"CRITICAL ERROR during conversion: {e}")
    sys.exit(1)
