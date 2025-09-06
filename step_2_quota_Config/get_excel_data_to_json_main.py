# any_script.py

from step_2_quota_Config.sheet_to_json import load_workbook_to_dict

url = "https://docs.google.com/spreadsheets/d/1OjOkAol3vXCbk-QPGioUAJnQgPs3t9HQ/edit?usp=sharing"
data = load_workbook_to_dict(url)
#print the names of all available sheets within the excel file 
print("Excel Sheets Names:", data.keys())      # sheet names
print(data[next(iter(data))][:3])  # first 3 rows of first sheet
