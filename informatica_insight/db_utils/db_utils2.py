from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine,text,delete, MetaData, Table
from informatica_insight.db_utils.models import Base ,AVAILABLE_TABLES,WorkflowRun,SessionRun
import pandas as pd
import logging
import os
import re
import streamlit as st
import oracledb
import sys
from sqlalchemy.exc import OperationalError
from contextlib import closing
import configparser
from sqlalchemy.dialects import mysql
from sqlalchemy.sql import text


logger = logging.getLogger(__name__)

# ================================ #
#        DATABASE CONNECTION        #
# ================================ #

def get_config():
    """Retrieve the global config from Streamlit session state."""
    if "config" not in st.session_state:
        raise ValueError("❌ Config not loaded in session state!")
    return st.session_state["config"]

def test_db_connection():
    """Attempts to connect to the database using `get_db_engine()`."""
    try:
        engine = get_db_engine()  # Use the provided function
        with engine.connect():
            return "✅ Connection Successful!"
    except OperationalError as e:
        return f"❌ Connection Failed: {str(e)}"
    except ValueError as e:
        return f"⚠️ {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

def test_oracle_connection(db_type):
    """
    Test Oracle database connectivity.
    :param db_type: 'non_pci' or 'pci'
    :return: Success or error message.
    """
    try:
        connection = get_oracle_connection(db_type)
        if connection:
            connection.close()  # Close after successful connection
            return "✅ Connection Successful!"
        else:
            return "❌ Connection Failed: Unable to establish connection."

    except OperationalError as e:
        logger.error(f"❌ Operational Error: {e}")
        return f"❌ Connection Failed: {str(e)}"

    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        return f"❌ Connection Failed: {str(e)}"

def get_db_engine():
    """Return SQLAlchemy engine based on preferred database."""
    config = get_config()
    db_preference = config.get("insight_db.work_with")

    if db_preference == "sqlite":
        db_path = config.get("insight_db.sqlite.db_path")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure directory exists
        return create_engine(f"sqlite:///{db_path}", echo=False)

    elif db_preference == "postgres":
        db_cfg = config.get("insight_db.postgres")
        return create_engine(
            f"postgresql://{db_cfg['user']}:{db_cfg['password']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['dbname']}",
            echo=False
        )

    else:
        raise ValueError(f"❌ Unsupported database preference: {db_preference}")

def get_db_session():
    """Get a new database session."""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# ================================ #
#        DATABASE OPERATIONS       #
# ================================ #

def initialize_database():
    """Create all database tables if they don't exist."""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    logger.info("✅ Database tables initialized.")


# ================================ #
#       FETCHING TABLE DATA        #
# ================================ #

def fetch_cached_tables2(update_progress=None):
    """Fetch table data and return it as a dictionary of DataFrames with record counts."""

    config = st.session_state["config"]
    cache_tables = config.get("insight_db.cache_tables", [])

    if not cache_tables:
        logger.warning("⚠️ No tables defined for caching in configuration.")
        return {}

    cached_tables = {}

    # Use a fresh session inside a context manager
    engine = get_db_engine()  # Ensure this function returns an SQLAlchemy engine
    Session = sessionmaker(bind=engine)

    with closing(Session()) as session:
        total_tables = len(cache_tables)

        for index, table in enumerate(cache_tables):
            try:
                logger.info(f"Fetching data from table: {table}")
                #df = pd.read_sql_table(table, session.bind)  # ORM fetch, problem found in sqlite as date save as plain text and cause issue
                #if will stay in PS , can be use
                df = pd.read_sql_query(f"SELECT * FROM {table}", session.bind)

                cached_tables[table] = df

                record_count = len(df)
                logger.info(f"✅ Loaded {record_count} records from {table}")

                # Update progress UI
                if update_progress:
                    update_progress(index + 1, total_tables, table, record_count)

            except Exception as e:
                logger.error(f"❌ Error fetching data from table '{table}': {e}")

    logger.info("🔒 Database session closed.")
    return cached_tables

