import os
import sys
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from io import StringIO

# Ensure the script finds Wiki_Gendersort.py in the same repo
repo_path = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
sys.path.append(repo_path)  # Add it to Python's search path

# Debugging: List all files in the repository
st.write("Current Directory:", os.getcwd())
st.write("Files in Directory:", os.listdir(repo_path))

# Check if Wiki_Gendersort.py exists before importing
if "Wiki_Gendersort.py" in os.listdir(repo_path):
    try:
        from Wiki_Gendersort import Wiki_Gendersort
        gender_sorter = Wiki_Gendersort()  # Initialize the gender sorter
        st.success("✅ Successfully imported Wiki_Gendersort")
    except Exception as e:
        st.error(f"⚠️ Import failed: {e}")
else:
    st.error("❌ ERROR: Could not find Wiki_Gendersort.py. Make sure it exists in your repo and is at the root level.")

# Streamlit UI
st.title("🔎 LinkedIn Profile Search (Google CSE)")

# User Inputs
CSE_ID = st.text_input("Enter Custom Search Engine ID (CSE ID)")

query = st.text_input("Enter Search Query")
num_results = st.number_input("Number of Results to Fetch", min_value=1, max_value=200, value=50)
gender = st.radio("Filter by Gender:", ["Male", "Female", "Both"])

# Define LinkedIn country subdomains (Full List)
country_options = {
    "United States": "www.linkedin.com/in",
    "United Kingdom": "uk.linkedin.com/in",
    "Netherlands": "nl.linkedin.com/in",
    "South Africa": "za.linkedin.com/in",
    "Canada": "ca.linkedin.com/in",
    "Australia": "au.linkedin.com/in",
    "Germany": "de.linkedin.com/in",
    "France": "fr.linkedin.com/in",
    "India": "in.linkedin.com/in",
    "Brazil": "br.linkedin.com/in",
    "Italy": "it.linkedin.com/in",
    "Spain": "es.linkedin.com/in",
    "China": "cn.linkedin.com/in",
    "Japan": "jp.linkedin.com/in",
    "Mexico": "mx.linkedin.com/in",
    "Argentina": "ar.linkedin.com/in",
    "Belgium": "be.linkedin.com/in",
    "Sweden": "se.linkedin.com/in",
    "Switzerland": "ch.linkedin.com/in",
    "Russia": "ru.linkedin.com/in",
    "Singapore": "sg.linkedin.com/in",
    "Ireland": "ie.linkedin.com/in",
    "New Zealand": "nz.linkedin.com/in",
    "United Arab Emirates": "ae.linkedin.com/in",
    "Saudi Arabia": "sa.linkedin.com/in",
}

# Multi-select for countries
selected_countries = st.multiselect("Select Countries to Search:", list(country_options.keys()))

# Construct the hidden country-specific site query
if selected_countries:
    site_query = " OR ".join([f"site:{country_options[country]}" for country in selected_countries])
    full_query = f"({site_query}) {query}"
else:
    full_query = query

# Function to fetch LinkedIn profiles
def fetch_results():
    if not CSE_ID or not query or not selected_countries:
        st.warning("Please fill in all fields before running the search.")
        return None
    
    results = []
    start_index = 1
    batch_size = 10
    progress_bar = st.progress(0)

    while len(results) < num_results:
        url = f"https://www.googleapis.com/customsearch/v1?q={full_query}&cx={CSE_ID}&start={start_index}"
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
