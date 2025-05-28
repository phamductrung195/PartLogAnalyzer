# data_processing.py
import pandas as pd

def get_top_10_worst_components(data):
    if 'Pick Error Counter' in data.columns and 'No Parts Error Counter' in data.columns:
        data['Pick Error Counter'] = data['Pick Error Counter'] - data['No Parts Error Counter']
    
    error_columns = ['Pick Error Counter', 'Vision Error Counter', 'Nozzle Error Counter', 'Coplanarity Error Counter']
    
    if all(col in data.columns for col in error_columns):
        data['Total Errors'] = data[error_columns].sum(axis=1)
        component_errors = data.groupby(['Parts Name', 'Machine Name'])['Total Errors'].sum().reset_index()
        top_10_worst_components = component_errors.sort_values(by='Total Errors', ascending=False).head(20)
        return top_10_worst_components
    else:
        print("Error columns missing from data.")
        return pd.DataFrame()  # Return an empty DataFrame if error columns are missing

def filter_data_by_date(data, start_date, end_date):
    data['Date'] = pd.to_datetime(data['Date'])  # Ensure 'Date' column is in datetime format
    return data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]
