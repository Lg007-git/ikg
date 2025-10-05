import re
import pandas as pd
# Path to your scraped data CSV
input_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02.csv'  # Adjust this to your actual file path

# Path to save cleaned CSV
output_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02_cleaned.csv'

# Load CSV into DataFrame
df = pd.read_csv(input_csv)

def preprocess_text(text):
    # Remove URLs, mentions, and special characters
    text = re.sub(r'http\S+|www\S+', '', text)  # Remove URLs
    text = re.sub(r'@\w+', '', text)  # Remove mentions (e.g., @username)
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetical characters
    text = text.lower()  # Convert to lowercase
    return text

if 'content' in df.columns:
    df['clean_content'] = df['content'].apply(preprocess_text)
    # Check the cleaned data
    print(df[['content', 'clean_content']].head())

    # Save the DataFrame with the new column to a CSV file
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Cleaned data saved to: {output_csv}")

else:
    print("No 'content' column found in the data.")
