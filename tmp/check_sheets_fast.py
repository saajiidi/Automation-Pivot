import openpyxl
source = r"g:\Github\Automation Pivot\data\22_25.xlsx"
wb = openpyxl.load_workbook(source, read_only=True)
print("Sheet Names:", wb.sheetnames)
