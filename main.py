import pandas as pd
import streamlit as st
from parse import parse_with_ollama
from scrape import (
    clean_body_content, 
    extract_body_content, 
    scrape_website, 
    split_dom_content,
)

st.title("AI Web Scrapper")
url = st.text_input("Enter a Website URL: ")

if st.button("Scrape Website"):
    if url:
        st.write("Scraping the website...")
        
        # Scrape the website
        dom_content = scrape_website(url)
        body_content = extract_body_content(dom_content)
        cleaned_content = clean_body_content(body_content)

        # Store the DOM content in Streamlit session state
        st.session_state.dom_content = cleaned_content

        # Display the DOM content in an expandable text box
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            # Use a spinner to indicate processing
            with st.spinner("Parsing the content. Please wait..."):
                dom_chunks = split_dom_content(st.session_state.dom_content)
                parsed_result = parse_with_ollama(dom_chunks, parse_description)

            st.write("Parsing completed!")

            # Transform the parsed result into tabular format
            try:
                # Assuming parsed_result contains a Markdown table or structured text
                # Use `pandas` to create a DataFrame directly from parsed_result if possible
                rows = [line.split("|")[1:-1] for line in parsed_result.splitlines() if line.startswith("|")]
                headers = rows.pop(0)
                df = pd.DataFrame(rows, columns=headers)

                # Display table in Streamlit
                st.dataframe(df)

                # Save the parsed result to an Excel file
                excel_file = "parsed_output of.xlsx"
                df.to_excel(excel_file, index=False)

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
