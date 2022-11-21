from utils import get_collection
from time import time
from pymongo import TEXT
import math
import json

BATCH_SIZE = 10000

def load_json():
  # Get JSON file
  file = input("Enter JSON file name: ")
  try:
    f = open(file, 'r')
  except FileNotFoundError:
    print("The file "+ file + " does not exist!")
    quit()

  # Get port number
  try:
    port = int(input("Enter port number: "))
  except ValueError:
    print("Invalid input!")
    quit()

  # Acquire MongoDB collection
  try:
    dblp = get_collection(port)
  except Exception as err:
    print("Connection error!", err)
    quit()
  
  dblp.drop()

  start_time = time()

  # Insert JSON file into MongoDB
  current_batch = []
  with f:
    for line in f:
      current_batch.append(json.loads(line.strip()))

      if len(current_batch) == BATCH_SIZE:
        dblp.insert_many(current_batch)
        current_batch = []

  if len(current_batch) > 0:
    dblp.insert_many(current_batch)

  # Create index
  dblp.aggregate([
        {"$addFields": {"year_str": {"$toString": "$year"}}},
        {"$out": "dblp"}
  ])
  
  dblp.create_index(
      keys = [
          ("title", TEXT),
          ("authors", TEXT),
          ("abstract", TEXT),
          ("venue", TEXT),
          ("year_str", TEXT)
      ],
      default_language='none'
  )
  
  dblp.create_index(
      keys = [
          ("references", 1)
      ],
      default_language='none'
  )

  seconds_to_construct = math.ceil(time() - start_time)
  print(f"Document store constructed in {seconds_to_construct}s!")
  
      
if __name__ == "__main__":
  load_json()
