import pandas as pd
import numpy as np

class GetStart_And_End_Date:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    
    def GetStartDate(self):
        return self.start_date
    
    def GetEndDate(self):
        return self.end_date
    
    def FullDate(self):
        return str(self.start_date) + " to " + str(self.end_date)
    
class DailyLabourCost_Aggregation(GetStart_And_End_Date):
    def __init__(self, dataframe,start_date,end_date):
        super().__init__(start_date, end_date)
        self.dataframe = dataframe
        self.dataframe['Date']=pd.to_datetime(self.dataframe['Date'])
        self.dataframe=self.dataframe.groupby(['Venue'], as_index=False).agg({
            'Net Sales': 'sum',
            'Labour Total Cost (est)': 'sum',
            'Labour Total Cost as % of Total Net Sales': 'mean'  # Assuming average percentage is needed
        })
        #print(self.dataframe)
        # self.dataframe=self.dataframe['Net Sales'].fillna(0)
        # self.dataframe=self.dataframe['Labour Total Cost as % of Total Net Sales'].fillna(0)
        # self.dataframe=self.dataframe['Labour Total Cost (est)'].fillna(0)
        self.dataframe['Net Sales']=self.dataframe['Net Sales'].round(2)
        self.dataframe['Labour Total Cost as % of Total Net Sales'] = self.dataframe['Labour Total Cost as % of Total Net Sales'].round(2)
    def GetTotalNetRevenue(self):
        return round(sum(self.dataframe['Net Sales']),2)

    def TotalLabourCost(self):
        total_revenue = self.dataframe["Net Sales"].sum()
        total_revenue = round(total_revenue,2)
        total_labour_cost = self.dataframe["Labour Total Cost (est)"].sum()

        # Calculate total Labour % of Sales
        if total_revenue > 0:
            total_labour_percentage = (total_labour_cost / total_revenue) * 100
            total_labour_percentage = round(total_labour_percentage,2)
        else:
            total_labour_percentage = 0  # Avoid division by zero

        return total_labour_percentage

    def GetBranchNames(self):
        return self.dataframe['Venue'].tolist()

    def GetNetSalePerBranch(self):
        return self.dataframe['Net Sales'].tolist()

    def GetLabourCostPerBranch(self):
        self.dataframe['Labour Total Cost as % of Total Net Sales'].tolist()

    def GetColumnNames_Table(self):
        return ['Branch','Labour Total Cost as %','Net Sales £']
    
    def GetData_Table(self):
        return self.dataframe[['Venue','Labour Total Cost as % of Total Net Sales','Net Sales']].fillna(0).values.tolist()+[['Total',self.TotalLabourCost(),self.GetTotalNetRevenue()]]


"""
label_names
,data_values
,dataset,Total_Net_Sales
, Top_Sold_Specific_Items
,Top_Sold_Categories
,Top_Item,Top_Category
, Total_Items_Sale
, Branch_Total_Net_Sales
, columns_dataset_two
,columns_two  ,columns
,columns_dataset
,Report_Date
"""
class WeeklyItemBreakDown_Aggregation(GetStart_And_End_Date):
    def __init__(self, dataframe,start_date,end_date):
        super().__init__(start_date, end_date)
        self.dataframe = dataframe
        self.dataframe['Sold Items'] = 1
        self.dataframe['Net Sale']=self.dataframe['Net Sale'].round(2)



    def GetTopItem(self):
        return self.GetTopSpecificItems().idxmax()
    
    def GetTopSpecificItems(self):
        #print("self.dataframe.GetTopSpecificItems",self.dataframe)
        return self.dataframe['PLU Name'].value_counts()

    def GetTopCategory(self):
        return self.GetTopSoldCategories().idxmax()

    def GetTopSoldCategories(self):
        return self.dataframe['PLU Category'].value_counts()

    def GetLabelCategory(self):
        return self.GetTopSoldCategories()[:5].index.tolist()

    def GetDataValueCategory(self):
        return self.GetTopSoldCategories()[:5].values.tolist()
    
    def GetLabelSpecificItems(self):
        return self.GetTopSpecificItems()[:5].index.tolist()
    
    def GetDataValueSpecificItems(self):
        return self.GetTopSpecificItems()[:5].values.tolist()

    def GetColumnNames_SpecificItemsTable(self):
        return ["Item","Net Sales","Items Sold"]
    def GetColumnNames_LeadTable(self):
        return ['Lead Type' ,	'Net Sales £', 'Items Sold']
        
    def GetColumnNames_CategoryTable(self):
        return ['Category'	 , 'Net Sales £', 'Items Sold']
    
    def GetData_SpecificItemsTable(self):
        #print("columns of self.dataframe",self.dataframe.columns.tolist())
        top_items=self.dataframe.groupby(['PLU Name'])[['Net Sale','Sold Items']].sum().sort_values(by='Sold Items',ascending=False)
        return list(top_items.reset_index().values.tolist() + [['Total',round(top_items.sum().tolist(),2),top_items['Sold Items'].sum().tolist()]])
    
    def GetData_CategoryTable(self):
        top_items=self.dataframe.groupby(['PLU Category'])[['Net Sale','Sold Items']].sum().sort_values(by='Sold Items',ascending=False)
        return list(top_items.reset_index().values.tolist() + [['Total',round(top_items.sum(),2).tolist(),top_items['Sold Items'].sum().tolist()]])
    
    def GetData_LeadTable(self):
        top_items=self.dataframe.groupby(['Lead Type'])[['Net Sale','Sold Items']].sum().sort_values(by='Sold Items',ascending=False)
        return list(top_items.reset_index().values.tolist() + [['Total',round(top_items.sum(),2).tolist(),top_items['Sold Items'].sum().tolist()]])
        # return self.dataframe[['PLU Name','Items Sold','Net Sales','GP%']].fillna(0).values.tolist()
    def GetData_Table(self,columns):
        return []

    def GetBranchNames(self):
        #print(self.dataframe)
        return self.dataframe['Venue'].tolist()
    
    def GetTotalNetRevenue(self):
        return round(sum(self.dataframe['Net Sale']),2)