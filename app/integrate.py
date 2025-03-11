from Models import *


connection_string="mongodb+srv://facemessage78:So02KSZ21vKUmwW8@cluster0.o1rwl.mongodb.net/"
dataframe=pd.read_csv('testing\DB Export 1.csv')
dataframe['Venue'] = dataframe['Venue'].replace({'Pinkmans Whiteladies': 'Pinkmans - Whiteladies Road'})
dataframe = dataframe[~dataframe['Venue'].isin(['Pinkmans - old market', '25A Old Market','Pinkmans - Gloucester Road'])]

database_handler_obj = DatabaseHandler(database_name="PinkmanDB",connection_string=connection_string)
grouped_dataframe =(
    dataframe.groupby(["Order Date", "Venue"])
    .apply(lambda x: x.drop(["Order Date", "Venue"], axis=1).to_dict(orient="records"))
    .reset_index(name="Orders")
)
# print(grouped_dataframe)
database_handler_obj.Save_Database("WeeklyItemBreakDown", "Order Date", grouped_dataframe)


