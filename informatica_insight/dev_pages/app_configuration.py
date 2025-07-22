import streamlit as st
from streamlit_ace import st_ace
from informatica_insight.db_utils.db_utils2 import test_db_connection,test_oracle_connection
import yaml


@st.cache_data
def load_yaml(file_path):
    """Load YAML content from a file with caching."""
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error(f"Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        st.error(f"Error parsing YAML file: {e}")
        return {}



def display_app_configuration():
    """Display and edit the YAML configuration file with theme selection and real-time validation."""
    tab1, tab2 = st.tabs(["📄 Insight Yaml", "⚙️ Insight Setup view"])

    with tab1:
        st.subheader("⚙️ Configuration Viewer & Editor")
        st.markdown("Edit the YAML configuration below.")

        # Use global config from session state
        config = st.session_state["config"]

        # Check for updates to the configuration
        if config.check_for_updates():
            st.info("Configuration file updated and reloaded.")

        # Load YAML content using the cached function
        yaml_content = load_yaml(config.config_file)
        if not yaml_content:
            st.error("Unable to load configuration.")
            return

        # Convert YAML to string for the editor
        yaml_string = yaml.dump(yaml_content, default_flow_style=False)

        # Create a narrower section for the theme selector
        col1, col2, col3 = st.columns([1, 2, 1])  # Center-align the selector
        with col2:
            themes = ["monokai", "github", "solarized_dark", "solarized_light", "dracula", "twilight"]
            selected_theme = st.selectbox("Select Editor Theme", themes, index=0, key="theme_selector")

        # YAML Editor with Ace Editor
        edited_yaml = st_ace(
            value=yaml_string,
            language="yaml",
            theme=selected_theme,  # Use the selected theme
            key=f"yaml_editor_{selected_theme}",  # Ensure unique key for re-rendering
            height=400,
        )

        # Real-time validation feedback
        validation_placeholder = st.empty()  # Placeholder for validation messages
        if edited_yaml:
            try:
                yaml.safe_load(edited_yaml)  # Validate YAML
                validation_placeholder.success("YAML is valid.")
            except yaml.YAMLError as e:
                validation_placeholder.error(f"YAML validation error: {e}")

        # Save Changes Button
        if st.button("Save and apply changes♻️"):
            try:
                yaml.safe_load(edited_yaml)  # Validate again before saving
                with open(config.config_file, "w") as file:
                    file.write(edited_yaml)
                st.success("Configuration saved successfully,rebooting!")
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            except yaml.YAMLError as e:
                st.error(f"Failed to save: Invalid YAML format: {e}")

    with tab2:
        st.header("🔍 Insight Tool Configuration")
        ### **Insight DB Details**
        st.subheader("📌 Insight DB Details")

        db_colors = {
            "sqlite": "🔵 SQLite",
            "postgres": "🟢 PostgreSQL",
        }

        db_preference = st.session_state["config"].get("insight_db.work_with", "Unknown")

        insight_db_config = {
            "postgres": st.session_state["config"].get("insight_db.postgres", {}),
            "sqlite": st.session_state["config"].get("insight_db.sqlite", {}),
        }

        if db_preference in insight_db_config:
            with st.expander(f"🗄️ {db_preference.upper()} Database"):
                db_details = insight_db_config[db_preference]

                if db_preference == "postgres":
                    st.markdown(
                        f"**Database Name:** `{db_details.get('dbname', 'Not specified')}`  \n"
                        f"**User:** `{db_details.get('user', 'Not specified')}`  \n"
                        f"**Host:** `{db_details.get('host', 'Not specified')}`  \n"
                        f"**Port:** `{db_details.get('port', 'Not specified')}`"
                    )

                elif db_preference == "sqlite":
                    st.markdown(
                        f"**Database Path:** `{db_details.get('db_path', 'Not specified')}`"
                    )
                if st.button("🔄 Test Connection", key=f"test_{db_preference}"):
                    with st.spinner(f"Testing connection..."):
                        result = test_db_connection()
                        st.success(result) if "✅" in result else st.error(result)
        else:
            st.warning("⚠️ No valid database configuration found.")

        ### **Informatica DB Details**
        st.subheader("📌 Informatica DB Details")
        informatica_db = st.session_state["config"].get("informatica_db", {})

        if informatica_db:
            for db_name, details in informatica_db.items():
                with st.expander(f"🗄️ {db_name.upper()} Database"):
                    st.markdown(
                        f"**User:** `{details['user']}`  \n"
                        f"**Host:** `{details['host']}`  \n"
                        f"**Port:** `{details['port']}`  \n"
                        f"**Service Name:** `{details['service_name']}`"
                    )

                    if st.button("🔄 Test Connection", key=f"test_oracle_{db_name}"):
                        with st.spinner(f"Testing connection to {db_name}..."):
                            result = test_oracle_connection(db_name)
                            st.success(result) if "✅" in result else st.error(result)


        ### **Configuration Files**
        st.subheader("📌 Configuration Files")
        files_config = st.session_state["config"].get("files", {})

        if files_config:
            with st.expander("🛠️ ODBC & TNSNAMES Configuration"):
                for file_name, details in files_config.items():
                    if isinstance(details, dict):  # Ensure it's a dictionary
                        st.markdown(
                            f"**📄 {file_name.replace('_', ' ').title()}**  \n"
                            f"🔹 **Path:** `{details.get('path', 'Not specified')}`  \n"
                            f"🔹 **Align Informatica:** `{details.get('align_informatica_connections_details', False)}`"
                        )
                        st.divider()  # Optional separator for better readability