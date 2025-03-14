#connects route.py with model.py


from app.Models import *
from app.AggregateData import *
from app.MachineLearning import *

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
        branches = {}
        
        # Sample data for demonstration - in real implementation, you'd load from your CSV files
        # sample_data = [
        #     {"Next Week": "2025-03-21", "Weekday": "Friday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 2.0, "Forecast Lower": 1.0, "Forecast Upper": 3.0},
        #     {"Next Week": "2025-03-22", "Weekday": "Saturday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 2.0, "Forecast Lower": 1.0, "Forecast Upper": 4.0},
        #     {"Next Week": "2025-03-23", "Weekday": "Sunday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 2.0, "Forecast Lower": 1.0, "Forecast Upper": 3.0},
        #     {"Next Week": "2025-03-24", "Weekday": "Monday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 3.0, "Forecast Lower": 1.0, "Forecast Upper": 4.0},
        #     {"Next Week": "2025-03-25", "Weekday": "Tuesday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 3.0, "Forecast Lower": 1.0, "Forecast Upper": 4.0},
        #     {"Next Week": "2025-03-26", "Weekday": "Wednesday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 3.0, "Forecast Lower": 1.0, "Forecast Upper": 4.0},
        #     {"Next Week": "2025-03-27", "Weekday": "Thursday", "Item Name": "Beetroot hummus and roasted veggies Focaccia", "Forecast": 2.0, "Forecast Lower": 1.0, "Forecast Upper": 4.0}
        # ]
        
        
        # In a real implementation, you would load data from your forecasts folder:
        forecast_folder = 'forecasts'
        if os.path.exists(forecast_folder):
            forecast_files = [f for f in os.listdir(forecast_folder) if f.startswith('forecasts_') and f.endswith('.csv')]
            
            for file in forecast_files:
                branch_name = file.replace('forecasts_', '').replace('.csv', '').replace('_', ' ')
                file_path = os.path.join(forecast_folder, file)
                
                forecasts_df = pd.read_csv(file_path, parse_dates=['Next Week'])
                
                # Convert datetime to date string format YYYY-MM-DD
                data_list = forecasts_df.to_dict('records')
                for item in data_list:
                    if isinstance(item['Next Week'], pd.Timestamp):
                        item['Next Week'] = item['Next Week'].strftime('%Y-%m-%d')
                
                branches[branch_name] = data_list

        
        return branches
        
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