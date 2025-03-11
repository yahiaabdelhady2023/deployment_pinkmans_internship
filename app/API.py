#API such as email API and google API and gmail API

import pandas as pd
import imaplib
import email
from email.header import decode_header
import os
import openpyxl
import io

from pymongo import MongoClient
from datetime import datetime

#IMPORTANT NOTE:
"""
folder name has to be named like '"X_name"', not "x_name" or 'x_name', otherwise IMAPLIB won't be able to handle it properly
"""
FOLDER_FOR_LABOUR_COST_DAILY='"Daily Revenue and Labour Report"'
FOLDER_FOR_WEEKLY_REVENUE='"Pinkmans - Weekly Revenue and Cost of Sales Report"'
KOBAS_EMAIL="mailer@kobas.co.uk"
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993  # Port for SSL

#Gmail account credentials
EMAIL = 'facemessage78@gmail.com'
PASSWORD = 'kulu imye mavn cyny' 



class DateOperations:
    def Get_Today_Date(self):
        return pd.Timestamp.now().strftime("%Y-%m-%d")
    
    def Change_Date_Format(self,old_format,new_format,date):
        date_obj = datetime.strptime(date, old_format)
        formatted_date = date_obj.strftime(new_format)
        return formatted_date
    


class DBOperations:
    def __init__(self):
        self.client = MongoClient("mongodb+srv://facemessage78:So02KSZ21vKUmwW8@cluster0.o1rwl.mongodb.net/")
        self.DB=self.client['PinkmanDB']
        self.WeeklyRevenue_Collection = self.DB["WeeklyRevenue"]
        self.DailyRevenue_Collection = self.DB["DailyRevenue"]
        
        self.WeeklyRevenue_Collection.create_index([("Order Date", 1), ("Venue", 1)], unique=False)
        self.DailyRevenue_Collection.create_index([("Date", 1), ("Venue", 1)], unique=False)

        self.data_dict={}
        self.greater_than_or_equal="$gte" #keyword built in MongoDB used for start_date comparsion [finding starting date range]
        self.less_than_or_equal="$lt" #keyword built in MongoDB used for end_date comparsion [finding ending date range]
        """
        these two above useful for finding a date inside a specific date range e.g.

        start_date=12-14-2024
        end_date=12-16-2024
        would yield all dates inside it and including these two as it is equal as well not only greater/less than
        """

        self.date_column=""

    def SetDataDictionary(self,dataframe):
        self.data_dict=dataframe.to_dict(orient="records")

    def Save_Database(self,collection,data_dict):
        # collection.insert_many(data_dict)
        for single_dict in data_dict:
            collection.update_one(
                {self.date_column: single_dict[self.date_column], "Venue": single_dict["Venue"]},  # Filter to match existing records
                {
                    "$set": single_dict  # Update fields with new values
                },
                upsert=True  # If no match found, insert a new document
            )




    def Save_DailyRevenue(self):
        self.Save_Database(self.DailyRevenue_Collection,self.data_dict)


    def Save_WeeklyRevenue(self):
        self.Save_Database(self.WeeklyRevenue_Collection,self.data_dict)

    def GetWeeklyRevenue_Specific_Date(self,report_date,branch=None):
        try:
            # assuming the collection is named "WeeklyRevenue" and the date is stored in "Order Date" field without hour/seconds e.g. 2024-12-02
            if branch:
                result=self.WeeklyRevenue_Collection.find({"Order Date": report_date,"Venue": branch})
            else:
                result=self.WeeklyRevenue_Collection.find({"Order Date": report_date})

            return pd.DataFrame(list(result))
        except Exception as e:
            print("Error fetching Weekly Revenue for specific date, Error : "+str(e))

    def GetDailyRevenue_Specific_Date(self,report_date,branch=None):
        try:
            # assuming the collection is named "DailyRevenue" and the date is stored in "Order Date" field without hour/seconds e.g. 2024-12-02
            if branch:
                result=self.DailyRevenue_Collection.find({"Date": report_date,"Venue": branch})
            else:
                result=self.DailyRevenue_Collection.find({"Date": report_date})
        
            return pd.DataFrame(list(result))
        except Exception as e:
            print("Error fetching Daily Revenue for specific date, Error : "+str(e))

    def GetWeeklyRevenue_Specific_Period(self, start_date, end_date,branch=None):
        try:
            if branch:
                result=self.WeeklyRevenue_Collection.find({"Order Date": {"$gte": start_date, "$lt": end_date},"Venue": branch})
            else:
                result=self.WeeklyRevenue_Collection.find({"Order Date": {"$gte": start_date, "$lt": end_date}})
            
            return pd.DataFrame(list(result))
    
        except Exception as e:
            print("Error fetching Weekly Revenue for specific period, Error : "+str(e))
    
    def GetDailyRevenue_Specific_Period(self, start_date, end_date, branch=None):
        try:
            if branch:
                result=self.DailyRevenue_Collection.find({"Date": {"$gte": start_date, "$lt": end_date},"Venue": branch})
            else:
                result=self.DailyRevenue_Collection.find({"Date": {"$gte": start_date, "$lt": end_date}})
            
            return pd.DataFrame(list(result))
        except Exception as e:
            print("Error fetching Daily Revenue for specific period, Error : "+str(e))



