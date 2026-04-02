import pandas as pd
source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
xlsx = pd.ExcelFile(source)
print("Sheet Names:", xlsx.sheet_names)
