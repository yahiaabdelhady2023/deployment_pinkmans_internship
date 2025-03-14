import pandas as pd
import numpy as np
from prophet import Prophet
import os
import pickle
import pandas as pd
from datetime import datetime, timedelta
from flask import render_template
from apscheduler.schedulers.background import BackgroundScheduler

class MachineLearning:
    def __init__(self,Venue,PLU_Category,PLU_Name):
        self.venue = Venue
        self.PLU_Category = PLU_Category
        self.PLU_Name = PLU_Name
        self.df=None
        self.model=None
        self.model_file = f"models/{Venue}/{PLU_Category}/{PLU_Name.replace('/', '_')}.pkl"
    
    def Prepare(self,df):
        df[(df.Venue==self.venue) & (df['PLU Category']==self.PLU_Category)]['PLU Name'].value_counts()
        df=df[(df.Venue==self.venue) & (df['PLU Name']==self.PLU_Name)]
        df['Number Of Items Sold']=1
        df=df[['Order Date','Number Of Items Sold']]
        df.set_index('Order Date',inplace=True)
        df=df.groupby('Order Date').sum()
        self.df = df
        self.df['ds']=self.df.index
        self.df['y']=self.df['Number Of Items Sold']
        

    def Fit(self):
        model = Prophet()
        self.model=model
        self.model.add_country_holidays(country_name='UK')
        self.model.fit(self.df)
        # self._save_model()
    


    def Predict(self,dataframe):
        # if not self.model and not self._load_model():
        #     # If no model exists, train a new one
        #     print("training a new model")
        #     self.Prepare(dataframe)
        #     self.Fit()

        today = datetime.now()
        # Start with today to ensure we get enough data
        prediction_start = today
        # End 2 weeks out
        prediction_end = today + timedelta(days=13)  

        # For the second week only, we'll filter after getting predictions
        second_week_start = today + timedelta(days=7)  # 7 days from today
        second_week_end = prediction_end
        future_dates = pd.DataFrame({
        'ds': pd.date_range(start=prediction_start, end=prediction_end)
        })
        # future_dates = self.model.make_future_dataframe(periods=7, freq='D', include_history=False)
        predictions = self.model.predict(future_dates)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        second_week_mask = (predictions['ds'] >= second_week_start)
        predictions = predictions[second_week_mask]
        # Rename columns
        predictions = predictions.rename(columns={
            'ds': 'Next Week',
            'yhat': 'Forecast',
            'yhat_lower': 'Forecast Lower',
            'yhat_upper': 'Forecast Upper'
        })
        predictions['Next Week'] = predictions['Next Week'].dt.strftime('%Y-%m-%d')

        return round(predictions).to_dict(orient='records')
    
        # tables_data = {
    #     "Fruits": [
    #         {"Name": "Apple", "Color": "Red", "Price": 1.2},
    #         {"Name": "Banana", "Color": "Yellow", "Price": 0.5},
    #     ],
    #     "Vegetables": [
    #         {"Name": "Carrot", "Color": "Orange", "Price": 0.8},
    #         {"Name": "Spinach", "Color": "Green", "Price": 1.5},
    #     ]
    # }
        

    def _save_model(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_file), exist_ok=True)
        
        # Save the model
        with open(self.model_file, 'wb') as f:
            pickle.dump(self.model, f)
        
    def _load_model(self):
        # Load the model if it exists
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                self.model = pickle.load(f)
            return True
        return False