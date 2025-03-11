import pandas as pd
import numpy as np
from prophet import Prophet

class MachineLearning:
    def __init__(self,Venue,PLU_Category,PLU_Name):
        self.venue = Venue
        self.PLU_Category = PLU_Category
        self.PLU_Name = PLU_Name
        self.df=None
        self.model=None
    
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
        self.model.fit(self.df)



    def Predict(self):
        future_dates = self.model.make_future_dataframe(periods=7, freq='D', include_history=False)
        predictions = self.model.predict(future_dates)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        
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
        

