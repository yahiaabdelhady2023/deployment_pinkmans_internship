import matplotlib
matplotlib.use('Agg')
#import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.tsa.stattools import adfuller
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import time
import datetime
import seaborn as sns
import io
import base64
from app.Models import *
from app.AggregateData import *
from datetime import date

# Get today's date
today = date.today()

# Format it as year-month-day
# two_weeks_ago = today - timedelta(weeks=20)

# # Print the date in the format 'YYYY-MM-DD'
# two_weeks_ago=two_weeks_ago.strftime('%Y-%m-%d')


end_date = today.strftime("%Y-%m-%d")
start_date='2023-09-01'

fetch_missing_start_date=today - timedelta(weeks=1)
fetch_missing_start_date=fetch_missing_start_date.strftime('%Y-%m-%d')

database_handler_obj.Fetch_Missing_Date(fetch_missing_start_date, end_date,"Order Date","WeeklyItemBreakDown",daily_labour_cost_report_obj,weekly_item_breakdown_report_obj)
dataframe=database_handler_obj.Fetch_Period(start_date,end_date,"Order Date","WeeklyItemBreakDown")
df = dataframe

# Explode the Orders column
df_exploded = df.explode('Orders', ignore_index=True)

# Convert the dictionaries in the Orders column to separate columns
Orders_df = pd.json_normalize(df_exploded['Orders'])

# Combine with parent-level columns
dataframe = pd.concat([df_exploded.drop(columns=['Orders']), Orders_df], axis=1)
DataFrame=dataframe
DataFrame=DataFrame[DataFrame['Gross Sale']!=0.0]
DataFrame.drop(['Lead Type','Tax Rate','Cost','Sales Type','Order ID','Order Time','Tax','Item Discount','Gross Sale'],axis=1,inplace=True)
DataFrame.isna().sum()

DataFrame['Order Date']=pd.to_datetime(DataFrame['Order Date'])
DataFrame['Sold Items']=1

# DataFrame=DataFrame[DataFrame['Venue']!='']
DataFrame = DataFrame[(DataFrame['Venue']!='Pinkmans - old market') & (DataFrame['Venue'] !='25A Old Market')]

all_branches=list(DataFrame['Venue'].unique())




def plot_per_branch(branch_name,item_name,start_date=None,end_date=None,y_axis_variable="Sold Items",return_ajax=False):
        if start_date is not None and end_date is not None:
                start_period = pd.to_datetime(start_date, format='%Y-%m-%d')
                end_period = pd.to_datetime(end_date, format='%Y-%m-%d')
        else:
            start_period = None
            end_period = None

        if branch_name != "All Branches":
                branch=DataFrame[DataFrame['Venue']==branch_name]
        else:
                branch=DataFrame

        branch=branch.groupby(['Order Date','PLU Name']).agg({'Net Sale': 'sum','Sold Items':'sum'}).reset_index()

        if item_name!="All Items":
                model=branch[branch['PLU Name']==item_name]
        else:
                model=branch.groupby('Order Date')[['Sold Items', 'Net Sale']].sum().reset_index()


        model=model.set_index('Order Date')
        if start_period and end_period:
                model=model[start_period:end_period]
        
        if start_date is None and end_date is None:
            # print("Before going to down, Order Date is",model.index)
            start_date = str(model.index[0])[:10]
            end_date = str(model.index[-1])[:10]
        rolling_mean = model[y_axis_variable].rolling(window=7).mean()
        xdate=model.index
        ydate=model[y_axis_variable]
        sumed_value = model[y_axis_variable].sum()
        default_text=f"Number Of Sold Items {sumed_value}"
        if y_axis_variable=="Net Sale":
            default_text=f"Net Sale Total Amount: {round(sumed_value,2)} £"
        plt.title(branch_name+" : "+item_name+f" {start_date} - {end_date} \n\n {default_text}", pad=20)
        plt.plot(xdate,ydate)
        plt.xticks(rotation=60)
        plt.tight_layout()
        plt.xlabel("Order Date",fontsize=16)
        if y_axis_variable =="Net Sale":
            y_axis_variable = y_axis_variable+" (£)"
        plt.ylabel(y_axis_variable,fontsize=16)
        plt.plot(rolling_mean)
        plt.legend(['Original','Mean'])

        plt.tight_layout()

        output = io.BytesIO()
        plt.savefig(output, format='png')  # Save the current figure
        plt.close()  # Close the current plot to free memory
        output.seek(0)
        
        if return_ajax==True:
            return  base64.b64encode(output.getvalue()).decode('utf-8')
        else:
            return  output.getvalue()
        


