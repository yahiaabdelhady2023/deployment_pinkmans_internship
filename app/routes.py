from flask import Flask, jsonify, render_template,request ,redirect, url_for, session,stream_with_context,Response, send_file
from functools import wraps
from requests_oauthlib import OAuth2Session
from app.Bridge import *
from app.GraphsToDisplay import *
import os
from dotenv import load_dotenv
import tempfile

import pandas as pd
import numpy as np
# import tensorflow as tf
import joblib
from apscheduler.schedulers.background import BackgroundScheduler


from flask import Blueprint, render_template
import numpy as np
# from app.rnn_model import load_saved_model, predict_new_data
# from app.forecast_sales_file import *




#Here the route functions
load_dotenv() 
COMPANY_CODE = os.getenv("COMPANY_CODE")
PASSWORD = os.getenv("COMPANY_PASSWORD")
######################################################################
def Is_SignedIn(original_function):
    @wraps(original_function)
    def function_wrapper(*args, **kwargs):
        if "logged" in session:
            return redirect(url_for('home'))
        return original_function(*args,**kwargs)
    return function_wrapper 


def Login_Required(original_function):
    @wraps(original_function)
    def function_wrapper(*args, **kwargs):
        if "logged" not in session:
            return redirect(url_for('Login'))
        return original_function(*args, **kwargs)
    return function_wrapper
######################################################################

"""
All Processing routes are list down here
"""

def ValidateLogin():
        company_code=request.form['id_company_code']
        password=request.form['id_password']


        if company_code ==COMPANY_CODE and password == PASSWORD:

            session['logged']=True
            return redirect(url_for('home'))
        else:
            invalid=1
            return render_template("login.html",invalid=invalid)







######################################################################

"""
All AJAX requests are list down here
"""


def Update_Plot_Graph():

    data = request.get_json()  
    specific_Item = data.get('specific_Item')
    branch = data.get('branch')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    type_of_graph=data.get('type_of_graph')
    type_of_trend=data.get('type_of_trend')
    category=data.get('category')
    is_net_sale = data.get('is_net_sale')
    # print("important category is",category)


    # print("type of graph: " + type_of_graph)
    # print("type of trend: " + type_of_trend)
    # print("branch: " + branch)
    # print("specific_Item: " + specific_Item)
    # print("category: " + category)
    # print("start_date: " + start_date)
    # print("end_date: " + end_date)
    try:
        if type_of_graph=="Specific Item Graph":
            image_to_display=plot_per_branch(branch,specific_Item,start_date,end_date,return_ajax=True)
        elif type_of_graph=="Specific Item Graph Net Sale":
            image_to_display=plot_per_branch(branch,specific_Item,start_date,end_date,return_ajax=True,y_axis_variable="Net Sale")

        elif type_of_graph=="Category BreakDown Graph":
             image_to_display=show_categories_break_down(branch,start_date,end_date,category,return_ajax=True)
        else:
            image_to_display=show_trends_per_branch(branch,start_date,end_date,specific_Item,type_of_trend,return_ajax=True)
    except Exception as e:
        print("Exception occured while trying to make image",e)
        return jsonify({'image': "error"})
    
    return jsonify({'image': image_to_display})

def Update_Branch_Specific_Items_Graph():
    data = request.get_json() 
    branch = data.get('branch')
    all_specific_items=Get_All_Specific_Items(branch)
    all_categories=Get_All_Categories(branch)
    return jsonify({'all_specific_items': all_specific_items,'all_categories':all_categories})


def plot_png():

    image_to_display=plot_per_branch("All Branches",'All Items')

    # Return the image as a response with the correct MIME type
    return Response(image_to_display, mimetype='image/png')