def get_oracle_connection(db_type):
    """
    Establish a connection to Oracle DB.
    :param db_type: 'non_pci' or 'pci'
    """
    try:
        config = st.session_state["config"]
        oracle_cfg = config.get(f"informatica_db.{db_type}")

        if not oracle_cfg:
            raise ValueError(f"❌ Oracle DB config not found for '{db_type}'!")


        connection = oracledb.connect(
            user=oracle_cfg["user"],
            password=oracle_cfg["password"],
            dsn=f"{oracle_cfg['host']}:{oracle_cfg['port']}/{oracle_cfg['service_name']}",
        )

        return connection

    except Exception as e:
        logger.error(f"❌ Failed to connect to Oracle ({db_type}): {e}")
        return None

def fetch_data_from_oracle(sql_query, db_type):
    """Fetch data from Oracle while handling special character encoding issues."""

    oracle_connection = get_oracle_connection(db_type)  # Get Oracle connection

    if oracle_connection is None:
        logger.error(f"❌ Oracle connection failed for {db_type}. Cannot fetch data.")
        return None

    try:
        with oracle_connection.cursor() as cursor:
            cursor.execute(sql_query)  # Execute query
            rows = cursor.fetchall()  # Fetch all results
            column_names = [desc[0] for desc in cursor.description]  # Get column names

        if not rows:
            logger.warning(f"⚠️ No data returned from query.")
            return None

        # ✅ Handle special character decoding
        def safe_decode(value):
            if isinstance(value, bytes):
                try:
                    return value.decode("utf-8")  # Try UTF-8 decoding first
                except UnicodeDecodeError:
                    return value.decode("latin-1", errors="replace")  # Fallback to Latin-1
            return value

        # ✅ Convert to DataFrame with safe decoding
        df = pd.DataFrame([[safe_decode(cell) for cell in row] for row in rows], columns=column_names)


        logger.info(f"✅ Successfully fetched {len(df)} rows from Oracle ({db_type}).")
        return df

    except Exception as e:
        logger.error(f"❌ Error fetching data from Oracle ({db_type}): {e}")
        return None

    finally:
        oracle_connection.close()

def truncate_table(table_name, engine):
    """Deletes all records from the given table using SQLAlchemy ORM."""
    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        # Reflect the table dynamically
        metadata = MetaData()
        metadata.reflect(bind=engine)
        table = metadata.tables.get(table_name)

        if table is None:
            logger.error(f"❌ Table {table_name} does not exist in the database.")
            return False

        # Perform deletion
        session.execute(delete(table))
        session.commit()
        session.close()

        logger.info(f"🗑️ Truncated table {table_name}.")
        return True

    except Exception as e:
        logger.error(f"❌ Error truncating table {table_name}: {e}")
        return False

def insert_data_to_target_db(table_name, df):
    """Insert data into the target database (SQLite/PostgreSQL) using SQLAlchemy engine."""
    if df is None or df.empty:
        logger.warning(f"⚠️ No data to insert for {table_name}. Skipping.")
        return

    try:
        engine = get_db_engine()
        df.columns = [col.lower() for col in df.columns]
        df.to_sql(table_name, engine, if_exists="append", index=False)

        logger.info(f"✅ Inserted {len(df)} rows into {table_name}.")
    except Exception as e:
        logger.error(f"❌ Error inserting data into {table_name}: {e}")

def transfer_data(table_name, db_type):
    """Fetch data from Oracle for multiple queries and insert it into the target DB."""
    logger.info(f"🔄 Starting data transfer for {table_name} using {db_type} DB...")

    engine = get_db_engine()
    # if not truncate_table(table_name, engine):
    #     return

    oracle_engine = get_oracle_connection(db_type)

    # Get the queries from config
    queries = st.session_state["config"].get(f"insight_db.ddl.{table_name}.fetch_data_queries", {})

    if not queries:
        logger.warning(f"⚠️ No queries found in config for {table_name}. Skipping.")
        return f"⚠️ No queries found for {table_name}."

    total_rows = 0
    for query_name, sql_query in queries.items():
        try:
            logger.info(f"📥 Running query '{query_name}' for {table_name}...")

            # Fetch data for this query
            df = fetch_data_from_oracle(sql_query, db_type)

            if df is None or df.empty:
                logger.warning(f"⚠️ No data returned for query '{query_name}'. Skipping.")
                continue

            logger.info(f"✅ Successfully fetched {len(df)} rows for query '{query_name}'.")


            # Insert into the target DB
            insert_data_to_target_db(table_name, df)
            total_rows += len(df)

        except Exception as e:
            logger.error(f"❌ Error processing query '{query_name}' for {table_name}: {e}")

    if total_rows > 0:
        return f"✅ Data transfer completed for {table_name} ({total_rows} total rows)."
    else:
        return f"⚠️ No data was transferred for {table_name}."

