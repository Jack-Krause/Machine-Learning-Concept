import csv
import os
import requests
import pandas as pd
import json
import random


def parse_csv(path, save_headers=False, features_arr=None, composite_sum=False):
    print("path of csv file: " + path)

    root_dir = os.environ.get("ROOT_DIR")
    parsed_data_dir = os.path.join(root_dir, "parsed_data")
    if save_headers:
        save_headers_json(path, parsed_data_dir, features_arr)

    with open(os.path.join(parsed_data_dir, "feature_headers.json"), 'r') as headers_json_file:
        headers_obj = json.load(headers_json_file)

        if features_arr:
            selected_dtypes = {}
            valid_cols = []

            for col in features_arr:
                if col in headers_obj:
                    selected_dtypes[col] = headers_obj[col]
                    valid_cols.append(col)

            data = pd.read_csv(path, dtype=selected_dtypes, usecols=valid_cols)
            if composite_sum:
                data['composite_target'] = 0.0
                for header in valid_cols:
                    col_data = pd.to_numeric(data[header], errors='coerce').fillna(0)
                    data['composite_target'] += col_data

                if 'composite_target' not in data.columns:
                    data['composite_target'] = 0.0
                for header in valid_cols:
                    col_data = pd.to_numeric(data[header], errors='coerce').fillna(0)
                    data['composite_target'] = data['composite_target'] + col_data

            return data, headers_obj


def save_headers_json(path, save_path, features_arr=None):
    os.makedirs(save_path, exist_ok=True)
    data = pd.read_csv(path, low_memory=False)
    dtypes_dict = data.dtypes.apply(lambda dt: dt.name).to_dict()

    if features_arr:
        dtypes_dict = {col: dtypes_dict[col] for col in features_arr if col in dtypes_dict}

    with open(os.path.join(save_path, "feature_headers.json"), "w") as f:
        json.dump(dtypes_dict, f, indent=4)


