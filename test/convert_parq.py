import pandas as pd

input = '/Users/alhu/VSC/llm-pipelines/backup/faktura_advanced_chat/backup.parquet'
output = '/Users/alhu/Data/Archive/View_Backup.xlsx'

df = pd.read_parquet(input)

df.to_excel(output, index=False)