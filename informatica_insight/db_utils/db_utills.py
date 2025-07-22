import sqlite3
import configparser
import os
import re
import logging
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from sqlalchemy import create_engine
import sqlite3

# Check the current logging level
#logger.info(f"Current logging level: {logger.getEffectiveLevel()}")

import sqlite3
import os
import logging




logger = logging.getLogger(__name__)

def get_db_connection(config):
    """Establish a connection to the SQLite database. Create the file if it doesn't exist."""
    
    try:
        if config.check_for_updates():
            logger.info("Configuration file has changed, reloading.")
        
        logger.info(f"Available config keys: {list(config.data.keys())}")
        # Get the database path
        database_path = config.get("db_details.db_path")
        if not database_path:
            logger.error("❌ Database path not found in configuration! Check db_details.db_path in config.")
            raise ValueError("Database path not found in configuration under 'db_details.db_path'.")

        # Ensure the directory exists
        db_dir = os.path.dirname(database_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)  # Create missing directories

        # Check if the database file exists
        if not os.path.exists(database_path):
            logger.info(f"Database file not found. Creating new database at: {database_path}")

        # Connect to the database (will create it if it doesn't exist)
        connection = sqlite3.connect(database_path)
        logger.info("Database connection established.")

        return connection

    except Exception as e:
        logger.error(f"Failed to establish database connection: {e}")
        return None


def fetch_and_cache_tables(config):
    try:
        # Establish a database connection
 
        connection = get_db_connection(config)
        if not connection:
            raise ValueError("Failed to connect to the database.!")

        # Get the list of tables to cache from the configuration
        cache_tables = config.get("data_viewer.cache_tables", [])
        if not cache_tables:
            logger.warning("No tables defined for caching in the configuration.")
            return {}

        # Cache table data
        cached_tables = {}
        for table in cache_tables:
            try:
                logger.info(f"Fetching data from table: {table}")
                cached_tables[table] = pd.read_sql_query(f"SELECT * FROM {table}", connection)
            except sqlite3.Error as db_err:
                logger.error(f"Error fetching data from table '{table}': {db_err}")
            except Exception as e:
                logger.error(f"Unexpected error fetching data from table '{table}': {e}")

        if not cached_tables:
            logger.warning("No data was cached. Check the table definitions or database connection.")
        else:
            logger.info("Successfully fetched and cached specified tables.")

        return cached_tables
    except sqlite3.Error as db_err:
        logger.error(f"Database error occurred: {db_err}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching tables: {e}")
        raise
    finally:
        # Ensure the connection is closed
        if 'connection' in locals() and connection:
            connection.close()
            logger.info("Database connection closed.")


def display_table_data(table_name, connection):
    """Display data from a specified table."""
    query = f"SELECT * FROM {table_name} LIMIT 100"  # Limit rows for performance
    try:
        df = pd.read_sql_query(query, connection)
        st.write(f"### Data from Table: {table_name}")
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading table {table_name}: {e}")

def display_table_data_with_filters(config, table_name):
    """Display table data with filters and enhanced UI using AgGrid."""
    db_path = config.data.get("db_details", {}).get("db_path")
    if not db_path:
        st.error("Database path not found in configuration.")
        return

    try:
        # Connect to the SQLite database
        engine = create_engine(f"sqlite:///{db_path}")
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)

        # Display table using AgGrid
        st.subheader(f"Data from {table_name}")
        st.markdown("Use the filters and sorting options below to explore the data.")

        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=True)  # Enable pagination
        gb.configure_default_column(editable=True, filter=True)  # Enable filtering
        grid_options = gb.build()

        # Display the grid
        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            theme="balham",  # You can choose from "streamlit", "light", "dark", etc.
            update_mode="VALUE_CHANGED",
            fit_columns_on_grid_load=True,
        )

        st.success(f"Loaded {len(df)} rows from {table_name}")

    except Exception as e:
        st.error(f"Error loading table {table_name}: {e}")

