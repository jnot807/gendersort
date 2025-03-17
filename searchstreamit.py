import os
import sys  # To modify the system path
import requests
from datetime import datetime
import streamlit as st
import pandas as pd

# Ensure the script finds Wiki_Gendersort.py in the same repo
repo_path = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
sys.path.append(repo_path)  # Add it to Python's search path

# Debugging: List all files in the repository
print("Current Directory:", os.getcwd())
print("Files in Directory:", os.listdir(repo_path))

# Import the Wiki-Gendersort library
from Wiki_Gendersort import wiki_gendersort

# Initialize the gender sorter
gender_sorter = wiki_gendersort()

# Streamlit UI
st.title("Gender Filtered Google Custom Search Results")

# User Inputs
API_KEY = st.text_input("Enter your Google API Key:", type="password")  # API key input field
CSE_ID = st.text_input("Enter the Custom Search Engine ID (CSE ID):")
query = st.text_input("Enter the search query:")
num_results = st.number_input("Enter the number of results to fetch:", min_value=1, max_value=100, value=10)
gender = st.selectbox("Select Gender to Filter By:", ("male", "female"))

# Fetch Google CSE Results when the button is pressed
if st.button("Fetch and Filter Results"):
    if API_KEY and CSE_ID and query:
        # List to hold filtered results
        results = []

        # Fetch results in batches of 10 (since that's the limit for a single API request)
        for start_index in range(1, num_results + 1, 10):  # Batching by 10 results per request
            url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CSE_ID}&start={start_index}"
            response = requests.get(url)
            data = response.json()

            if 'items' in data:
                for item in data['items']:
                    title = item['title']  # The title or name of the result
                    link = item['link']    # The URL of the result

                    # Extract the first name from the title (you can adjust this logic as needed)
                    name = title.split()[0] if title else ""

                    # Use Wiki-Gendersort to predict the gender
                    predicted_gender = gender_sorter.assign(name)

                    # Compare predicted gender (handle case sensitivity and "UNK")
                    if predicted_gender == "F" and gender == "female":
                        results.append([title, link])  # Store title and link if gender matches
                    elif predicted_gender == "M" and gender == "male":
                        results.append([title, link])  # Store title and link if gender matches
                    else:
                        # Print for skipped names if they don't match the gender
                        st.text(f"Skipping '{name}' due to gender mismatch (predicted: {predicted_gender}, filtered: {gender})")
            else:
                st.text("No results found or reached the end of results.")
                break  # Stop fetching if no more results

        # Display results
        if results:
            st.write(f"Displaying results for the query: '{query}'")

            # Create a table for results
            results_df = pd.DataFrame(results, columns=["Title", "Link"])
            st.dataframe(results_df)

            # Create HTML content for download
            html_content = '<html>\n<head>\n<title>Search Results</title>\n</head>\n<body>\n'
            html_content += f'<h1>Search Results for: "{query}"</h1>\n'  # Title
            html_content += '<table border="1" cellpadding="10" cellspacing="0">\n'
            html_content += '<tr><th>Title</th><th>Link</th></tr>\n'  # Table headers

            for title, link in results:
                html_content += f'<tr><td>{title}</td><td><a href="{link}" target="_blank">{link}</a></td></tr>\n'

            html_content += '</table>\n</body>\n</html>\n'

            # Provide a download button for the HTML file
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
