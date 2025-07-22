# pages/admin.py

import streamlit as st
from sqlalchemy.orm import Session
from sqlalchemy import delete
from db.models import User, Role, UserVisit, Permission
from db.db_utils import get_db_session
from datetime import datetime
import bcrypt
import pandas as pd


def display_admin_page():
    st.title("🧑‍💼 Admin Panel")
    st.markdown("Manage users and roles below.")

    session = get_db_session(st.session_state["portal_config"])

    tab1, tab2, tab3 = st.tabs(["👥 Manage Users", "🛡️ Roles & Permissions", "📈 User Visit Logs"])

    with tab1:
        display_user_creation_form(session)
        display_existing_users(session)
        display_user_deletion(session)

    with tab2:
        display_role_permission_mapping(session)
        display_create_role_form(session)
        display_create_permission_form(session)
        display_delete_role_or_permission(session)

    with tab3:
        display_user_visit_logs(session)


# ========== Manage Users Tab ==========

def display_user_creation_form(session: Session):
    st.subheader("➕ Create New User")
    st.info("ℹ️ Creating new user.")

    roles = session.query(Role).order_by(Role.name).all()
    role_names = [r.name for r in roles]

    if not role_names:
        st.warning("⚠️ No roles found in the database. Please create roles first.")
        return

    with st.form("add_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("👤 Username", placeholder="Enter username")

        with col2:
            role = st.selectbox("🛡️ Role", role_names)

        password = st.text_input("🔒 Password", type="password", placeholder="Enter secure password")
        submitted = st.form_submit_button("✅ Create User")

        if submitted:
            if not username or not password:
                st.error("❌ Username and password are required.")
            elif session.query(User).filter_by(username=username).first():
                st.error(f"🚫 User '{username}' already exists.")
            else:
                hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                new_user = User(username=username, password=hashed_pw, role=role)
                session.add(new_user)
                session.commit()
                st.success(f"✅ User **{username}** with role **{role}** created successfully.")
                st.rerun()


def display_existing_users(session: Session):
    st.subheader("👥 Existing Users")
    users = session.query(User).order_by(User.username).all()

    with st.expander("📄 View All Users", expanded=True):
        if users:
            for user in users:
                st.markdown(f"- **{user.username}**  |  🛡️ `{user.role}`")
        else:
            st.info("No users found.")


def display_user_deletion(session: Session):
    st.subheader("🗑️ Remove User")

    users = session.query(User).order_by(User.username).all()
    with st.expander("⚠️ Delete Existing User"):
        usernames = [u.username for u in users]
        if usernames:
            user_to_delete = st.selectbox("Select user to delete", usernames)

            if st.button("🗑️ Confirm Delete"):
                user_obj = session.query(User).filter_by(username=user_to_delete).first()
                session.delete(user_obj)
                session.commit()
                st.success(f"✅ Deleted user '{user_to_delete}'")
                st.rerun()
        else:
            st.info("No users to delete.")


# ========== Roles & Permissions Tab ==========

def display_role_permission_mapping(session: Session):
    st.subheader("🔍 View Role → Permission Mapping")

    with st.expander("📘 Show All Roles and Their Permissions", expanded=True):
        roles = session.query(Role).order_by(Role.name).all()

        if roles:
            role_permission_data = []

            for role in roles:
                permissions = [perm.permission for perm in role.permissions]
                role_permission_data.append({
                    "Role": role.name,
                    "Permissions": ", ".join(permissions) if permissions else "—"
                })

            df_roles = pd.DataFrame(role_permission_data)
            st.dataframe(df_roles, use_container_width=True)
        else:
            st.info("No roles found in the database.")


def display_create_role_form(session: Session):
    with st.expander("🎯 Create Role and Assign Permissions", expanded=False):
        st.markdown("Define a role and assign existing permissions to it.")

        col1, col2 = st.columns([2, 3])
        with col1:
            role_name = st.text_input("🆕 Role Name", placeholder="e.g., analyst")

        with col2:
            all_permissions = [p.permission for p in session.query(Permission).order_by(Permission.permission).all()]
            selected_permissions = st.multiselect("🔐 Assign Permissions", options=all_permissions)

        if st.button("✅ Create Role"):
            if not role_name:
                st.error("❌ Role name is required.")
            elif session.query(Role).filter_by(name=role_name).first():
                st.error(f"🚫 Role '{role_name}' already exists.")
            else:
                new_role = Role(name=role_name)
                for perm_name in selected_permissions:
                    perm_obj = session.query(Permission).filter_by(permission=perm_name).first()
                    if perm_obj:
                        new_role.permissions.append(perm_obj)
                session.add(new_role)
                session.commit()
                st.success(f"✅ Role '{role_name}' created with {len(selected_permissions)} permission(s).")
                st.rerun()


def display_create_permission_form(session: Session):
    with st.expander("➕ Add New Permission", expanded=False):
        st.markdown("Create a new custom permission to assign to roles.")
        new_permission = st.text_input("Permission Name", placeholder="e.g., export_data")

        if st.button("✅ Add Permission"):
            if not new_permission:
                st.error("❌ Permission name is required.")
            elif session.query(Permission).filter_by(permission=new_permission).first():
                st.warning(f"⚠️ Permission '{new_permission}' already exists.")
            else:
                new_perm = Permission(permission=new_permission)
                session.add(new_perm)
                session.commit()
                st.success(f"✅ Permission '{new_permission}' added successfully.")
                st.rerun()


def display_delete_role_or_permission(session: Session):
    with st.expander("🗑️ Remove Role or Permission", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🧹 Remove Role")
            roles = [r.name for r in session.query(Role).order_by(Role.name)]
            role_to_delete = st.selectbox("Select Role to Delete", roles, key="delete_role")

            if st.button("❌ Delete Role"):
                role_obj = session.query(Role).filter_by(name=role_to_delete).first()
                if role_obj:
                    session.delete(role_obj)
                    session.commit()
                    st.success(f"✅ Role '{role_to_delete}' deleted successfully.")
                    st.rerun()

        with col2:
            st.markdown("### 🧹 Remove Permission")
            perms = [p.permission for p in session.query(Permission).order_by(Permission.permission)]
            perm_to_delete = st.selectbox("Select Permission to Delete", perms, key="delete_permission")

            if st.button("❌ Delete Permission"):
                perm_obj = session.query(Permission).filter_by(permission=perm_to_delete).first()
                if perm_obj:
                    session.delete(perm_obj)
                    session.commit()
                    st.success(f"✅ Permission '{perm_to_delete}' deleted successfully.")
                    st.rerun()


# ========== User Visit Logs Tab ==========

def display_user_visit_logs(session: Session):
    st.subheader("📈 User Login History")

    with st.expander("📊 View Recent Visits", expanded=False):
        visits = session.query(UserVisit).order_by(UserVisit.login_time.desc()).limit(100).all()

        if visits:
            df = pd.DataFrame([{
                "Username": v.username,
                "Page": v.page if v.page else "Login",
                "Time": v.login_time.strftime('%Y-%m-%d %H:%M:%S')
            } for v in visits])

            st.dataframe(df, use_container_width=True)
        else:
            st.info("No user visits have been logged yet.")
