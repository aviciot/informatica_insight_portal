import streamlit as st


def display_home_page():
    st.markdown('<div id="home-page">', unsafe_allow_html=True)

    st.title("Welcome to the Informatica Insights Portal!")
    st.subheader("Overview")

    st.write(
        """
        The Informatica Insights Portal provides a unified view of your Informatica environment,
        including metadata, workflow hierarchies, session diagnostics, and performance analytics.

        🔍 **Key capabilities**:
        - Visualize folder → workflow → session hierarchies
        - Analyze session durations and anomalies
        - Explore database connections, table usage, and command dependencies
        - Identify overlapping executions and runtime inefficiencies
        - Access advanced ML-based performance insights

        Use the sidebar to navigate between modules.
        """
    )

    st.markdown("---")
    st.subheader("Team Collaboration")
    st.write(
        """
        Need to discuss a workflow issue or performance anomaly with the team? Use the Slack channel:
        """
    )
    slack_url = "https://slack.com/app_redirect?channel=C086RCQBZU6"
    st.markdown(f"[Open Slack Channel]({slack_url})", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
