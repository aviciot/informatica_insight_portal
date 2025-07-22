# custom_css_loader.py
import os
import logging
import streamlit as st

def load_custom_css():
    css_file_path = os.path.join("styles", "custom_styles.css")
    try:
        # Try to open and read the CSS file
        with open(css_file_path, "r") as f:
            css = f.read()

        # Apply CSS styles to Streamlit
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

        # Log success message
        logging.debug("Custom CSS loaded successfully.")

    except FileNotFoundError:
        # If the file is not found, log an error
        logging.error(f"CSS file not found: {css_file_path}")
    except Exception as e:
        # Log any other unexpected errors
        logging.error(f"Failed to load custom CSS. Error: {e}")