def DisplayNewReport():
    Report_to_display_details=request.get_json(force=True)
    #print("----------------------------------------------------------------")
    #print(Report_to_display_details)
    #print("----------------------------------------------------------------")
    branchname,start_date,end_date,report_type_text,report_type_id=Report_to_display_details
    # report_id=DatabaseBridge.Get_Selected_Unique_ReportID(branchname,start_date,end_date,report_type_id)
    # start_date="2024-12-12"
    # end_date="2024-12-12"
    # Report_Date=str(start_date)+" - "+str(end_date)

    columns_two=[]
    columns_dataset_two=[]

    if int(report_type_id)==2:
   

        bridge_connector=Bridge()


        # dataset,Top_Sold_Specific_Items,Top_Sold_Categories,Total_Items_Sale,Branch_Total_Net_Sales,Top_Item,Top_Category,label_names,data_values,branchname,columns,columns_dataset,columns_dataset_two,columns_two=Return_Report_Dataset(2,branchname,start_date,end_date,report_id,report_type_text)
        # label_names,data_values,dataset,Total_Net_Sales, Top_Sold_Specific_Items,Top_Sold_Categories,Top_Item,Top_Category, Total_Items_Sale, Branch_Total_Net_Sales, columns_dataset_two,columns_two  ,columns,columns_dataset,Report_Date = bridge_connector.GetDailyReportDataset_Bridge(start_date,end_date,branchname)
        label_names, data_values ,dataset , Total_Net_Sales,  Top_Sold_Specific_Items , Top_Sold_Categories, Top_Item, Top_Category, \
        Total_Items_Sale, Branch_Total_Net_Sales,columns_dataset_two ,columns_two, columns, columns_dataset, Report_Date = bridge_connector.GetWeeklyItemBreakDownDataset_Bridge(start_date,end_date,report_type_text,branchname)

        all_data={"dataset":dataset,"Top_Sold_Specific_Items":Top_Sold_Specific_Items,"Top_Sold_Categories":Top_Sold_Categories
                  ,"Total_Items_Sale":Total_Items_Sale,"Total_Net_Sales":Branch_Total_Net_Sales
                  ,"Top_Item":Top_Item,"Top_Category":Top_Category,"label_names":label_names,"data_values":data_values,"Report_Date":Report_Date,"branchname":branchname,"columns":columns,"columns_dataset":columns_dataset,"columns_dataset_two":columns_dataset_two,"columns_two":columns_two}
    else:
        bridge_connector=Bridge()
        # label_names,data_values,dataset,Total_Net_Sales,branchname,columns,columns_dataset=Return_Report_Dataset(int(report_type_id),branchname,start_date,end_date)
        label_names,data_values,dataset,Total_Net_Sales,columns,columns_dataset,Report_Date=bridge_connector.GetDailyReportDataset_Bridge(start_date,end_date,branchname)
        all_data={"label_names":label_names,"data_values":data_values,"Report_Date":Report_Date,"dataset":dataset,"Total_Net_Sales":Total_Net_Sales,"branchname":branchname,"columns":columns,"columns_dataset":columns_dataset}

    return jsonify(all_data)


def GetBranchesForReport():
    message=request.get_json(force=True)

    bridge_connector=Bridge()
    report_id_type=message[-1]

    if int(report_id_type)==4:
        all_branches_for_specific_report=bridge_connector.GetDailyReportBranches_Bridge(message[0],message[1])
    else:
        all_branches_for_specific_report=bridge_connector.GetWeeklyItemReportBranches_Bridge(message[0],message[1])
    #print(all_branches_for_specific_report)
    return jsonify(all_branches_for_specific_report)

######################################################################

"""
Page Routes are listed down here
"""

@Login_Required
def Home():
        all_specific_items=Get_All_Specific_Items()
        all_branches=Get_All_Branches()

        return render_template("home.html",all_specific_items=all_specific_items,all_branches=all_branches)






@Is_SignedIn
def Login():
    return render_template("login.html")

    




