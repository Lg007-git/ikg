import os
from google import genai
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))  # Make sure GEMINI_KEY is set in your environment

# Load your scraped tweets
tweets_df = pd.read_csv("traffic_2025-09-29.csv")

cleaned_data = []

for tweet in tweets_df['content']:
    try:
        prompt = f"""
                Tweet: "{tweet}"
                Extract traffic location in latitude and longitude.
                If exact coordinates are mentioned, use them.
                Otherwise, give approximate coordinates for the area mentioned.
                Return JSON like:
                {{
                "traffic_related": true/false,
                "type": "jam/accident/roadblock/other",
                "lat":  0.0,
                "lon": 0.0
                }}
                """

        # Send request to Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",  # Gemini model
            contents=prompt
        )

        content = response.text
        cleaned_data.append({"tweet": tweet, "ai_extracted": content})

    except Exception as e:
        print(f"Error processing: {tweet}\n{e}")

# Save results
today = date.today()
output_file = f"traffic_cleaned_{today}.csv"
pd.DataFrame(cleaned_data).to_csv(output_file, index=False)
print(f"✅ Saved cleaned tweets → {output_file}")
