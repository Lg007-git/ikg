import json
import pandas as pd
import re
import os

# Input file path
input_file = r'D:\Scrapping\twitter_scrapping\without_ai_cleaning\output1.txt'

# Output folder path
output_folder = r'D:\Scrapping\twitter_scrapping\ikg\part1'

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

texts = []
json_dicts = []

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'"(.*?)",```json\s*(\{.*?\})\s*```'
matches = re.findall(pattern, content, flags=re.DOTALL)

for text, json_str in matches:
    texts.append(text.strip())
    try:
        data = json.loads(json_str)
        json_dicts.append(data)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        json_dicts.append({})

df = pd.DataFrame(json_dicts)
df['text'] = texts

# Convert types
df['traffic_related'] = df['traffic_related'].astype(bool)
df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')

# Calculate harvest rate per query
total_per_query = df.groupby('query').size()
relevant_per_query = df[df['traffic_related']].groupby('query').size()

harvest_df = pd.DataFrame({
    'total_posts': total_per_query,
    'relevant_posts': relevant_per_query
}).fillna(0)

harvest_df['harvest_rate_%'] = (harvest_df['relevant_posts'] / harvest_df['total_posts']) * 100

# Save per-query harvest rate CSV
per_query_csv_path = os.path.join(output_folder, 'harvest_rate_per_query.csv')
harvest_df.to_csv(per_query_csv_path)
print(f"Harvest rate per query saved to '{per_query_csv_path}'.")

# Calculate overall harvest rate
total_scraped = len(df)
total_relevant = df['traffic_related'].sum()
overall_harvest_rate = (total_relevant / total_scraped) * 100

overall_df = pd.DataFrame({
    'total_scraped_posts': [total_scraped],
    'total_relevant_posts': [total_relevant],
    'overall_harvest_rate_%': [overall_harvest_rate]
})

# Save overall harvest rate CSV
overall_csv_path = os.path.join(output_folder, 'overall_harvest_rate.csv')
overall_df.to_csv(overall_csv_path, index=False)
print(f"Overall harvest rate saved to '{overall_csv_path}'.")

# Save summary to a text file
summary_txt_path = os.path.join(output_folder, 'harvest_rate_summary.txt')
with open(summary_txt_path, 'w', encoding='utf-8') as f:
    f.write("Harvest rate per query:\n")
    f.write(harvest_df.to_string())
    f.write("\n\nOverall harvest rate:\n")
    f.write(overall_df.to_string())

print(f"Summary saved to '{summary_txt_path}'.")
