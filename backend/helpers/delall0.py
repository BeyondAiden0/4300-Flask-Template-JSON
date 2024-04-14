import pandas as pd

file_path = 'C:\\Users\\Kevin\\Documents\\CS4300\\finalproj\\jsonstorage\\rev.csv'

# read the CSV file
df = pd.read_csv(file_path)

# drop all rows that have a 0 for 'Rating' column
df = df[df['Rating'] != 0]

# write back to the CSV
df.to_csv(file_path, index=False)