def display_table_data_with_filters_autocomplete(table_name, connection):
    """Display data with autocomplete-based search and pagination."""
    query = f"SELECT * FROM {table_name}"
    try:
        df = pd.read_sql_query(query, connection)

        # Generate a list of possible values for autocomplete (use the first column as an example)
        column_values = df.iloc[:, 0].astype(str).unique().tolist()  # Modify to use other columns if needed

        # Autocomplete search with selectbox
        search = st.selectbox("🔍 Search within the table", options=[""] + column_values, key="autocomplete_search")

        if search:
            # Filter data based on selected value
            df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

        # Display results in a paginated manner
        rows_per_page = 10
        total_rows = len(df)
        page_number = st.number_input(
            "Page", min_value=1, max_value=(total_rows // rows_per_page) + 1, step=1, key="pagination"
        )
        start_idx = (page_number - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        st.markdown(f"**Showing results {start_idx + 1} to {min(end_idx, total_rows)} of {total_rows}**")
        st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
    except Exception as e:
        st.error(f"Error loading table {table_name}: {e}")

def get_table_names(connection):
    """Fetch all table names from the SQLite database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor = connection.cursor()
    cursor.execute(query)
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def table_selector(connection):
    """Allow users to select a table from the database and view it with filters."""
    try:
        # Fetch table names dynamically
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql_query(query, connection)['name'].tolist()

        # Create a Streamlit selectbox for table selection
        selected_table = st.selectbox("Select a table to view:", tables)

        # Display the selected table's data with filters and pagination
        if selected_table:
            st.markdown(f"### Viewing: `{selected_table}`")
            display_table_data_with_filters_autocomplete(selected_table, connection)
    except Exception as e:
        st.error(f"Error loading table list: {e}")

def drop_create_view(config, view_key):
    """
    Drops and recreates a view based on the provided configuration.
    :param config: Configuration object for accessing the script path.
    :param view_key: Key to locate the specific view in the configuration.
    """
    conn = None
    try:
        # Retrieve the drop and create script path from the config
        drop_create_script = config.get(f"views.{view_key}.drop_create")

        if not drop_create_script or not os.path.exists(drop_create_script):
            logger.error(f"Drop and create script not found: {drop_create_script}")
            raise FileNotFoundError(f"Drop and create script not found: {drop_create_script}")

        # Connect to the SQLite database
        conn = get_db_connection(config)
        if conn is None:
            raise ValueError("Failed to establish a database connection.")

        cursor = conn.cursor()
        logger.info("Connected to the database.")

        # Read and execute the drop and create script
        with open(drop_create_script, 'r') as file:
            script_content = file.read()
            if not script_content.strip():
                logger.error(f"Drop and create script is empty: {drop_create_script}")
                raise ValueError(f"Drop and create script is empty: {drop_create_script}")

            cursor.executescript(script_content)
            logger.info(f"View for '{view_key}' dropped and recreated successfully.")
            print(f"View for '{view_key}' dropped and recreated successfully.")

        # Commit the changes
        conn.commit()

    except FileNotFoundError as fnf_error:
        logger.error(f"File error: {fnf_error}")
        raise fnf_error
    except ValueError as ve_error:
        logger.error(f"Value error: {ve_error}")
        raise ve_error
    except sqlite3.Error as sql_error:
        logger.error(f"SQLite error: {sql_error}")
        raise sql_error
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        raise ex
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")


def drop_and_create_table(config, table_key):
    """Drops and recreates the table based on the provided configuration."""

    conn = None
    try:
        print(f"ddl.{table_key}.drop_create")
        # Extract paths and flags from the configuration
        drop_create_script = config.get(f"ddl.{table_key}.drop_create")
        drop_and_create = config.get(f"ddl.{table_key}.drop_and_create", False)
        print(f"ddl.{table_key}.drop_create")
        if not drop_create_script or not os.path.exists(drop_create_script):
            print(f"Drop and create script not found: {drop_create_script}")
            raise FileNotFoundError(f"Drop and create script not found: {drop_create_script}")

        # Connect to the SQLite database using get_db_connection
        conn = get_db_connection(config)
        if conn is None:
            raise ValueError("Failed to establish a database connection.")

        cursor = conn.cursor()
        logger.info(f"Connected to database.")

        if drop_and_create:
            logger.info(f"Dropping and recreating the table for {table_key}.")
            with open(drop_create_script, 'r') as file:
                script_content = file.read()
                if not script_content.strip():
                    print(f"Drop and create script is empty: {drop_create_script}")
                    raise ValueError(f"Drop and create script is empty: {drop_create_script}")
                cursor.executescript(script_content)
                logger.info(f"Table for {table_key} dropped and recreated successfully.")
                print(f"Table for {table_key} dropped and recreated successfully.")
        conn.commit()
    except FileNotFoundError as fnf_error:
        logger.error(f"File error: {fnf_error}")
        raise fnf_error
    except ValueError as ve_error:
        logger.error(f"Value error: {ve_error}")
        raise ve_error
    except sqlite3.Error as sql_error:
        logger.error(f"SQLite error: {sql_error}")
        raise sql_error
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        raise ex
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

def insert_data(config, table_key):
    """Inserts data into the table based on the provided configuration."""
    conn = None
    successful_inserts = 0
    try:
        # Extract paths from the configuration
        insert_script = config.get(f"ddl.{table_key}.insert")

        if not insert_script or not os.path.exists(insert_script):
            raise FileNotFoundError(f"Insert data script not found: {insert_script}")

        # Connect to the SQLite database using get_db_connection
        conn = get_db_connection(config)
        if conn is None:
            raise ValueError("Failed to establish a database connection.")

        cursor = conn.cursor()

        # Read the insert data script
        with open(insert_script, 'r', encoding='utf-8') as file:
            insert_data_sql = file.readlines()

        # Remove lines starting with '--' (comments) and join the remaining lines
        insert_data_sql = ''.join(line for line in insert_data_sql if not line.strip().startswith('--'))

        # Split statements by ';' followed by a newline
        statements = insert_data_sql.split(';')
        statements = [stmt.strip() + ';' for stmt in statements if stmt.strip()]  # Ensure valid statements

        if not statements:
            raise ValueError(f"Insert script is empty or contains no valid statements: {insert_script}")

        for statement in statements:
            try:
                cursor.execute(statement)
                successful_inserts += 1
            except sqlite3.Error as e:
                # Log only errors
                logger.error(f"Error inserting a record: {e}")
                logger.error(f"Failed statement: {statement.strip()}")

                continue  # Continue processing remaining statements

        conn.commit()
    except FileNotFoundError as fnf_error:
        logger.error(f"File error: {fnf_error}")
        raise fnf_error
    except ValueError as ve_error:
        logger.error(f"Value error: {ve_error}")
        raise ve_error
    except sqlite3.Error as sql_error:
        logger.error(f"SQLite error: {sql_error}")
        raise sql_error
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")
        raise ex
    finally:
        if conn:
            conn.close()

    # Log the final count of successfully inserted rows
    logger.info(f"Total records successfully inserted for {table_key}: {successful_inserts}")

def update_connection_details(cursor, conn_id, database_name, host_name, port_number):
    """Update the informatica_connections_details table using the unique ID."""

    update_query = """
        UPDATE informatica_connections_details
        SET database_name = ?, host_name = ?, port_number = ?, UPDATED_DATE = CURRENT_TIMESTAMP
        WHERE ID = ?;
    """
    try:
        # Execute the query with parameters
        cursor.execute(update_query, (database_name, host_name, port_number, conn_id))

        # Commit the changes
        cursor.connection.commit()

        # Check if any rows were affected
        if cursor.rowcount > 0:
            logger.debug(f"Updated connection details for ID {conn_id}")
        else:
            logger.debug(f"No matching ID found for {conn_id}. No rows updated.")
    except Exception as e:
        logger.debug(f"Error updating connection details for ID {conn_id}: {e}")
        raise e

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
    logger.debug(f"Starting update for Oracle connections using tnsnames.ora at: {tnsnames_path}")
    logger.debug(f"Number of connections to process: {len(oracle_connections)}")

    # Parse the tnsnames.ora file
    try:
        tns_entries = parse_tnsnames_file(tnsnames_path)
        logger.debug(f"Successfully parsed tnsnames.ora file. Entries found: {len(tns_entries)}")
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
                        update_connection_details(cursor, conn_id, sid, host, port)
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

    # Log the start of the process
    logger.debug(f"Starting update for non-Oracle connections using odbc.ini at: {odbc_ini_path}")
    logger.debug(f"Number of connections to process: {len(non_oracle_connections)}")

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
        logger.debug(f"Processing connection ID: {conn_id}, Connection String: {connection_string}")

        connection_string_lower = connection_string.lower()
        if connection_string_lower in [section.lower() for section in config_parser.sections()]:
            database_name = config_parser[connection_string].get('Database', None)

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
                update_connection_details(cursor, conn_id, database_name, host_name, port_number)
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

def update_informatica_connection_details(config, scope):
    """Update Informatica connection details for a specific scope."""
    print(f"Starting update for : {scope}")

    try:
        conn = get_db_connection(config)

        # Connect to the SQLite database
        db_path = config.get('db_details.db_path')
        db_user = config.get(f"db_details.{scope}.user")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Fetch connection strings along with IDs for the current scope
        query = """
            SELECT ID, connection_string, connection_type
            FROM informatica_connections_details
            WHERE connection_string IS NOT NULL AND INFORMATICA_USER = ? ;
        """
        logger.debug(f"Executing query: {query.strip()}")
        logger.debug(f"Query parameters: (INFORMATICA_USER={db_user})")

        cursor.execute(query, (db_user,))
        connection_data = cursor.fetchall()

        # Separate Oracle and non-Oracle connections
        oracle_connections = [
            (row[0], row[1]) for row in connection_data if row[2] == "Oracle"
        ]
        non_oracle_connections = [
            (row[0], row[1]) for row in connection_data if row[2] != "Oracle"
        ]
        # print(oracle_connections)

        # Handle non-Oracle connections with odbc.ini
        odbc_ini_path = config.get("files")[f"{scope}_odbc_ini"]["path"]
        logger.info(f"Current odbc_ini_path: {odbc_ini_path}")
        missing_connections_odbc = update_non_oracle_connections(
            cursor, non_oracle_connections, odbc_ini_path
        )

        # Handle Oracle connections with tnsnames.ora
        tnsnames_path = config.get("files")[f"{scope}_tnsnames"]["path"]
        logger.info(f"Current tnsnames_path: {tnsnames_path}")
        missing_connections_tns = update_oracle_connections(
            cursor, oracle_connections, tnsnames_path
        )

        # Print missing connections for the current scope
        if missing_connections_odbc:
            print(f"\nMissing connection strings from {odbc_ini_path}:")
            for missing in missing_connections_odbc:
                print(f"- {missing}")

        if missing_connections_tns:
            for missing in missing_connections_tns:
                print(f"- {missing}")

        conn.commit()

    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    finally:
        if conn:
            conn.close()