@Login_Required
def Graphs():
    """
    all_branches_names
    dataset
    initial_chart_type
    Report_Date
    label_names
    report_dates_for_displaying
    columns
    columns_dataset
    """
    
    initial_chart_type="pie"

    # Report_Date='2010-03-01 // 2010-03-04'

    # label_names=['Glouchester RD','Whiteladies RD','Trynm RD2']
    # dataset={"labels":label_names,"data":[0,0,0]}
    # Total_Net_Sales=12434.5
    # columns=['x','y','z']
    # columns_dataset=[[1,2,3],[2,3,4]]
    bridge_connector=Bridge()
    label_names,data_values,dataset,Total_Net_Sales,columns,columns_dataset,Report_Date=bridge_connector.GetDailyReportDataset_Bridge("2024-12-12","2024-12-12")
    report_dates_for_displaying=['2020','2021']
    report_type_id_default=4

    #print("label_names are",label_names)
    #print("columns are",columns)
    #print("columns_dataset is",columns_dataset)
    #print("report_date is",Report_Date)
    #print("Total_Net_Sales",Total_Net_Sales)
    return render_template("graphs.html",branches=label_names,dataset=dataset,initial_chart_type=initial_chart_type,Report_Date=Report_Date,Report_Branches=label_names,report_dates_for_displaying=report_dates_for_displaying,Total_Net_Sales=round(Total_Net_Sales),id_report_type_id=report_type_id_default,columns=columns,columns_dataset=columns_dataset)

@Login_Required
def MachineLearning():
    tables_data = {
        "Fruits": [
            {"Name": "Apple", "Color": "Red", "Price": 1.2},
            {"Name": "Banana", "Color": "Yellow", "Price": 0.5},
        ],
        "Vegetables": [
            {"Name": "Carrot", "Color": "Orange", "Price": 0.8},
            {"Name": "Spinach", "Color": "Green", "Price": 1.5},
        ]
    }
    bridge_connector=Bridge()
    tables_data=bridge_connector.MachineLearningPredications()
    print("tables_data is",tables_data)
    return render_template("machine_learning.html",tables=tables_data)

@Login_Required
def TrainMachineLearning():
    return render_template('train_machine_learning.html')

@Login_Required
def UseMachineLearning():
    data = request.get_json() 
    branch = data.get('branch')
    food_item = data.get('food_item')
    print("Inside UseMachineLearning",branch,food_item)
    return jsonify({'MachineLearningData': "error"})


def SignOut():
    session.clear()
    return redirect(url_for('Login'))


@Login_Required
def UserManual():
    return render_template('user_manual.html')


branches = {
    "Branch A": [{"Item": "Item 1", "Expected Future Sales": 100, "Upper Future Sales": 120},
                 {"Item": "Item 2", "Expected Future Sales": 150, "Upper Future Sales": 180}],
    
    "Branch B": [{"Item": "Item 1", "Expected Future Sales": 200, "Upper Future Sales": 250},
                 {"Item": "Item 2", "Expected Future Sales": 300, "Upper Future Sales": 350}],
    
    "Branch C": [{"Item": "Item 1", "Expected Future Sales": 180, "Upper Future Sales": 220},
                 {"Item": "Item 2", "Expected Future Sales": 260, "Upper Future Sales": 300}],
}


def download_csv():
    branch = request.args.get('branch')
    if branch not in branches:
        return "Branch not found", 404

    df = pd.DataFrame(branches[branch])
    csv_filename = f"{branch}_sales.csv"
    with tempfile.NamedTemporaryFile(mode="w", newline="", delete=False, suffix=".csv") as temp_file:
                csv_filename = temp_file.name  # Get the temp file path
                df.to_csv(csv_filename, index=False)
    

    return send_file(csv_filename, as_attachment=True, mimetype='text/csv')


# def machine_learning_view():
#     # forecast_data = {branch: forecast_sales(branch) for branch in branches}
#     # forecast_data = forecast_sales(branches)
#     model = load_saved_model()

#     # Generate example input data (replace with your actual data)
#     new_data = np.random.rand(1, 10, 1)  # 1 sample, 10 time steps, 1 feature

#     # Get predictions
#     predictions_branches = predict_new_data(model, new_data)
#     predictions_branches["Last Updated" +str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     return render_template('machine_learning_view.html', branches=predictions_branches)










