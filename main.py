from importlib import reload
import pandas as pd
import streamlit as st
from urllib.parse import urlparse
from parse import parse_with_chatgpt
from scrape import (
    clean_body_content,
    extract_body_content,
    scrape_website,
    split_dom_content,
)

st.set_page_config(page_title="Web Scraper", layout="wide")

# Initialize session state
if "urls_and_commands" not in st.session_state:
    st.session_state.urls_and_commands = []
if "download_history" not in st.session_state:
    st.session_state.download_history = []

# Page Title
st.title("🌐 Multi-Link Web Scraper")

# --- Layout --- 
col1, col2 = st.columns([2, 3])

# --- Column 1: Add and Manage URLs ---
with col1:
    st.header("🔗 Add and Manage URLs")

    with st.form("add_url_form"):
        st.subheader("➕ Add New URL")
        url = st.text_input("Enter Website URL")
        command = st.text_input("Enter Parsing Command")
        submitted = st.form_submit_button("Add")
        if submitted:
            if url and command and (url.startswith("http://") or url.startswith("https://")):
                st.session_state.urls_and_commands.append({"url": url, "command": command})
                st.success("Added URL and Command successfully!")
            else:
                st.error("Invalid URL. Ensure it starts with 'http://' or 'https://'.")

    st.subheader("Manage URLs and Commands")
    if st.session_state.urls_and_commands:
        for i, item in enumerate(st.session_state.urls_and_commands):
            with st.expander(f"URL {i + 1}: {item['url']}"):
                st.write(f"**Command:** {item['command']}")
                new_url = st.text_input(f"Edit URL {i + 1}", item['url'], key=f"url_{i}")
                new_command = st.text_input(f"Edit Command {i + 1}", item['command'], key=f"command_{i}")

                save_button = st.button("Save Changes", key=f"save_{i}")
                delete_button = st.button("Delete", key=f"delete_{i}")

                if save_button:
                    st.session_state.urls_and_commands[i] = {"url": new_url, "command": new_command}
                    st.success("Updated successfully!")

                if delete_button:
                    st.session_state.urls_and_commands.pop(i)
                    st.success(f"URL {i + 1} deleted successfully!")
    else:
        st.info("No URLs added yet. Add them above.")

# --- Column 2: Scrape and Process Results ---
with col2:
    st.header("Scrape and Process Results")
    if st.button("Start Processing All URLs"):
        if st.session_state.urls_and_commands:
            progress = st.progress(0)
            excel_file = "parsed_results.xlsx"

            try:
                with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                    sheets_written = 0  # Track how many sheets are written
                    
                    for i, item in enumerate(st.session_state.urls_and_commands):
                        url, command = item["url"], item["command"]

                        progress.progress((i + 1) / len(st.session_state.urls_and_commands))
                        st.write(f"Processing URL {i + 1}: {url}")

                        dom_content = scrape_website(url)
                        body_content = extract_body_content(dom_content)
                        cleaned_content = clean_body_content(body_content)
                        dom_chunks = split_dom_content(cleaned_content)
                        parsed_result = parse_with_chatgpt(dom_chunks, command)

                        rows = [line.split("|")[1:-1] for line in parsed_result.splitlines() if line.startswith("|")]
                        if rows:  # Only proceed if rows are not empty
                            headers = rows.pop(0)
                            df = pd.DataFrame(rows, columns=headers)

                            if not df.empty:
                                parsed_url = urlparse(url)
                                domain = parsed_url.netloc.split(".")[0].replace(".", "_")
                                sheet_name = f"Result_{domain}"[:31]  # Excel sheet names have a max length of 31 characters
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                sheets_written += 1

                                st.success(f"Processed URL {i + 1} into sheet '{sheet_name}'")
                                st.session_state.download_history.append({
                                    "file": excel_file,
                                    "urls": [item["url"] for item in st.session_state.urls_and_commands],
                                })
                            else:
                                st.warning(f"No data to write for URL {i + 1}: {url}")
                        else:
                            st.warning(f"No data parsed for URL {i + 1}: {url}")

                    # If no sheets were written, add a default sheet
                    if sheets_written == 0:
                        pd.DataFrame({"Note": ["No valid data was processed."]}).to_excel(
                            writer, sheet_name="Default", index=False
                        )

                st.success("✅ Processing complete!")
                st.session_state.results_file = excel_file
                st.download_button(
                    label="Download Parsed Content as Excel",
                    data=open(excel_file, "rb").read(),
                    file_name=excel_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            except Exception as e:
                st.error(f"Error during processing: {e}")

    else:
        st.warning("⚠️ No URLs to process. Add them in the left panel.")


    st.write("### Download History")
    if st.session_state.download_history:
        for idx, record in enumerate(st.session_state.download_history):
            with st.expander(f"Download {idx + 1}"):
                st.write(f"**Processed URLs:**")
                for url in record["urls"]:
                    st.write(f"- {url}")
                with open(record["file"], "rb") as file:
                    st.download_button(
                        label=f"Download {record['file']}",
                        data=file,
                        file_name=record["file"],
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