def drop_views(engine, views):
    """Drop all views safely in reverse order (last created first)."""
    sorted_views = sorted(views.keys(), reverse=True)

    with engine.connect() as conn:
        for view_name in sorted_views:
            drop_view_sql = views.get(view_name, {}).get("drop")
            if drop_view_sql:
                try:
                    print(f"🔄 Dropping view: {view_name}")  # Debug
                    conn.execute(text(drop_view_sql))
                    conn.commit()
                    print(f"✅ Dropped view: {view_name}")
                except Exception as e:
                    print(f"❌ Error dropping view {view_name}: {e}")

def drop_tables(engine, tables, available_tables):
    """Drop tables only if they exist."""
    with engine.connect() as conn:
        for table_name in tables:
            if table_name in available_tables:
                try:
                    print(f"🔄 Dropping table: {table_name}")  # Debug
                    available_tables[table_name].__table__.drop(conn, checkfirst=True)
                    conn.commit()
                    print(f"✅ Dropped table: {table_name}")
                except Exception as e:
                    print(f"❌ Error dropping table {table_name}: {e}")

def recreate_tables(engine, tables, available_tables):
    """Recreate selected tables."""
    with engine.connect() as conn:
        for table_name in tables:
            if table_name in available_tables:
                try:
                    print(f"🔄 Recreating table: {table_name}")  # Debug
                    available_tables[table_name].__table__.create(conn)
                    conn.commit()
                    print(f"✅ Recreated table: {table_name}")
                except Exception as e:
                    print(f"❌ Error recreating table {table_name}: {e}")

def recreate_views(engine, views):
    """Recreate all views in correct order."""
    with engine.connect() as conn:
        for view_name, view_sql in views.items():
            create_view_sql = view_sql.get("create")
            if create_view_sql:
                try:
                    print(f"🔄 Recreating view: {view_name}")  # Debug
                    conn.execute(text(create_view_sql))
                    conn.commit()
                    print(f"✅ Recreated view: {view_name}")
                except Exception as e:
                    print(f"❌ Error recreating view {view_name}: {e}")

def recreate_selected_tables(table_names):
    """Master function to drop and recreate tables with views."""
    engine = get_db_engine()


    available_tables = AVAILABLE_TABLES

    invalid_tables = [t for t in table_names if t not in available_tables]
    if invalid_tables:
        return [{"Table": t, "Status": f"⚠️ Not recognized: {t}"} for t in invalid_tables]

    all_views = st.session_state["config"].get("insight_db.views", {})

    # Step 1️⃣ Drop Views First
    drop_views(engine, all_views)

    # Step 2️⃣ Drop Tables
    drop_tables(engine, table_names, available_tables)

    # Step 3️⃣ Recreate Tables
    recreate_tables(engine, table_names, available_tables)

    # Step 4️⃣ Recreate Views
    recreate_views(engine, all_views)

    return [{"Table": t, "Status": "✅ Recreated"} for t in table_names]


