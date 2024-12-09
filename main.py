import pandas as pd
import streamlit as st
from urllib.parse import urlparse
from parse import parse_with_ollama
from scrape import (
    clean_body_content, 
    extract_body_content, 
    scrape_website, 
    split_dom_content,
)

st.title("AI Initiative: Web Scraper")

# Step 1: Enter a Website URL
url = st.text_input("Enter a Website URL: ")

if st.button("Scrape Website"):
    if url:
        st.write("Scraping the website...")
        
        try:
            # Scrape the website
            dom_content = scrape_website(url)
            body_content = extract_body_content(dom_content)
            cleaned_content = clean_body_content(body_content)

            # Store the DOM content in Streamlit session state
            st.session_state.dom_content = cleaned_content

            # Display the DOM content in an expandable text box
            with st.expander("View DOM Content"):
                st.text_area("DOM Content", cleaned_content, height=300)

        except Exception as e:
            st.error(f"Failed to scrape the website: {e}")

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            # Use a spinner to indicate processing
            with st.spinner("Parsing the content. Please wait..."):
                try:
                    # Split DOM content and parse
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    parsed_result = parse_with_ollama(dom_chunks, parse_description)
                    st.write("Parsing completed!")

                    # Transform the parsed result into tabular format
                    rows = [line.split("|")[1:-1] for line in parsed_result.splitlines() if line.startswith("|")]
                    headers = rows.pop(0)  # Assume the first row is the header
                    df = pd.DataFrame(rows, columns=headers)

                    # Extract domain and exclude everything after '.com'
                    parsed_url = urlparse(url)
                    domain = parsed_url.netloc.split(".com")[0].replace(".", "_")
                    excel_file = f"parsed_output_of_{domain}.xlsx"

                    # Save the parsed result to an Excel file
                    df.to_excel(excel_file, index=False)

                    # Display the table in Streamlit
                    st.dataframe(df)

                    # Allow user to download the Excel file
                    st.download_button(
                        label="Download Parsed Content as Excel",
                        data=open(excel_file, "rb").read(),
                        file_name=excel_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                except Exception as e:
                    st.error(f"Failed to process parsed content: {e}")
                    st.text_area("Parsed Result", parsed_result)
