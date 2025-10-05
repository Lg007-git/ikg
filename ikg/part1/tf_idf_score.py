import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from Preprocess_the_Text_for_it_idf import preprocess_text

# Path to your scraped data CSV
input_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02.csv'

# Load the CSV into DataFrame
df = pd.read_csv(input_csv)

# Check if 'content' column exists before preprocessing
if 'content' in df.columns:
    # Apply text preprocessing
    df['clean_content'] = df['content'].apply(preprocess_text)
    # Print a sample to ensure it worked
    print(df[['content', 'clean_content']].head())
else:
    print("No 'content' column found in the data.")
    exit()

# Check if 'clean_content' exists after preprocessing
if 'clean_content' in df.columns:
    # Initialize TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=50)  # You can tweak these parameters

    # Fit and transform the cleaned content
    tfidf_matrix = vectorizer.fit_transform(df['clean_content'])

    # Convert the result to a DataFrame for easier readability
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    # Show the top 5 rows of TF-IDF scores
    print(tfidf_df.head())
else:
    print("No 'clean_content' column after preprocessing.")


# Save TF-IDF scores to a CSV file
tfidf_df.to_csv(r'D:\Scrapping\twitter_scrapping\ikg\part1\tfidf_output.csv', index=False)
print("TF-IDF results saved to tfidf_output.csv")

top_keywords = tfidf_df.sum().sort_values(ascending=False).head(20)
print(top_keywords)
top_keywords.to_csv(r'D:\Scrapping\twitter_scrapping\ikg\part1\top_keywords.csv')