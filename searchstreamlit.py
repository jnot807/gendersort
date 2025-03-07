import streamlit as st
import os
import sys
import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Add the path to Wiki-Gendersort
sys.path.append('/Users/jasonnottage/Documents/PYTHON/Wiki-Gendersort-master')

# Import Wiki-Gendersort
from Wiki_Gendersort import wiki_gendersort

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
    "Norway": "no.linkedin.com/in",
    "Denmark": "dk.linkedin.com/in",
    "Finland": "fi.linkedin.com/in",
    "Poland": "pl.linkedin.com/in",
    "Turkey": "tr.linkedin.com/in",
    "Malaysia": "my.linkedin.com/in",
    "Indonesia": "id.linkedin.com/in",
    "Philippines": "ph.linkedin.com/in",
    "Thailand": "th.linkedin.com/in",
    "South Korea": "kr.linkedin.com/in",
    "Vietnam": "vn.linkedin.com/in",
    "Israel": "il.linkedin.com/in",
    "Portugal": "pt.linkedin.com/in",
    "Greece": "gr.linkedin.com/in",
    "Czech Republic": "cz.linkedin.com/in",
    "Hungary": "hu.linkedin.com/in",
    "Romania": "ro.linkedin.com/in",
    "Slovakia": "sk.linkedin.com/in",
    "Ukraine": "ua.linkedin.com/in",
    "Chile": "cl.linkedin.com/in",
    "Colombia": "co.linkedin.com/in",
    "Peru": "pe.linkedin.com/in",
    "Venezuela": "ve.linkedin.com/in",
    "Egypt": "eg.linkedin.com/in",
    "Pakistan": "pk.linkedin.com/in",
    "Bangladesh": "bd.linkedin.com/in",
    "Sri Lanka": "lk.linkedin.com/in",
    "Nigeria": "ng.linkedin.com/in",
    "Kenya": "ke.linkedin.com/in",
    "Ghana": "gh.linkedin.com/in",
    "Morocco": "ma.linkedin.com/in",
    "Tunisia": "tn.linkedin.com/in",
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

    gender_sorter = wiki_gendersort()
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
