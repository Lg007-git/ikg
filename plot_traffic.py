import os
import pandas as pd
import folium
import json
from google import genai
from dotenv import load_dotenv
# -------------------------
# Initialize Gemini
# -------------------------
load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))  # Replace with your API key

# -------------------------
# Load cleaned tweets
# -------------------------
df = pd.read_csv("traffic_cleaned_2025-09-29.csv")  # Adjust filename

# -------------------------
# Create map centered in India
# -------------------------
m = folium.Map(location=[22.5937, 78.9629], zoom_start=5)

# -------------------------
# Plot each tweet
# -------------------------
for _, row in df.iterrows():
    tweet = row['tweet']
    try:
        data = json.loads(row['ai_extracted'])
        traffic_type = data.get("type", "other")
        lat = data.get("lat")
        lon = data.get("lon")

        # If lat/lon missing, ask AI to provide approximate coordinates
        if lat is None or lon is None:
            prompt = f"""
            Tweet: "{tweet}"
            Extract traffic info and provide latitude and longitude.
            Return JSON like:
            {{
                "traffic_related": true/false,
                "type": "jam/accident/roadblock/other",
                "lat": 0.0,
                "lon": 0.0
            }}
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            ai_result = response.text.strip()
            ai_data = json.loads(ai_result)
            lat = ai_data.get("lat")
            lon = ai_data.get("lon")
            traffic_type = ai_data.get("type", traffic_type)

        # Only plot if coordinates available
        if lat and lon:
            color = "red" if traffic_type=="jam" else "orange" if traffic_type=="accident" else "blue"
            folium.Marker(
                location=[lat, lon],
                popup=f"{traffic_type}: {tweet[:100]}...",
                icon=folium.Icon(color=color)
            ).add_to(m)

    except Exception as e:
        print(f"Skipping row due to error: {e}")

# -------------------------
# Save map
# -------------------------
m.save("traffic_map.html")
print("✅ Map saved as traffic_map.html")