class IGetReportsEmailAPI(DBOperations,DateOperations):
    def __init__(self):
        super().__init__()

    def Connect_to_Gmail(self,category_to_select="inbox"):
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            mail.login(EMAIL, PASSWORD)
            mail.select(category_to_select)
            #returning mail object so it can be used for other operations
            return mail
        except Exception as e:
            print("Error Failed connecting to Gmail to get Excel files, Error : "+str(e))
    
    def Find_Email(self,category,specific_date):
        """
        using the above details it fetches the Excel file from GMAIL
        only for Labour cost

        (in DD-MMM-YYYY format)
        """
        try:
            mail=self.Connect_to_Gmail(category)

            status, all_emails = mail.search(None, f'ON "{specific_date}"')

            if all_emails == [b'']:
                return f"Error No Email Found for that specific date {specific_date}"
            

            """
            handling the email found, via getting the attachments then return file_like_object to be handled by pandas
            dataframe then it will stored in database
            """
            
            for email_id in list(all_emails):
                status, msg_data = mail.fetch(email_id, '(RFC822)')

                if status == "OK":
                        message_Object = email.message_from_bytes(msg_data[0][1])  # converting email bytes to message object
                        if message_Object.is_multipart():
                            for part in message_Object.walk():
                                content_disposition = str(part.get('Content-Disposition'))
                                if "attachment" in content_disposition:
                                        file_like_object = io.BytesIO(part.get_payload(decode=True))
            return file_like_object
        except Exception as e:
             print("Find Email function error",str(e))
        

    def Get_Email_Labour_cost_Daily(self,specific_date="05-Nov-2010"):
        """
        Get Email Labour Cost Daily which is Excel file from label/category
        Daily Revenue and Labour Report in Gmail
        """
        
        try:

            file_like_object = self.Find_Email(FOLDER_FOR_LABOUR_COST_DAILY,specific_date)
            dataframe = pd.read_excel(file_like_object, engine="openpyxl")
            dataframe.fillna(0,inplace=True) #filling NA with zeros
            dataframe=dataframe[['Venue','Net Sales','Labour Total Cost (est)','Labour Total Cost as % of Total Net Sales']]
            dataframe['Date']=self.Change_Date_Format(old_format="%d-%b-%Y", new_format="%Y-%m-%d",date=specific_date)
            self.SetDataDictionary(dataframe)
            print(dataframe)
            self.date_column="Date"

        except Exception as e:
            print("Get_Email_Labour_cost_Daily function error",str(e))

    def Get_Weekly_Revenue(self, specific_date="25-Nov-2024"):
        """
        Get Email Get_Weekly_Revenue which is CSV file from label/category
        Pinkmans - Weekly Revenue and Cost of Sales Report in Gmail
        """
        try:
            file_like_object = self.Find_Email(FOLDER_FOR_WEEKLY_REVENUE,specific_date)
            dataframe = pd.read_csv(file_like_object)
            grouped_dataframe =(
                dataframe.groupby(["Order Date", "Venue"])
                .apply(lambda x: x.drop(["Order Date", "Venue"], axis=1).to_dict(orient="records"))
                .reset_index(name="Orders")
            )
            self.SetDataDictionary(grouped_dataframe)
            # print(grouped_dataframe)
            self.date_column="Order Date"
        except Exception as e:
             print("Get Weekly Revenue function error",str(e))

        


obj=IGetReportsEmailAPI()
# obj.Get_Weekly_Revenue("09-Dec-2024")
# obj.Save_WeeklyRevenue()
# print(obj.GetWeeklyRevenue_Specific_Period('2024-11-02','2024-11-04'))
obj.Get_Email_Labour_cost_Daily('14-Dec-2024')
