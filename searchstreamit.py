import os
import sys
import requests
from datetime import datetime
import streamlit as st
import pandas as pd

# Ensure the script finds Wiki_Gendersort.py in the same repo
repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(repo_path)

# Import the Wiki-Gendersort library
from Wiki_Gendersort import wiki_gendersort

# Initialize the gender sorter
gender_sorter = wiki_gendersort()

# Streamlit UI
st.title("Gender Filtered Google Custom Search Results")
st.write("(Remember: Google CSE has a limit of 1000 results per day)")

# User Inputs
API_KEY = st.text_input("Enter your Google API Key:", type="password")
CSE_ID = st.text_input("Enter the Custom Search Engine ID (CSE ID):")
query = st.text_input("Enter the search query:")
num_results = st.number_input("Enter the number of results to fetch:", min_value=1, max_value=100, value=10)

gender_filter = st.selectbox("Select Gender to Filter By:", ("male", "female", "both"))
additional_genders = st.selectbox("Include Additional Genders:", ("none", "unknown", "unisex", "both"))

# Fetch Google CSE Results when the button is pressed
if st.button("Fetch and Filter Results"):
    if API_KEY and CSE_ID and query:
        results = []

        for start_index in range(1, num_results + 1, 10):
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}&start={start_index}"
            response = requests.get(url)
            data = response.json()

            if 'items' in data:
                for item in data['items']:
                    title = item['title']
                    link = item['link']
                    name = title.split()[0] if title else ""
                    predicted_gender = gender_sorter.assign(name)

                    # Filtering logic
                    match = False

                    # Base gender filter
                    if gender_filter == "male" and predicted_gender == "M":
                        match = True
                    elif gender_filter == "female" and predicted_gender == "F":
                        match = True
                    elif gender_filter == "both" and predicted_gender in ("M", "F"):
                        match = True

                    # Add unisex or unknown based on additional selection
                    if additional_genders == "unisex" and predicted_gender == "UNI":
                        match = True
                    elif additional_genders == "unknown" and predicted_gender == "UNK":
                        match = True
                    elif additional_genders == "both" and predicted_gender in ("UNK", "UNI"):
                        match = True

                    if match:
                        results.append([title, link, predicted_gender])
                    else:
                        st.text(f"Skipping '{name}' due to gender mismatch (predicted: {predicted_gender}, filtered: {gender_filter} + {additional_genders})")
            else:
                st.text("No results found or reached the end of results.")
                break

        if results:
            st.write(f"Displaying results for the query: '{query}'")
            results_df = pd.DataFrame(results, columns=["Title", "Link", "Predicted Gender"])
            st.dataframe(results_df)

            # HTML styling based on gender
            gender_colors = {
                "M": "#d0e7ff",   # light blue
                "F": "#ffd6e8",   # light pink
                "UNI": "#fff9cc", # light yellow
                "UNK": "#eeeeee"  # light gray
            }

            html_content = '''
            <html>
            <head>
                <title>Search Results</title>
                <style>
                    body { font-family: Arial, sans-serif; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; }
                    th { background-color: #f2f2f2; }
                </style>
            </head>
            <body>
            '''
            html_content += f'<h1>Search Results for: "{query}"</h1>\n'
            html_content += '<table>\n'
            html_content += '<tr><th>Title</th><th>Link</th><th>Predicted Gender</th></tr>\n'

            for title, link, gender in results:
                row_color = gender_colors.get(gender, "#ffffff")
                html_content += f'<tr style="background-color: {row_color};"><td>{title}</td><td><a href="{link}" target="_blank">{link}</a></td><td>{gender}</td></tr>\n'

            html_content += '</table>\n</body>\n</html>'

            st.download_button(
                label="Download Results as HTML",
                data=html_content,
                file_name=f"{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        else:
            st.text("No matching results found.")
    else:
        st.warning("Please fill in your Google API Key, CSE ID, and query.")
