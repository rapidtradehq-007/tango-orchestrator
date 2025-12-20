import os
import pandas as pd
import logging
from app.config.settings import CONFIG
from datetime import datetime

def get_column(local_storage_path, column):
    if not os.path.exists(local_storage_path):
        raise FileNotFoundError(f"File not found in local storage: {local_storage_path}")

    df = pd.read_csv(local_storage_path)
    if column not in df.columns:
        raise ValueError(
            f"File does not contain required column: File: {local_storage_path}, Column: {column}"
        )

    return set(df[column].dropna().tolist())

def get_data(prefix):
    input_folder = CONFIG["OUTPUT_PATH"]
    if not os.path.exists(input_folder):
        raise FileNotFoundError(
            f"Input folder does not exist: {input_folder}"
        )

    matching_files = [
        os.path.join(input_folder, file)
        for file in os.listdir(input_folder)
        if file.startswith(prefix)
    ]

    if not matching_files:
        raise FileNotFoundError(
            f"No file found with prefix='{prefix}'"
        )

    latest_file = max(matching_files, key=os.path.getctime)
    logging.info(f"Latest file detected: {latest_file}")
    return latest_file


def save_data(entity_name, data: list[dict]):
    """
    Persist a list of entity dictionaries.
    """
    if not data:
        raise ValueError("No data to save")

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{CONFIG['OUTPUT_PATH']}/{entity_name}_{ts}.csv"

    columns = sorted({key for item in data for key in item.keys()})
    pd.DataFrame(data, columns=columns).to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )
