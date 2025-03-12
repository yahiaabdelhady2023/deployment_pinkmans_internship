import pandas as pd
import imaplib
import email
from email.header import decode_header
import os
import openpyxl
import io
from datetime import datetime, timedelta

from pymongo import MongoClient
from datetime import datetime

from abc import ABC, abstractmethod


FOLDER_FOR_LABOUR_COST_DAILY='"Daily Revenue and Labour Report"'
FOLDER_FOR_WEEKLY_REVENUE='"Pinkmans - Weekly Revenue and Cost of Sales Report"'


class DateOperations:
    def Get_Today_Date(self):
        return pd.Timestamp.now().strftime("%Y-%m-%d")
    
    def Change_Date_Format(self,old_format,new_format,date):
        date_obj = datetime.strptime(date, old_format)
        formatted_date = date_obj.strftime(new_format)
        return formatted_date
    

class AbstractReportEmailAPI(ABC):
    @abstractmethod
    def GetEmailReportAttachment(specific_date,category):
        pass

class WeeklyItemBreakDownReport_EmailAPI(AbstractReportEmailAPI):
    def __init__(self,email_handler,file_handler,database_handler):
        self.email_handler = email_handler
        self.file_handler = file_handler
        self.database_handler = database_handler
    
    def GetEmailReportAttachment(self, specific_date):
        try:
            self.email_handler.SelectCategory(FOLDER_FOR_WEEKLY_REVENUE)
            file_like_object = self.email_handler.FetchAttachments(specific_date)
            dataframe = pd.read_csv(file_like_object)
            grouped_dataframe =(
                dataframe.groupby(["Order Date", "Venue"])
                .apply(lambda x: x.drop(["Order Date", "Venue"], axis=1).to_dict(orient="records"))
                .reset_index(name="Orders")
            )
            # print(grouped_dataframe)
            self.database_handler.Save_Database("WeeklyItemBreakDown", "Order Date", grouped_dataframe)
            return dataframe.values.tolist()
        
        except Exception as e:
             print("Get Weekly Revenue function error",str(e))





class DailyLabourCostReport_EmailAPI(AbstractReportEmailAPI,DateOperations):
    def __init__(self, email_handler, file_handler, database_handler):

        self.email_handler = email_handler
        self.file_handler = file_handler
        self.database_handler = database_handler
        # print(self.database_handler)
    
    def GetEmailReportAttachment(self, specific_date):
        try:
            self.email_handler.SelectCategory(FOLDER_FOR_LABOUR_COST_DAILY)
            file_like_object = self.email_handler.FetchAttachments(specific_date)
            dataframe = pd.read_excel(file_like_object, engine="openpyxl")
            dataframe.fillna(0,inplace=True) #filling NA with zeros
            dataframe=dataframe[['Venue','Net Sales','Labour Total Cost (est)','Labour Total Cost as % of Total Net Sales']]
            dataframe['Date']=self.Change_Date_Format(old_format="%d-%b-%Y", new_format="%Y-%m-%d",date=specific_date)
            # print(dataframe)
            self.database_handler.Save_Database("DailyLabourCost",  "Date", dataframe)
            return dataframe.values.tolist()

        except Exception as e:
            print("Get_Email_Labour_cost_Daily function error",str(e))


class FileProcessor:
    def __init__(self,Excel_Engine="openpyxl"):
        self.Excel_Engine = Excel_Engine
    
    def process_excel(self,file_like_object, date, columns_to_keep, date_column_name, old_format, new_format):
        dataframe = pd.read_excel(file_like_object, engine=self.Excel_Engine)
        dataframe.fillna(0, inplace=True)
        dataframe = dataframe[columns_to_keep]
        dataframe[date_column_name] = datetime.strptime(date, old_format).strftime(new_format)
        return dataframe

    def process_csv(file_like_object):
        dataframe = pd.read_csv(file_like_object)
        grouped_dataframe = (
            dataframe.groupby(["Order Date", "Venue"])
            .apply(lambda x: x.drop(["Order Date", "Venue"], axis=1).to_dict(orient="records"))
            .reset_index(name="Orders")
        )
        return grouped_dataframe


