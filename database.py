from pymongo import MongoClient

client=MongoClient('localhost',27017)
print("✅ Connected successfully!")
db=client['flight_tracker']

flights_collection=db['flights']
flights_logs_collection=db['flights_logs']