def show_categories_break_down(branch_name, start_date, end_date, category_name="SOFT DRINKS", return_ajax=False):
    if start_date is not None and end_date is not None:
        start_period = pd.to_datetime(start_date, format='%Y-%m-%d')
        end_period = pd.to_datetime(end_date, format='%Y-%m-%d')

    # Filter by branch
    if branch_name != "All Branches":
        selected_branch = DataFrame[DataFrame['Venue'] == branch_name]
    else:
        selected_branch = DataFrame

    # Convert date column
    selected_branch['Order Date'] = pd.to_datetime(selected_branch['Order Date'])
    selected_branch = selected_branch.set_index('Order Date')

    # Filter by date range
    if start_period is not None and end_period is not None:
        selected_branch = selected_branch[start_period:end_period]

    # Filter by category
    if category_name != "All Categories":
        category_data = selected_branch[selected_branch['PLU Category'] == category_name]
    else:
        category_data = selected_branch

    # Count sold items & sum net sales
    item_counts = category_data['PLU Name'].value_counts()
    net_sales = category_data.groupby('PLU Name')['Net Sale'].sum()

    # Take top 10 items
    top_items = item_counts[:10].index
    sold_counts = item_counts[top_items]
    net_sales = net_sales[top_items]

    # Bar settings
    x = np.arange(len(top_items))  # X-axis positions
    width = 0.4  # Bar width

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot bars side by side
    bars1 = ax.bar(x - width/2, sold_counts, width, label="Units Sold", color='blue', alpha=0.7)
    bars2 = ax.bar(x + width/2, net_sales, width, label="Net Sales (£)", color='red', alpha=0.7)

    # Add labels on Net Sales bars
    for bar in bars2:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"£{yval:,.2f}", ha='center', va='bottom', fontsize=10, color='red')

    for bar in bars1:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval:,.0f}", ha='center', va='bottom', fontsize=10, color='red')

    # Labels & Title
    ax.set_xticks(x)
    ax.set_xticklabels(top_items, rotation=90)
    ax.set_ylabel("Count / Net Sale (£)")
    ax.set_title(f"{branch_name}, Category: {category_name} ({start_date} - {end_date})")
    ax.legend()

    plt.tight_layout()

    # Save output as PNG
    output = io.BytesIO()
    plt.savefig(output, format='png')
    plt.close()
    output.seek(0)

    if return_ajax:
        return base64.b64encode(output.getvalue()).decode('utf-8')
    else:
        return output.getvalue()


# def show_categories_break_down(branch_name,start_date,end_date,category_name="SOFT DRINKS",return_ajax=False):
#     if start_date is not None and end_date is not None:
#                 start_period = pd.to_datetime(start_date, format='%Y-%m-%d')
#                 end_period = pd.to_datetime(end_date, format='%Y-%m-%d')

#     if branch_name != "All Branches":
#         selected_branch=DataFrame[DataFrame['Venue']==branch_name]
#     else:
#         selected_branch=DataFrame
#     selected_branch['Order Date']=pd.to_datetime(selected_branch['Order Date'])
#     selected_branch=selected_branch.set_index('Order Date')
#     if start_period is not None and end_period is not None:
#                 selected_branch=selected_branch[start_period:end_period]
#     if category_name != "All Categories":
#         values=selected_branch[selected_branch['PLU Category']==category_name]['PLU Name'].value_counts()
#     else:
#         values=selected_branch['PLU Name'].value_counts()

#     plt.bar(values.index[:10],values.values[:10])
#     values.index
#     plt.xticks(rotation=90)
#     plt.title(f"{branch_name}, Category Name : {category_name} {start_date} - {end_date}",pad=20)