class EmailHandler:
    def __init__(self, username, password, server="imap.gmail.com", port=993):
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.EmailObject = ""
    def ConnectGmail(self):
        self.EmailObject = imaplib.IMAP4_SSL(self.server, self.port)
        self.EmailObject.login(self.username, self.password)
        return self.EmailObject
    
    def SelectCategory(self,category):

        status,_= self.EmailObject.select(category)
        if status=='OK':
            return True
        else:
            return False
    
    def FetchAttachments(self, specific_date):
        try:
            status, all_emails = self.EmailObject.search(None, f'ON "{specific_date}"')
            if all_emails == [b'']:
                raise FileNotFoundError(f"No Email Found for the specific date: {specific_date}")

            for email_id in all_emails[0].split():
                status, msg_data = self.EmailObject.fetch(email_id, '(RFC822)')
                if status == "OK":
                    message = email.message_from_bytes(msg_data[0][1])
                    if message.is_multipart():
                        for part in message.walk():
                            if part.get("Content-Disposition") and "attachment" in part.get("Content-Disposition"):
                                return io.BytesIO(part.get_payload(decode=True))
            raise FileNotFoundError("No attachment found in the email.")
        except Exception as e:
            raise Exception(f"Error fetching attachment: {e}")


class DatabaseHandler:
    def __init__(self,database_name,connection_string):
        self.client = MongoClient(connection_string
    connectTimeoutMS=30000,
    socketTimeoutMS=None,
    socketKeepAlive=True,
    maxPoolSize=1
            )
        self.database_name = self.client[database_name]
        self.connection_string = connection_string

    def Save_Database(self,collection_name, date_column, dataframe):
        collection = self.database_name[collection_name]

        for single_dict in dataframe.to_dict(orient="records"):
            collection.update_one(
                {date_column: single_dict[date_column], "Venue": single_dict["Venue"]},
                {"$set": single_dict},
                upsert=True
            )

    
    def Fetch_Date(self,report_date,date_column,collection_name,branch=None):
        try:
            # print(collection_name)
            # assuming the collection is named "WeeklyRevenue" and the date is stored in "Order Date" field without hour/seconds e.g. 2024-12-02
            if branch:
                result=self.database_name[collection_name].find({date_column: report_date,"Venue": branch})
            else:
                result=self.database_name[collection_name].find({date_column: report_date})


            return pd.DataFrame(list(result))
        except Exception as e:
            print("Error fetching for specific date, Error : "+str(e))


    def Fetch_Missing_Date(self,start_date,end_date,date_column,collection_name,daily_labour_cost_report_obj,weekly_item_breakdown_report_obj):
            """
            2024-11-25
            """
            db_results = self.database_name[collection_name].find({date_column: {"$gte": start_date, "$lte": end_date}})
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            db_dates=[]
            for result in db_results:
                # print("result is",result)
                db_dates.append(result[date_column])
            db_dates=set(db_dates)
            # print(db_results,"db_results")
            # db_dates = {doc[date_column] for doc in db_results}
            expected_dates = {
                (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                for i in range((end_date - start_date).days + 1)
            }
            print("expected_dates",expected_dates)
            missing_dates = expected_dates - db_dates
            print("Missing dates:", missing_dates)

            print("db_dates",db_dates)
            if collection_name == "DailyLabourCost":
                for missing_date in missing_dates:
                    missing_date = datetime.strptime(missing_date, "%Y-%m-%d")
                    missing_date = missing_date.strftime("%d-%b-%Y")
                    # print("Missing date: is", missing_date)
                    daily_labour_cost_report_obj.GetEmailReportAttachment(missing_date)
            else:
                for missing_date in missing_dates:
                    missing_date = datetime.strptime(missing_date, "%Y-%m-%d")
                    missing_date = missing_date.strftime("%d-%b-%Y")
                    weekly_item_breakdown_report_obj.GetEmailReportAttachment(missing_date)

    def Fetch_Period(self,start_date,end_date,date_column,collection_name,branch=None):
        try:

            if branch:
                result=self.database_name[collection_name].find({date_column: {"$gte": start_date, "$lte": end_date},"Venue": branch})
            else:
                result=self.database_name[collection_name].find({date_column: {"$gte": start_date, "$lte": end_date}})
            
            return pd.DataFrame(list(result))
        except Exception as e:
            print("Error fetching for specific period, Error : "+str(e))




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

# weekly_item_breakdown_report_obj.GetEmailReportAttachment('2-Dec-2024')
# dataframe_list=daily_labour_cost_report_obj.GetEmailReportAttachment('12-Dec-2024')


# print(dataframe_list)

# print(database_handler_obj.Fetch_Date('2024-12-12',"Date","DailyLabourCost"))