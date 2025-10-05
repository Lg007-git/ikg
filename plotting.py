import pandas as pd
import folium
import json

# Load cleaned tweets
df = pd.read_csv("traffic_cleaned_2025-09-29.csv")

# Create a map centered in India
m = folium.Map(location=[22.5937, 78.9629], zoom_start=5)

for _, row in df.iterrows():
    tweet = row['tweet']
    try:
        # Clean JSON string
        s = row['ai_extracted']
        s_clean = s.replace('```json','').replace('```','').replace('""','"').strip()
        data = json.loads(s_clean)

        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)
        traffic_type = data.get("type", "other")

        # Only plot if valid coordinates
        if lat != 0.0 and lon != 0.0:
            color = "red" if traffic_type=="jam" else "orange" if traffic_type=="accident" else "blue"
            folium.Marker(
                location=[lat, lon],
                popup=f"{traffic_type}: {tweet[:100]}...",
                icon=folium.Icon(color=color)
            ).add_to(m)

    except Exception as e:
        print(f"Skipping row due to error: {e}")

# Save map
m.save("traffic_map.html")
print("✅ Map saved as traffic_map.html")