def recreate_selected_views(selected_views):
    """Drop and recreate multiple selected views based on config."""
    engine = get_db_engine()

    # Get the view definitions from config
    views_config = st.session_state["config"].get("insight_db.views", {})

    if not selected_views:
        return "⚠️ No views selected for recreation."

    try:
        with engine.begin() as connection:
            for view_name in selected_views:
                drop_view_sql = views_config[view_name].get("drop")
                create_view_sql = views_config[view_name].get("create")

                if drop_view_sql:
                    connection.execute(text(drop_view_sql))
                    logger.info(f"🛠 Dropped view: {view_name}")

                if create_view_sql:
                    connection.execute(text(create_view_sql))
                    logger.info(f"✅ Recreated view: {view_name}")

        return f"✅ Successfully recreated views: {', '.join(selected_views)}"

    except Exception as e:
        logger.error(f"❌ Error recreating views: {e}")
        return f"❌ Error recreating views: {e}"

def update_informatica_connection_details(scope, user):
    """Update Informatica connection details for a specific scope."""


    logger.info(f"Starting update for : {scope}")
    config = st.session_state["config"]

    try:
        engine = get_db_engine()
        # Get database session
        session = get_db_session()

        # Fetch database configurations
        db_user = user

        # Fetch connection strings along with IDs for the current scope
        query = text("""
            select id, connection_string, connection_type
            FROM informatica_connections_details
            WHERE connection_string IS NOT NULL AND lower(INFORMATICA_USER) = :db_user;
        """)

        logger.info(f"Executing query: {query}")
        logger.debug(f"Query parameters: (INFORMATICA_USER={db_user})")

        result = session.execute(query, {"db_user": db_user})
        connection_data = result.fetchall()

        # Separate Oracle and non-Oracle connections
        oracle_connections = [(row.id, row.connection_string) for row in connection_data if
                              row.connection_type == "Oracle"]
        non_oracle_connections = [(row.id, row.connection_string) for row in connection_data if
                                  row.connection_type != "Oracle"]

        #logger.info(f"non_oracle_connections : {non_oracle_connections}")
        # Handle non-Oracle connections with odbc.ini
        odbc_ini_path = config.get("files")[f"{scope}_odbc_ini"]["path"]
        logger.info(f"Current odbc_ini_path: {odbc_ini_path}")
        missing_connections_odbc = update_non_oracle_connections(session, non_oracle_connections, odbc_ini_path)

        ##Handle Oracle connections with tnsnames.ora
        tnsnames_path = config.get("files")[f"{scope}_tnsnames"]["path"]
        logger.info(f"Current tnsnames_path: {tnsnames_path}")
        missing_connections_tns = update_oracle_connections(session, oracle_connections, tnsnames_path)
        logger.info(f"\nmissing_connections_tns : {missing_connections_tns}:")
        # Print missing connections for the current scope
        if missing_connections_odbc:
            print(f"\nMissing connection strings from {odbc_ini_path}:")
            for missing in missing_connections_odbc:
                print(f"- {missing}")

        if missing_connections_tns:
            for missing in missing_connections_tns:
                print(f"- {missing}")

        session.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
        raise e
    finally:
        session.close()


def update_connection_details(conn_id, database_name, host_name, port_number):
    """Update the informatica_connections_details table using the unique ID."""

    engine = get_db_engine()

    update_query = text("""
        UPDATE informatica_connections_details
        SET database_name = :database_name,
            host_name = :host_name,
            port_number = :port_number,
            updated_date = CURRENT_TIMESTAMP
        WHERE id = :conn_id;
    """)


    params = {
        "database_name": database_name,
        "host_name": host_name,
        "port_number": port_number,
        "conn_id": conn_id
    }

    try:
        # Compile and log the final SQL with values
        compiled_query = update_query.compile(
            dialect=mysql.dialect(),
            compile_kwargs={"literal_binds": True}
        )
        logger.info(f"params SQL:\n{params}")

        with engine.connect() as conn:
            with conn.begin():  # starts a transaction and commits on success
                result = conn.execute(update_query, params)

                if result.rowcount > 0:
                    logger.debug(f"✅ Updated connection details for ID {conn_id}")
                else:
                    logger.debug(f"⚠️ No matching ID found for {conn_id}. No rows updated.")
    except Exception as e:
        logger.debug(f"❌ Error updating connection details for ID {conn_id}: {e}")
        raise
