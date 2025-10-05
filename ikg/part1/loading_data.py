import pandas as pd

# Path to your scraped data
input_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02.csv'  # Adjust to your file path
df = pd.read_csv(input_csv)

# Check the first few rows to confirm data structure
print(df.head())

