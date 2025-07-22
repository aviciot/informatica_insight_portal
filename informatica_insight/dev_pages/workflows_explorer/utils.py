from collections import defaultdict
import pandas as pd

def merge_dicts(dict1, dict2):
    """Merges two dictionaries recursively, combining lists and nested dictionaries."""
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(value, dict) and isinstance(dict1[key], dict):
                merge_dicts(dict1[key], value)
            elif isinstance(value, list) and isinstance(dict1[key], list):
                dict1[key].extend(value)
            else:
                dict1[key] = value
        else:
            dict1[key] = value
    return dict1

def group_and_clean_hierarchy(hierarchy):
    """Groups first-level children with the same name and cleans the hierarchy."""
    grouped_hierarchy = defaultdict(dict)
    for key, value in hierarchy.items():
        clean_key = key.strip() or "AllSessions"
        if isinstance(value, dict):
            grouped_hierarchy[clean_key] = merge_dicts(grouped_hierarchy[clean_key], value)
        else:
            grouped_hierarchy[clean_key] = value
    return dict(grouped_hierarchy)
