import pandas as pd

input = '/Users/alexander/Downloads/backup250621.parquet'
output = '/Users/alexander/Downloads/backup250621.xlsx'

df = pd.read_parquet(input)

df.to_excel(output, index=False)