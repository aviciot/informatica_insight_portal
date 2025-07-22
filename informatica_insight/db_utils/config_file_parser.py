import re
import logging

logger = logging.getLogger(__name__)


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
        return database_specific
   # print("!!!!!!!!!!TNS:\n", all_databases)

    return all_databases