def parse_tnsnames_file(file_path, specific=""):
    """
    Parses a TNS names file and extracts TNS entries with fields (host, port, sid, service_name).
    :param file_path: Path to the tnsnames.ora file.
    :param specific: Comma-separated list of specific TNS entries to return. If empty, all entries are returned.
    :return: Dictionary of TNS entries with their parsed fields.
    """
    try:
        with open(file_path, "r") as file:
            tns = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot find tnsnames.ora at the specified path: {file_path}")
    except IOError as err:
        raise IOError(f"Error reading tnsnames.ora file: {err}")

    # Remove comments and excess blank lines
    text = re.sub(r'#[^\n]*\n', '\n', tns)  # Remove comments
    text = re.sub(r'( *\n *)+', '\n', text.strip())  # Remove excess blank lines

    databases = []
    start = 0
    index = 0
    while index < len(text):
        num_of_parenthesis = 0
        index = text.find('(', start)  # Find first parenthesis
        if index == -1:
            break
        while index < len(text):
            if text[index] == '(':
                num_of_parenthesis += 1
            elif text[index] == ')':
                num_of_parenthesis -= 1
            index += 1
            if num_of_parenthesis == 0:  # If balanced, extract the entry
                break

        databases.append(text[start:index].strip())
        start = index  # Move to the next entry

    all_databases = {}
    for each in databases:
        clean = each.replace("\n", "").replace(" ", "")
        # Extract database name
        database_name_match = re.match(r'^(\w+)=', clean)
        if not database_name_match:
            continue
        database_name = database_name_match.group(1)
        connection_string = clean[len(database_name) + 1:]

        # Extract fields
        host = port = sid = service_name = ""
        host_match = re.search(r'HOST=([\w\-.]+)', connection_string, re.IGNORECASE)
        port_match = re.search(r'PORT=(\d+)', connection_string, re.IGNORECASE)
        sid_match = re.search(r'SID=([\w\-.]+)', connection_string, re.IGNORECASE)
        service_name_match = re.search(r'SERVICE_NAME=([\w\-.]+)', connection_string, re.IGNORECASE)

        if host_match:
            host = host_match.group(1)
        if port_match:
            port = port_match.group(1)
        if sid_match:
            sid = sid_match.group(1)
        if service_name_match:
            service_name = service_name_match.group(1)

        # Store parsed data
        all_databases[database_name] = {
            "host": host,
            "port": port,
            "sid": sid,
            "service_name": service_name,
        }

    if specific:
        specific_list = specific.upper().replace(' ', '').split(',')
        database_specific = {key: all_databases[key] for key in specific_list if key in all_databases}
        print("Here",database_specific)
        return database_specific
  #  print("!!!!!!!!!!TNS:\n", all_databases)
    return all_databases


def update_oracle_connections(cursor, oracle_connections, tnsnames_path):
    """Update Oracle connections using the manually parsed tnsnames.ora file."""
    logger.info(f"Starting update for Oracle connections using tnsnames.ora at: {tnsnames_path}")
    logger.info(f"Number of connections to process: {len(oracle_connections)}")

    # Parse the tnsnames.ora file
    try:
        tns_entries = parse_tnsnames_file(tnsnames_path)
        logger.info(f"Successfully parsed tnsnames.ora file. Entries found: {len(tns_entries)}")
    except FileNotFoundError:
        logger.error(f"The tnsnames.ora file was not found at the specified path: {tnsnames_path}")
        raise FileNotFoundError
        return []
    except Exception as e:
        logger.error(f"Error parsing tnsnames.ora file at {tnsnames_path}. Details: {e}")
        raise e
        return []

    missing_connections = []

    # Process each connection
    for conn_id, conn_string in oracle_connections:
        logger.debug(f"Processing connection ID: {conn_id}, Connection String: {conn_string}")
        match_found = False

        for key in tns_entries.keys():
            if conn_string.lower() == key.lower():
                match_found = True
                details = tns_entries[key]

                # Retrieve details (with default empty values to handle missing ones)
                host = details.get('host', '')
                port = details.get('port', '')
                sid = details.get('sid', '')
                service_name = details.get('service_name', '')

                logger.debug(f"Parsed details for {conn_string}: Host={host}, Port={port}, SID={sid}, ServiceName={service_name}")

                if (sid or service_name) and host and port:
                    try:
                        logger.debug(f"Updating connection details for ID {conn_id}...")
                        update_connection_details(conn_id, sid, host, port)
                        logger.debug(f"Successfully updated connection details for ID {conn_id}.")
                    except Exception as e:
                        logger.error(f"Error updating connection details for ID {conn_id}: {e}")
                        raise e
                else:
                    logger.error(f"Missing information in {tnsnames_path} for connection_string: {conn_string}")
                    missing_connections.append(connection_string)
                break

        if not match_found:
            logger.error(f"No matching entry found in {tnsnames_path} for connection_string: {conn_string}")
            missing_connections.append(conn_string)

    # Log completion of the process
    if missing_connections:
        logger.warning(f"Missing connections: {missing_connections}")
    logger.debug(f"Completed processing Oracle connections. Missing connections count: {len(missing_connections)}")

    return missing_connections

