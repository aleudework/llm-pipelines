import pandas as pd

input = '/Users/alhu/VSC/llm-pipelines/backup/faktura_effective_gpt/backup.parquet'
output = '/Users/alhu/Downloads/backup_eff_250818.xlsx'

df = pd.read_parquet(input)

df.to_excel(output, index=False)