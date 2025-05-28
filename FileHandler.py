import pandas as pd
import os
import re
from datetime import datetime

# Function to get all PartsLog CSV files from the selected folder path
from pandas import Timestamp  # Import Timestamp

def get_csv_files(folder_info, start_date=None, end_date=None):
    csv_files = []
    for folder_path, machine_name in folder_info:  # Unpacking tuples
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.startswith('PartsLog_') and file.endswith('.csv'):
                    file_date_str = file.split('_')[-1][:8]  # Extract the date
                    try:
                        file_date = Timestamp(datetime.strptime(file_date_str, '%Y%m%d').date())  # Convert to Timestamp
                        # Check if the file date is within the selected range
                        if (start_date is None or file_date >= start_date) and (end_date is None or file_date <= end_date):
                            csv_files.append((os.path.join(root, file), machine_name))  # Append both file path and machine name
                    except ValueError:
                        print(f"Skipping file with unexpected date format: {file}")
    return csv_files




# Function to merge and clean data from all CSV files
def merge_and_clean(file_paths):
    combined_df = pd.DataFrame()
    
    for file, machine_name in file_paths:
        try:
            match = re.search(r"PartsLog_(.+?)_\d{14}\.csv", os.path.basename(file))
            program_name = match.group(1) if match else "Unknown"

            df = pd.read_csv(file, delimiter=',', skiprows=2, on_bad_lines='skip', engine='python')
            
            df['Machine Name'] = machine_name  # Use machine name from .txt file
            df['Program Name'] = program_name
            df['File Name'] = os.path.basename(file)

            if 'Parts Name' in df.columns:
                columns = df.columns.tolist()
                columns.insert(columns.index('Parts Name'), columns.pop(columns.index('Program Name')))
                df = df[columns]

            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except pd.errors.ParserError as e:
            print(f"Error reading {file}: {e}")
    
    return combined_df

