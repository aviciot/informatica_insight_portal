import streamlit as st

# Home Page Function
def display_home_page():
    st.markdown('<div id="home-page">', unsafe_allow_html=True)
    st.title("Welcome to the DS Dashboard!")
    st.subheader("Overview")
    st.write(
        """
        Dashboard helps streamline and manage DS, QA operations.
        - **QA**: Upload and compare files.
        - **DEV**: Handle development-related tasks.

        Navigate using the sidebar!
        """
    )

    st.markdown("---")
    st.subheader("Slack Integration")
    st.write(
        """
        Need to communicate with the team? Click the link below to open the Slack channel:
        """
    )
    slack_url = "https://slack.com/app_redirect?channel=C086RCQBZU6"
    st.markdown(f"[Open Slack Channel]({slack_url})", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
