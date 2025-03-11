from pymongo import MongoClient

client = MongoClient("mongodb+srv://facemessage78:So02KSZ21vKUmwW8@cluster0.o1rwl.mongodb.net/")
db = client["PinkmanDB"]
collection = db["WeeklyItemBreakDown"]

# Delete all documents from the collection
collection.delete_many({})

print("All documents removed successfully!")