import csv
import json
from datetime import datetime

# List of keywords to check if the tweet is traffic-related
TRAFFIC_KEYWORDS = ["traffic", "jam", "congestion", "smog", "bottle neck", "gridlock"]
LOCATION_KEYWORDS = ["bengaluru", "gurugram", "delhi", "mumbai", "kolkata", "chennai"]

# Function to check if the content is traffic-related
def is_traffic_related(content):
    return any(keyword.lower() in content.lower() for keyword in TRAFFIC_KEYWORDS)

# Function to extract location from content
def extract_location(content):
    for keyword in LOCATION_KEYWORDS:
        if keyword.lower() in content.lower():
            return keyword.capitalize()
    return ""

# Function to process the CSV file and convert to the desired format
def process_csv(input_file, output_file):
    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        with open(output_file, mode="w", encoding="utf-8") as outfile:
            for row in reader:
                tweet_id = row["id"]
                user = row["user"]
                date = row["date"]
                content = row["content"]

                # Convert the date to a datetime object to handle formatting
                date_obj = datetime.fromisoformat(date[:-1])  # Remove 'Z' for datetime compatibility
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Format as desired
                
                # Check if the tweet is traffic-related
                traffic_related = is_traffic_related(content)
                location = extract_location(content)

                # Define the traffic type based on content (example: "jam", "other", etc.)
                if traffic_related:
                    traffic_type = "jam" if "jam" in content.lower() else "congestion"
                else:
                    traffic_type = "other"

                # Create the output JSON format
                result = f'"{content}",```json\n' + json.dumps({
                    "traffic_related": traffic_related,
                    "type": traffic_type,
                    "location": location,
                    "date_time": formatted_date
                }, ensure_ascii=False, indent=4).replace("  ", "\t").replace("\n", "\n\t") + "\n```"

                # Write the result to the output file
                outfile.write(result + "\n\n")

# Input and output file paths
input_csv = r'D:\Scrapping\twitter_scrapping\playwright_output\traffic1_2025-10-02.csv'  # Replace with the path to your input CSV
output_file =r'D:\Scrapping\twitter_scrapping\without_ai_cleaning\output1.txt'  # Replace with the path to your desired output file

# Process the CSV and generate the output file
process_csv(input_csv, output_file)

print("Conversion completed!")