#     for i in range(len(values.index[:10])):
#         plt.text(i,values.values[i],values.values[i], ha='center')

#     plt.tight_layout()
#     y=values.values[:10]
#     y_min, y_max = min(y), max(y)
#     buffer = (y_max - y_min) * 0.2  # 10% buffer for visual space

#     # Adjusting the y-axis dynamically
#     plt.ylim(y_min - buffer, y_max + buffer)

#     output = io.BytesIO()
#     plt.savefig(output, format='png')  # Save the current figure
#     plt.close()  # Close the current plot to free memory
#     output.seek(0)
    
#     if return_ajax==True:
#         return  base64.b64encode(output.getvalue()).decode('utf-8')
#     else:
#         return  output.getvalue()


def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'

def show_trends_per_branch(branch_name,start_date,end_date,item_name,type_of_trend,return_ajax=False):
    if start_date is not None and end_date is not None:
            start_period = pd.to_datetime(start_date, format='%Y-%m-%d')
            end_period = pd.to_datetime(end_date, format='%Y-%m-%d')

    print("start_period -->",start_period)
    if branch_name != "All Branches":
            branch=DataFrame[DataFrame['Venue']==branch_name]
    else:
            branch=DataFrame

    branch=branch.groupby(['Order Date','PLU Name']).agg({'Net Sale': 'sum','Sold Items':'sum'}).reset_index()



    if item_name!="All Items":
            branch=branch[branch['PLU Name']==item_name]
    else:
            branch=branch.groupby('Order Date')[['Sold Items', 'Net Sale']].sum().reset_index()

    branch=branch.set_index('Order Date')
    if start_period is not None and end_period is not None:
                branch=branch[start_period:end_period]
    if type_of_trend=="Weekly":
        branch[type_of_trend] = branch.index.day_name() #starting day of the week should be monday
        
    elif type_of_trend=="Monthly":
        branch[type_of_trend] = branch.index.month_name()
    else:
        branch[type_of_trend] = branch.index.month.map(get_season)
        # print(branch[type_of_trend])

    trend_sales = branch.groupby(type_of_trend)[['Sold Items','Net Sale']].sum()
    # trend_sales.plot(kind='bar',stacked=True  ,color=['Green', 'lightblue'], alpha=0.8)

    ax = trend_sales.plot(kind='bar')
    ax.legend(['Sold Items : Unit','Net Sale : £'])
    plt.title(f"{branch_name} Sold Items & Net Sale for whole period {item_name} {start_date} - {end_date}")
    for i in range(len(trend_sales['Sold Items'].values)):
        plt.text(i,trend_sales['Sold Items'].values[i],trend_sales['Sold Items'].values[i], ha='right')

    trend_sales['Net Sale']=trend_sales['Net Sale'].round().apply(int)
    for i in range(len(trend_sales['Net Sale'].values)):
        plt.text(i,trend_sales['Net Sale'].values[i],trend_sales['Net Sale'].values[i], ha='left')

    plt.title(f"{branch_name} for whole period {item_name} {start_date} - {end_date}")

    plt.tight_layout()

    output = io.BytesIO()
    plt.savefig(output, format='png')  # Save the current figure
    plt.close()  # Close the current plot to free memory
    output.seek(0)

    if return_ajax==True:
        return  base64.b64encode(output.getvalue()).decode('utf-8')
    else:
        return  output.getvalue()

def Get_All_Specific_Items(branch="All Branches"):
    if branch == "All Branches":
        return ["All Items"] + list(DataFrame['PLU Name'].unique())
    else:
        return ["All Items"] + list(DataFrame[DataFrame['Venue']==branch]['PLU Name'].unique())
    




def Get_All_Categories(branch="All Branches"):
    if branch == "All Branches":
        return ["All Categories"] + list(DataFrame['PLU Category'].unique())
    else:
        return ["All Categories"] + list(DataFrame[DataFrame['Venue']==branch]['PLU Category'].unique())
    

def Get_All_Branches():
     return   list(DataFrame['Venue'].unique()) + ["All Branches"]

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