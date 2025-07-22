import streamlit as st

# Set up Streamlit page
st.set_page_config(
    page_title="Data Services Dashboard",
    page_icon="📂",
    layout="wide",
)

import logging
import os
import bcrypt
from pathlib import Path

from styles.app_ultis import load_custom_css
from home_page import display_home_page
from informatica_insight.informatica_insight_page import display_informatica_insight_page
from config.config import Config
from admin_page import display_admin_page
from db.db_utils import get_db_session, get_db_engine,initialize_database
from db.models import User, Role,UserVisit
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone

# from crontab_manager_page.crontab_manager_page import display_crontab_manager
# from crontab_manager_page.test_page import display_test

# Logging configuration
LOG_FILE_PATH = os.path.abspath("app.log")
if not os.path.exists(LOG_FILE_PATH):
    with open(LOG_FILE_PATH, "w") as log_file:
        log_file.write("")  # Create empty log file

if "logging_initialized" not in st.session_state:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    logging.info("Logging initialized.")
    st.session_state["logging_initialized"] = True


# Initialize app configuration
config_file = Path("config", "config.yaml")
config = Config(config_file)

engine = get_db_engine(config)
session = get_db_session(config)

# ✅ 3. Make sure tables exist before querying!
if not engine.dialect.has_table(engine.connect(), "roles"):
    initialize_database(config)





# Role-based permissions
# yaml
#ROLE_PERMISSIONS = config.get("role_permissions", {})


def has_permission(permission):
    """Check if the current user has the specified permission."""
    permissions = st.session_state.get("permissions", [])
   # print("permission",permissions)
    return "all" in permissions or permission in permissions


def validate_user(username, password):
    """Validate user credentials from the in-memory cache."""
    users_cache = st.session_state.get("user_cache", {})
    user_data = users_cache.get(username)

    if not user_data:
        return None

    if bcrypt.checkpw(password.encode("utf-8"), user_data["password"].encode("utf-8")):
        return {
            "role": user_data["role"],
            "permissions": user_data["permissions"]
        }

    return None






# def validate_user(username, password):
#     """Validate user credentials."""
#     user_data = config.get(f"users.{username}")
#     if not user_data:
#         return None  # User not found
#
#     if bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
#         return {
#             "role": user_data["role"],
#             "permissions": ROLE_PERMISSIONS.get(user_data["role"], []),
#         }
#     return None  # no credentials,Avi - add retry?


def display_login_screen():
    """Render the login screen."""
    st.title("Login to Dashboard")
    username = st.text_input("Username", placeholder="Enter your username", key="login_username")
    password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")

    if st.button("Login", key="login_button"):
        user_info = validate_user(username, password)
        if user_info:
            visit = UserVisit(username=username, login_time=datetime.now(timezone.utc))
            session.add(visit)
            session.commit()
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = user_info["role"]
            st.session_state["permissions"] = user_info["permissions"]
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password.")


def init():
    """Initialize the app."""
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True
        logging.info("App initialized.")

        # Load the configuration into session state
    if "portal_config" not in st.session_state:
        st.session_state["portal_config"] = config

        # Add default session states
        st.session_state.setdefault("logged_in", False)
        st.session_state.setdefault("current_page", "Home")

    if "user_cache" not in st.session_state:

        # ✅ 4. Load and cache roles + users (now safe for SQLite)
        roles_cache = {}
        for role in session.query(Role).all():
            roles_cache[role.name] = [perm.permission for perm in role.permissions]

        users_cache = {}
        for user in session.query(User).all():
            role_name = user.role
            users_cache[user.username] = {
                "password": user.password,
                "role": role_name,
                "permissions": roles_cache.get(role_name, [])
            }

        st.session_state["user_cache"] = users_cache

        print("Cached users:", list(st.session_state["user_cache"].keys()))

init()
load_custom_css()
# Handle login/logout
if not config.get("dev_mode") and not st.session_state.get("logged_in", False):
    display_login_screen()
    st.stop()

if config.get("dev_mode"):
    st.session_state["logged_in"] = True
    st.session_state["username"] = "admin"
    st.session_state["role"] = "admin"
    st.session_state["permissions"] = ["all"]  # Admin gets all permissions

# Page mappings
PAGES = {
    "Home": display_home_page,
    "DEV: Informatica Insights": display_informatica_insight_page,
    "Admin": display_admin_page,
    # "CronTab Management": display_crontab_manager,
}

# Sidebar Navigation
with st.sidebar:
    if config.get("dev_mode"):
        # Display dev mode message with CSS classes
        st.markdown(
            """
            <div class="dev-mode-container">
                <span class="dev-mode-icon">🛠️</span>
                <p class="dev-mode-title">Developer Mode</p>
                <p class="dev-mode-subtitle">Logged in as: Admin </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.image("./config/under-construction.png", width=140)
    else:
        if st.session_state.get("logged_in", False):
            st.write(f"Logged in as: {st.session_state['username']}")
            if st.button("Logout"):
                st.session_state["logged_in"] = False
                st.session_state["username"] = None
                st.session_state["role"] = None
                st.success("Logged out successfully!")
                st.rerun()

        # Common Sidebar Elements
    st.image("./config/logo.png", use_container_width=True)
    st.title("DS Dashboard")
    st.markdown("---")
    # Navigation Buttons
    st.subheader("🚀 Navigation")
    if st.button("🏠 Home", key="nav_home"):
        st.session_state["current_page"] = "Home"
        st.rerun()
    # if has_permission("development_tools"):
    #     with st.expander("🔧 Development Tools"):
    #         if st.button("CronTab Management", key="nav_cron_tab_manager"):
    #             st.session_state["current_page"] = "CronTab Management"
    #             st.rerun()
       # print(has_permission("informatica_insight"))

    if has_permission("informatica_insight"):
        with st.expander("Informatica Insight"):
            if st.button("Informatica Insights", key="nav_informatica_insights"):
                st.session_state["current_page"] = "DEV: Informatica Insights"
                st.rerun()
            # if st.button("DEV: Test", key="nav_test"):
            #     st.session_state["current_page"] = "DEV: Test"
            #     st.rerun()


    if has_permission("admin"):
        st.markdown("### ")
        st.markdown("---")
        st.markdown("#### 🔐 Admin Tools")
        if st.button("🧑‍💼 Go to Admin Panel", key="ds_admin"):
            st.session_state["current_page"] = "Admin"
            st.rerun()

# Render the current page
current_page = st.session_state.get("current_page", "Home")


if current_page in PAGES:
    PAGES[current_page]()
else:
    st.error(f"Page '{current_page}' not found.")
