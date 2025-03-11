import pandas as pd
import os
import joblib
import tensorflow as tf

def fetch_sales_data():
    data = {}
    for branch in branches:
        file_path = f"{branch}_sales.csv"
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            data[branch] = df
        else:
            data[branch] = pd.DataFrame()  # Empty if file is missing
    return data

def forecast_sales(branch):
    # Load existing sales data
    # file_path = f"{branch}_sales.csv"
    # if not os.path.exists(file_path):
    #     return pd.DataFrame()  # If no data, return empty DataFrame

    # df = pd.read_csv(file_path)
    df = pd.DataFrame(branch)

    # Prepare input for model (convert to correct shape)
    last_sales = df.iloc[-10:, 1:].values  # Use last 10 rows as input (modify as needed)
    last_sales = scaler.transform(last_sales)  # Normalize if required
    last_sales = last_sales.reshape(1, 10, last_sales.shape[1])  # Reshape for RNN

    # Predict future sales (next 7 days)
    predictions = model.predict(last_sales)
    predictions = scaler.inverse_transform(predictions.reshape(-1, predictions.shape[-1]))  # Undo normalization

    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        "Item": df["Item"][:7],  # Keep item names
        "Expected Future Sales": predictions[:, 0],
        "Upper Future Sales": predictions[:, 1]
    })
    
    return forecast_df


def forecast_sales(branch):
    # Load existing sales data
    # file_path = f"{branch}_sales.csv"
    # if not os.path.exists(file_path):
    #     return pd.DataFrame()  # If no data, return empty DataFrame

    # df = pd.read_csv(file_path)
    df = pd.DataFrame(branch)


    # Prepare input for model (convert to correct shape)
    last_sales = df.iloc[-10:, 1:].values  # Use last 10 rows as input (modify as needed)
    last_sales = scaler.transform(last_sales)  # Normalize if required
    last_sales = last_sales.reshape(1, 10, last_sales.shape[1])  # Reshape for RNN

    # Predict future sales (next 7 days)
    predictions = model.predict(last_sales)
    predictions = scaler.inverse_transform(predictions.reshape(-1, predictions.shape[-1]))  # Undo normalization
    
    # Create forecast DataFrame
    forecast_df = pd.DataFrame({
        "Item": df["Item"][:7],  # Keep item names
        "Expected Future Sales": predictions[:, 0],
        "Upper Future Sales": predictions[:, 1]
    })
    
    return forecast_df
