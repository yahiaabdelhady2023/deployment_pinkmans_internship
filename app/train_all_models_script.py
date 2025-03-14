from Models import *
from AggregateData import *
from MachineLearning import *

def Train_All_Models():
    try:
        today = datetime.today()
        
        # Find the start of this week (Monday of the current week)
        start_of_this_week = today - timedelta(days=today.weekday())
        
        # Calculate the start of the period (52 weeks ago from the start of this week)
        start_of_period = start_of_this_week - timedelta(weeks=2)
        
        # The end period is the start of this week (Monday)
        end_of_period = start_of_this_week
        
        print(f"Start of period: {start_of_period.strftime('%Y-%m-%d')}")
        print(f"End of period: {end_of_period.strftime('%Y-%m-%d')}")
        
        dataframe = database_handler_obj.Fetch_Period(
            start_of_period.strftime('%Y-%m-%d'),
            end_of_period.strftime('%Y-%m-%d'),
            "Order Date",
            "WeeklyItemBreakDown"
        )
        
        df = dataframe
        
        # Explode the Orders column
        df_exploded = df.explode('Orders', ignore_index=True)
        
        # Convert the dictionaries in the Orders column to separate columns
        Orders_df = pd.json_normalize(df_exploded['Orders'])
        
        # Combine with parent-level columns
        dataframe = pd.concat([df_exploded.drop(columns=['Orders']), Orders_df], axis=1)
        
        # Filter for SANDWICHES only
        # sandwiches_df = dataframe[dataframe['PLU Category'] == 'SANDWICHES']
        # sandwiches_df = dataframe
        # Get UNIQUE combinations of Venue and PLU Name
        venue_items = dataframe.groupby(['Venue', 'PLU Name']).size().reset_index()[['Venue', 'PLU Name']]
        
        print(f"Generating forecasts for {len(venue_items)} unique venue-item combinations")
        
        # Create a dictionary to store all forecasts by venue
        forecasts_by_venue = {}
        
        # Get current directory
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")
        
        # Create a 'forecasts' directory if it doesn't exist
        forecasts_dir = os.path.join(current_dir, 'forecasts')
        if not os.path.exists(forecasts_dir):
            os.makedirs(forecasts_dir)
            print(f"Created forecasts directory: {forecasts_dir}")
        
        for index, row in venue_items.iterrows():
            venue = row['Venue']
            food_item = row['PLU Name']
            
            print(f"Generating forecast for Venue: {venue}, Item: {food_item}")
            
            try:
                ml = MachineLearning(venue, 'SANDWICHES', food_item)
                ml.Prepare(dataframe)
                ml.Fit()
                
                # Get predictions
                predictions = ml.Predict(dataframe)
                
                # Debug
                print(f"Got {len(predictions)} predictions for {venue} - {food_item}")
                
                # Store predictions in our dictionary
                if venue not in forecasts_by_venue:
                    forecasts_by_venue[venue] = []
                    
                for pred in predictions:
                    # Add item name to each prediction
                    pred['Item Name'] = food_item
                    # Extract day of week
                    date_obj = datetime.strptime(pred['Next Week'], '%Y-%m-%d')
                    pred['Weekday'] = date_obj.strftime('%A')
                    forecasts_by_venue[venue].append(pred)
            except Exception as e:
                print(f"Error processing {venue} - {food_item}: {e}")
        
        # Print number of venues and total predictions
        print(f"Processed {len(forecasts_by_venue)} venues with forecasts")
        total_predictions = sum(len(forecasts) for forecasts in forecasts_by_venue.values())
        print(f"Total predictions: {total_predictions}")
        
        # Save forecasts to CSV files, one per venue
        for venue, forecasts in forecasts_by_venue.items():
            # Create a safe filename from venue name
            safe_venue_name = ''.join(c if c.isalnum() else '_' for c in venue)
            filename = os.path.join(forecasts_dir, f"forecasts_{safe_venue_name}.csv")
            
            if not forecasts:
                print(f"Warning: No forecasts to save for {venue}")
                continue
                
            # Convert to DataFrame
            forecast_df = pd.DataFrame(forecasts)
            
            # Reorder columns to have Weekday and Item Name first
            columns_order = ['Next Week', 'Weekday', 'Item Name', 'Forecast', 'Forecast Lower', 'Forecast Upper']
            forecast_df = forecast_df[columns_order]
            
            # Save to CSV with explicit handling
            try:
                forecast_df.to_csv(filename, index=False)
                file_size = os.path.getsize(filename)
                print(f"Saved forecasts for {venue} to {filename} ({file_size} bytes)")
            except Exception as e:
                print(f"Error saving CSV for {venue}: {e}")
        
        # Verify files were created
        saved_files = [f for f in os.listdir(forecasts_dir) if f.startswith("forecasts_")]
        print(f"Created {len(saved_files)} CSV files in {forecasts_dir}")
        for file in saved_files:
            full_path = os.path.join(forecasts_dir, file)
            print(f"  - {file} ({os.path.getsize(full_path)} bytes)")
        
        print("Generated all forecasts and saved to CSV files!")
    except Exception as e:
        print(f"An error occurred: {e}")


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


Train_All_Models()