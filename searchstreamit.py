import os
import sys
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from io import StringIO
import wikipediaapi
import wikipedia
from unidecode import unidecode
from tqdm import tqdm
from pathlib import Path

# Ensure the script finds Wiki_Gendersort.py in the same repo
repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(repo_path)

# Check if Wiki_Gendersort.py exists before importing
if "Wiki_Gendersort.py" in os.listdir(repo_path):
    try:
        from Wiki_Gendersort import wiki_gendersort
        gender_sorter = wiki_gendersort()
        st.success("✅ Successfully imported Wiki_Gendersort")
    except Exception as e:
        st.error(f"⚠️ Import failed: {e}")
else:
    st.error("❌ ERROR: Could not find Wiki_Gendersort.py. Make sure it exists in your repo.")

# Hardcoded Google CSE API Key
API_KEY = "AIzaSyBuskvy0h2pfBTyMsqmsb659duKYq2sCP8"

# Streamlit Inputs
CSE_ID = st.text_input("Enter the Custom Search Engine ID (CSE ID):")
query = st.text_input("Enter the search query:")
num_results = st.number_input("Enter the number of gender-matching results to fetch:", min_value=1, step=1)
gender = st.selectbox("Enter the gender to filter (male/female):", options=["male", "female"])

# Create folder for results
folder_path = os.path.join(os.getcwd(), "Search_Results")
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Create a unique filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{query.replace(' ', '_')}_{timestamp}.html"
html_filename = os.path.join(folder_path, filename)

# Fetch Google CSE Results
results = []
start_index = 1
batch_size = 10

site_query = ' OR '.join([f'"site:{domain}"' for domain in [
    "www.linkedin.com/in", "uk.linkedin.com/in", "ca.linkedin.com/in"
]])
full_query = f"({site_query}) \"{query}\""

# Show the query and API Key for debugging purposes
st.markdown(f"### Google Search Query: {full_query}")
st.text(f"Using API Key: {API_KEY}")
st.text(f"Using CSE ID: {CSE_ID}")

while len(results) < num_results:
    url = f"https://www.googleapis.com/customsearch/v1?q={full_query}&key={API_KEY}&cx={CSE_ID}&start={start_index}"
    response = requests.get(url)
    data = response.json()

    if 'items' not in data:
        st.warning("⚠️ No results found. Check if your query is formatted correctly.")
        break

    for item in data['items']:
        if len(results) >= num_results:
            break

        title = item['title']
        link = item['link']
        name = title.split()[0] if title else ""

        # Predict the gender
        predicted_gender = gender_sorter.assign(name)
        st.text(f"Predicted gender for '{name}': {predicted_gender}")

        # Filter based on predicted gender
        if (predicted_gender == "F" and gender == "female") or (predicted_gender == "M" and gender == "male"):
            results.append([title, link])
        else:
            st.text(f"Skipping '{name}' due to gender mismatch (predicted: {predicted_gender}, filtered: {gender})")

    start_index += batch_size

# Display the results in a table format in the app
if results:
    st.table(results)

# Save results as HTML (optional)
with open(html_filename, mode='w', encoding='utf-8') as file:
    file.write('<html>\n<head>\n<title>Search Results</title>\n</head>\n<body>\n')
    file.write('<h1>Search Results for: "{}"</h1>\n'.format(query))
    file.write('<table border="1" cellpadding="10" cellspacing="0">\n')
    file.write('<tr><th>Title</th><th>Link</th></tr>\n')
    for title, link in results:
        file.write(f'<tr><td>{title}</td><td><a href="{link}" target="_blank">{link}</a></td></tr>\n')
    file.write('</table>\n</body>\n</html>\n')

st.success(f"Results saved to {html_filename}")
