#connects route.py with model.py


from app.Models import *
from app.AggregateData import *

"""
    Report_Date='2010-03-01 // 2010-03-04'

    label_names=['Glouchester RD','Whiteladies RD','Trynm RD2']
    dataset={"labels":label_names,"data":[1,2,3]}
    Total_Net_Sales=12434.5
    columns=['x','y','z']
    columns_dataset=[[1,2,3],[2,3,4]]
"""

class Bridge:
    def MachineLearningPredications(self):
        #getting branch, names of sandwiches
        today = datetime.today()

        # Find the start of this week (Monday of the current week)
        start_of_this_week = today - timedelta(days=today.weekday())

        # Calculate the start of the 3-week period (2 weeks ago from the start of this week)
        start_of_period = start_of_this_week - timedelta(weeks=5)

        # The end of the 3-week period is the start of this week (Monday)
        end_of_period = start_of_this_week

        # Print the 3-week period
        print(f"Start of the 3-week period: {start_of_period.strftime('%Y-%m-%d')}")
        print(f"End of the 3-week period: {end_of_period.strftime('%Y-%m-%d')}")

        database_handler_obj.Fetch_Missing_Date(start_of_period.strftime('%Y-%m-%d'), end_of_period.strftime('%Y-%m-%d'),"Order Date","WeeklyItemBreakDown",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
        dataframe=database_handler_obj.Fetch_Period(start_of_period.strftime('%Y-%m-%d'),end_of_period.strftime('%Y-%m-%d'),"Order Date","WeeklyItemBreakDown")
        df = dataframe

        # Explode the Orders column
        df_exploded = df.explode('Orders', ignore_index=True)

        # Convert the dictionaries in the Orders column to separate columns
        Orders_df = pd.json_normalize(df_exploded['Orders'])

        # Combine with parent-level columns
        dataframe = pd.concat([df_exploded.drop(columns=['Orders']), Orders_df], axis=1)
        results={}
        ml=MachineLearning('Pinkmans - Bristol Cathedral','SANDWICHES','Tuna Focaccia')
        # ml = MachineLearning(venue,'SANDWICHES',food_item)
        ml.Prepare(dataframe)
        grouped = dataframe[dataframe['PLU Category']=='SANDWICHES'].groupby("Venue")["PLU Name"].apply(list).to_dict()
        for venue, food_items_per_venue in grouped.items():
            for food_item in food_items_per_venue[:5]:

                ml = MachineLearning(venue,'SANDWICHES',food_item)
                ml.Prepare(dataframe)
                ml.Fit()
                result=ml.Predict()
                # print("result ===>",result)
                string_to_send=f'☕ {venue}  : 🥐 {food_item}'
                results[string_to_send]=result
        return results
        
    def GetDailyReportBranches_Bridge(self,start_date,end_date):
        database_handler_obj.Fetch_Missing_Date(start_date, end_date,"Date","DailyLabourCost",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
        dataframe=database_handler_obj.Fetch_Period(start_date,end_date,"Date","DailyLabourCost")

        
        
        AggregateObj=DailyLabourCost_Aggregation(dataframe,start_date,end_date)
        label_names=AggregateObj.GetBranchNames()

        return label_names
    def GetWeeklyItemReportBranches_Bridge(self,start_date,end_date):
        database_handler_obj.Fetch_Missing_Date(start_date, end_date,"Order Date","WeeklyItemBreakDown",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
        dataframe=database_handler_obj.Fetch_Period(start_date,end_date,"Order Date","WeeklyItemBreakDown")
        df = dataframe

        # Explode the Orders column
        df_exploded = df.explode('Orders', ignore_index=True)

        # Convert the dictionaries in the Orders column to separate columns
        Orders_df = pd.json_normalize(df_exploded['Orders'])

        # Combine with parent-level columns
        dataframe = pd.concat([df_exploded.drop(columns=['Orders']), Orders_df], axis=1)
        # print("sick and mad?",dataframe)
        AggregateObj=WeeklyItemBreakDown_Aggregation(dataframe,start_date,end_date)
        label_names=AggregateObj.GetBranchNames()
        return label_names

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
    def GetWeeklyItemBreakDownDataset_Bridge(self,start_date,end_date,report_type,branchname="All"):
        database_handler_obj.Fetch_Missing_Date(start_date, end_date,"Order Date","WeeklyItemBreakDown",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
        dataframe=database_handler_obj.Fetch_Period(start_date,end_date,"Order Date","WeeklyItemBreakDown")
        df_exploded = dataframe.explode('Orders', ignore_index=True)

        # Convert the dictionaries in the Orders column to separate columns
        Orders_df = pd.json_normalize(df_exploded['Orders'])

        # Combine with parent-level columns
        dataframe = pd.concat([df_exploded.drop(columns=['Orders']), Orders_df], axis=1)
        # print("dataframe information",dataframe.info())
        if branchname !="All":
            dataframe=dataframe[dataframe['Venue']==branchname]


        AggregateObj=WeeklyItemBreakDown_Aggregation(dataframe,start_date,end_date)
        Top_Sold_Categories=[]
        columns=[]
        columns_two=[]
        Top_Sold_Specific_Items=[]
        columns_dataset_two=[]
        columns_dataset=[]
        # print("report type is",report_type)
        if "Categories" in report_type:
            Top_Sold_Categories = AggregateObj.GetLabelCategory()
            columns = AggregateObj.GetColumnNames_CategoryTable()
            columns_two = AggregateObj.GetColumnNames_LeadTable()
            label_names= AggregateObj.GetLabelCategory()
            data_values= AggregateObj.GetDataValueCategory()
            columns_dataset = AggregateObj.GetData_CategoryTable()
            columns_dataset_two = AggregateObj.GetData_LeadTable()
            
        else:
            Top_Sold_Specific_Items = AggregateObj.GetLabelSpecificItems()
            columns = AggregateObj.GetColumnNames_SpecificItemsTable()
            label_names= AggregateObj.GetLabelSpecificItems()
            data_values= AggregateObj.GetDataValueSpecificItems()
            columns_dataset = AggregateObj.GetData_SpecificItemsTable()
            
        Top_Category = AggregateObj.GetTopCategory()
        Top_Item = AggregateObj.GetTopItem()
        Total_Net_Sales=AggregateObj.GetTotalNetRevenue()
        Branch_Total_Net_Sales=AggregateObj.GetTotalNetRevenue()
        dataset={"labels":label_names,"data":data_values}
        Total_Items_Sale=Total_Net_Sales
        Report_Date = AggregateObj.FullDate()
        # print(type(label_names), type(data_values), type(dataset), type(Total_Net_Sales))
        # print(type(Top_Sold_Specific_Items), type(Top_Sold_Categories), type(Top_Item), type(Top_Category))
        # print(type(Total_Items_Sale), type(Branch_Total_Net_Sales), type(columns_dataset_two))
        # print(type(columns_two), type(columns), type(columns_dataset), type(Report_Date))


        return label_names, data_values ,dataset , Total_Net_Sales,  Top_Sold_Specific_Items , Top_Sold_Categories, Top_Item, Top_Category, \
        Total_Items_Sale, Branch_Total_Net_Sales,columns_dataset_two ,columns_two, columns, columns_dataset, Report_Date
    def GetDailyReportDataset_Bridge(self,start_date, end_date,branchname="All"):
        database_handler_obj.Fetch_Missing_Date(start_date, end_date,"Date","DailyLabourCost",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
        dataframe=database_handler_obj.Fetch_Period(start_date,end_date,"Date","DailyLabourCost")

        if branchname !="All":
            dataframe=dataframe[dataframe['Venue']==branchname]
        
        AggregateObj=DailyLabourCost_Aggregation(dataframe,start_date,end_date)
        label_names=AggregateObj.GetBranchNames()
        columns=AggregateObj.GetColumnNames_Table()
        columns_dataset=AggregateObj.GetData_Table()
        data_values=AggregateObj.GetNetSalePerBranch()
        dataset={"labels":label_names,"data":data_values}
        Total_Net_Sales=AggregateObj.GetTotalNetRevenue()
        Report_Date = AggregateObj.FullDate()
        return label_names, data_values , dataset, Total_Net_Sales, columns, columns_dataset, Report_Date


# b=Bridge.GetDailyReportDataset_Bridge()
# print("I am printing",b)




KOBAS_EMAIL="mailer@kobas.co.uk"
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993  # Port for SSL

#Gmail account credentials
EMAIL = 'facemessage78@gmail.com'
PASSWORD = 'kulu imye mavn cyny' 
connection_string="mongodb+srv://facemessage78:So02KSZ21vKUmwW8@cluster0.o1rwl.mongodb.net/"

file_processor_obj = FileProcessor()
email_handler_obj = EmailHandler(username=EMAIL,password=PASSWORD,server=IMAP_SERVER,port=IMAP_PORT)
email_handler_obj.ConnectGmail()
database_handler_obj = DatabaseHandler(database_name="PinkmanDB",connection_string=connection_string)
daily_labour_cost_report_obj=DailyLabourCostReport_EmailAPI(email_handler_obj,file_processor_obj,database_handler_obj)
weekly_item_breakdown_report_obj=WeeklyItemBreakDownReport_EmailAPI(email_handler_obj,file_processor_obj,database_handler_obj)