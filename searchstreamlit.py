import os
import sys
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from io import StringIO

# Automatically detect the repo directory and add it to Python's path
repo_path = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
sys.path.append(repo_path)  # Add the repo root to Python's search path

# Now import wiki.py
try:
    import wiki  # Import the gender sorter script from your GitHub repo
    gender_sorter = wiki.wiki_gendersort()  # Initialize the gender sorter
except ModuleNotFoundError:
    st.error("Error: Could not find `wiki.py`. Make sure it exists in your repo.")

# Streamlit UI
st.title("LinkedIn Profile Search (Google CSE)")

# User Inputs
API_KEY = st.text_input("Enter Google CSE API Key", type="password")
CSE_ID = st.text_input("Enter Custom Search Engine ID (CSE ID)")
query = st.text_input("Enter Search Query")
num_results = st.number_input("Number of Results to Fetch", min_value=1, max_value=200, value=50)
gender = st.radio("Filter by Gender:", ["Male", "Female", "Both"])

# Define LinkedIn country subdomains
country_options = {
    "United States": "www.linkedin.com/in",
    "United Kingdom": "uk.linkedin.com/in",
    "Netherlands": "nl.linkedin.com/in",
    "South Africa": "za.linkedin.com/in",
    "Canada": "ca.linkedin.com/in",
}

# Multi-select for countries
selected_countries = st.multiselect("Select Countries to Search:", list(country_options.keys()))

# Function to fetch LinkedIn profiles
def fetch_results():
    if not API_KEY or not CSE_ID or not query or not selected_countries:
        st.warning("Please fill in all fields before running the search.")
        return
    
    linkedin_domains = [country_options[country] for country in selected_countries]
    site_query = " OR ".join([f"site:{domain}" for domain in linkedin_domains])

    results = []
    start_index = 1
    batch_size = 10
    progress_bar = st.progress(0)

    while len(results) < num_results:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}+({site_query})&key={API_KEY}&cx={CSE_ID}&start={start_index}"
        response = requests.get(url)
        data = response.json()

        if 'items' not in data:
            st.warning("No more results available.")
            break

        for item in data['items']:
            if len(results) >= num_results:
                break

            title = item['title']
            link = item['link']
            name = title.split()[0] if title else ""
            predicted_gender = gender_sorter.assign(name)

            if gender == "Both" or (predicted_gender == "F" and gender == "Female") or (predicted_gender == "M" and gender == "Male"):
                results.append([title, link, predicted_gender])

        start_index += batch_size
        progress_bar.progress(min(len(results) / num_results, 1.0))

    # Convert results to DataFrame
    df = pd.DataFrame(results, columns=["Title", "Link", "Predicted Gender"])

    return df

# Button to start search
if st.button("Search LinkedIn Profiles"):
    df = fetch_results()
    
    if df is not None:
        st.success("Search Completed!")
        st.write(df)

        # Download button for CSV file
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(label="Download CSV", data=csv_buffer.getvalue(), file_name="linkedin_results.csv", mime="text/csv")
