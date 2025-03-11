import os
from dotenv import load_dotenv

load_dotenv()

x=os.getenv('COMPANY_CODE')
print(x)

from datetime import datetime, timedelta

# # Get today's date
# today = datetime.today()

# # Calculate the date for 14 days ago
# two_weeks_ago = today - timedelta(weeks=2)

# # Print the date in the format 'YYYY-MM-DD'
# print(two_weeks_ago.strftime('%Y-%m-%d'))



# Get today's date (assuming today is Monday)
today = datetime.today()

# Find the start of this week (Monday of the current week)
start_of_this_week = today - timedelta(days=today.weekday())

# Calculate the start of the 3-week period (2 weeks ago from the start of this week)
start_of_period = start_of_this_week - timedelta(weeks=2)

# The end of the 3-week period is the start of this week (Monday)
end_of_period = start_of_this_week

# Print the 3-week period
print(f"Start of the 3-week period: {start_of_period.strftime('%Y-%m-%d')}")
print(f"End of the 3-week period: {end_of_period.strftime('%Y-%m-%d')}")

