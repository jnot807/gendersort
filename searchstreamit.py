import os
import sys
import requests
import pandas as pd
import streamlit as st  # Required for Streamlit app
from datetime import datetime
from io import StringIO
import wikipediaapi  # Correct import for `wikipedia-api`
import wikipedia  # Standard Wikipedia module (ensure it's installed)
from unidecode import unidecode  # Required for Unicode handling
from tqdm import tqdm  # For progress bars
from pathlib import Path  # For file handling

# Ensure the script finds Wiki_Gendersort.py in the same repo
repo_path = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
sys.path.append(repo_path)  # Add it to Python's search path

# Debugging: List all files in the repository
print("Current Directory:", os.getcwd())
print("Files in Directory:", os.listdir(repo_path))

# Check if Wiki_Gendersort.py exists before importing
if "Wiki_Gendersort.py" in os.listdir(repo_path):
    try:
        from Wiki_Gendersort import wiki_gendersort  # Correct import
        gender_sorter = wiki_gendersort()  # Initialize the gender sorter
        print("✅ Successfully imported Wiki_Gendersort")
    except Exception as e:
        print(f"⚠️ Import failed: {e}")
else:
    print("❌ ERROR: Could not find Wiki_Gendersort.py. Make sure it exists in your repo and is at the root level.")

# Hardcoded Google CSE API Key
API_KEY = "AIzaSyBuskvy0h2pfBTyMsqmsb659duKYq2sCP8"

# Display a message when the script is run
print("\nScript is running as scheduled. Please provide the necessary inputs below.\n")

# Get the CSE ID, query, and number of results from user input
CSE_ID = input("Enter the Custom Search Engine ID (CSE ID): ")  # Prompt for CSE ID
query = input("Enter the search query: ")  # Prompt for search query
num_results = int(input("Enter the number of gender-matching results to fetch (e.g., 100): "))  # Desired results

# Prompt for gender selection
gender = input("Enter the gender to filter (male/female): ").lower()

# Set the path where results will be saved
folder_path = os.path.join(os.getcwd(), "Search_Results")

# Ensure the folder exists, create it if necessary
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a unique filename based on the query and timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{query.replace(' ', '_')}_{timestamp}.html"  # Replace spaces with underscores
html_filename = os.path.join(folder_path, filename)

# Fetch Google CSE Results
results = []
start_index = 1  # Start index for Google API pagination
batch_size = 10  # Number of results fetched per API call

# Construct Google-friendly query
site_query = ' OR '.join([f'"site:{domain}"' for domain in [
    "www.linkedin.com/in", "uk.linkedin.com/in", "ca.linkedin.com/in"
]])
full_query = f"({site_query}) \"{query}\""

print(f"🔍 Final Google Search Query: {full_query}")  # Debugging
print(f"🔑 Using API Key: {API_KEY}")
print(f"🌐 Using CSE ID: {CSE_ID}")

while len(results) < num_results:
    url = f"https://www.googleapis.com/customsearch/v1?q={full_query}&key={API_KEY}&cx={CSE_ID}&start={start_index}"
    response = requests.get(url)
    data = response.json()

    # Debug: Print API Response
    print(f"📢 API Request: {url}")
    print(f"🔍 API Response: {data}")  # Print entire response

    if 'items' not in data:
        print("⚠️ No results found. Check if your query is formatted correctly.")
        break  # Stop if no more results are available

    for item in data['items']:
        if len(results) >= num_results:
            break  # Stop if we have enough gender-matching results

        title = item['title']  # The title or name of the result
        link = item['link']    # The URL of the result

        # Extract the first name from the title (you can adjust this logic as needed)
        name = title.split()[0] if title else ""

        # Use Wiki-Gendersort to predict the gender
        predicted_gender = gender_sorter.assign(name)
        
        # Print the predicted gender for debugging
        print(f"Predicted gender for '{name}': {predicted_gender}")

        # Compare predicted gender (handle case sensitivity and "UNK")
        if (predicted_gender == "F" and gender == "female") or (predicted_gender == "M" and gender == "male"):
            results.append([title, link])  # Store title and link if gender matches
        else:
            # Print for skipped names if they don't match the gender
            print(f"Skipping '{name}' due to gender mismatch (predicted: {predicted_gender}, filtered: {gender})")

    # Increase start index for the next batch
    start_index += batch_size

# Write results to HTML
with open(html_filename, mode='w', encoding='utf-8') as file:
    # Start HTML structure
    file.write('<html>\n<head>\n<title>Search Results</title>\n</head>\n<body>\n')
    file.write('<h1>Search Results for: "{}"</h1>\n'.format(query))  # Title
    file.write('<table border="1" cellpadding="10" cellspacing="0">\n')
    file.write('<tr><th>Title</th><th>Link</th></tr>\n')  # Table headers

    # Write each result as a row in the table
    for title, link in results:
        file.write(f'<tr><td>{title}</td><td><a href="{link}" target="_blank">{link}</a></td></tr>\n')

    # End HTML structure
    file.write('</table>\n</body>\n</html>\n')

print(f"Results saved to {html_filename}")