def update_non_oracle_connections(cursor, non_oracle_connections, odbc_ini_path):
    """Update non-Oracle connections using the odbc.ini file."""
    missing_connections = []

    logger.info(f"Starting update for non-Oracle connections using odbc.ini at: {odbc_ini_path}")
    logger.info(f"Number of connections to process: {len(non_oracle_connections)}")

    config_parser = configparser.ConfigParser(strict=False, allow_no_value=True)

    # Check if the odbc.ini file exists
    if not os.path.exists(odbc_ini_path):
        logger.error(f"Error: The odbc.ini file was not found at the specified path: {odbc_ini_path}")
        return

    # Try to read and parse the odbc.ini file
    try:
        config_parser.read(odbc_ini_path)
        if not config_parser.sections():
            logger.error(f"Error: The odbc.ini file at {odbc_ini_path} is empty or has no sections.")
            raise
            return
        else:
            logger.debug(f"Successfully read:{odbc_ini_path} file. Sections found: {config_parser.sections()}")
    except configparser.Error as e:
        logger.error(f"Error: Failed to parse the odbc.ini file at {odbc_ini_path}. Details: {e}")
        raise e
        return

    # Process each connection

    for conn_id, connection_string in non_oracle_connections:
        logger.info(f"Processing connection ID: {conn_id}, Connection String: {connection_string}")

        connection_string_lower = connection_string.lower()
        if connection_string_lower in [section.lower() for section in config_parser.sections()]:
            database_name = config_parser[connection_string].get('Database', None)
            logger.info(f"Found connection: {connection_string_lower}, DataBase: {database_name}")
            # Handle both HostName and SERVER for host_name
            host_name = (
                    config_parser[connection_string].get('HostName', None) or
                    config_parser[connection_string].get('SERVER', None)
            )

            # Handle both PortNumber and PORT for port_number
            port_number = (
                    config_parser[connection_string].get('PortNumber', None) or
                    config_parser[connection_string].get('PORT', None)
            )

            # Debugging: Log the values retrieved
            logger.debug(
                f"Connection details for {connection_string}: Database={database_name}, HostName={host_name}, PortNumber={port_number}")

            if database_name and host_name and port_number:
                update_connection_details(conn_id, database_name, host_name, port_number)
            else:
                logger.warning(f"Missing details for connection string: {connection_string}")
                missing_connections.append(connection_string)
        else:
            logger.warning(f"Connection string not found in odbc.ini: {connection_string}")
            missing_connections.append(connection_string)

    # Log completion of the process
    if missing_connections:
        logger.info(f"Missing connections: {missing_connections}")
    logger.info(f"Completed processing non-Oracle connections. Missing connections count: {len(missing_connections)}")

    return missing_connections


def get_workflow_runs(db_session, start_date, end_date):
    # Return rows from workflow_run_statistics using a filter on start_time and end_time
    return db_session.query(WorkflowRun).filter(WorkflowRun.start_time >= start_date,
                                                WorkflowRun.end_time <= end_date).all()
