from utils import get_collection
from time import time
from pymongo import TEXT
import math
import subprocess
import json

BATCH_SIZE = 10000

# Writes a new file in which the years is marked as an string
# this new file is then loaded by mongoimport
# speeds up insertion process from my experiments for larrger files.
def convert_years_to_str(f):
  outputF = open("./tmp/data.json", "w")
  with outputF:
    with f:
      for line in f:
        data = json.loads(line.strip())
        data["year"] = str(data["year"])
        outputF.write(json.dumps(data))
        outputF.write("\n")
      

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
    dblp = get_collection("dblp", port)
    materialView = get_collection("material-view-test", port)
  except Exception as err:
    print("Connection error!", err)
    quit()
  dblp.drop()
  materialView.drop()

  # # track the start time of how long it takes to finish everything.
  start_time = time()

  convert_years_to_str(f)
  importProc = subprocess.Popen(f"mongoimport --collection=dblp --file=tmp/data.json --port {port} --numInsertionWorkers=10 --batchSize 10000 --db 291db", shell=True, stdout=subprocess.PIPE)
  importProc.wait()

  print(f"Finished writing all rows to database in {math.ceil(time() - start_time)}s! Running index creation...")
  
  # # Create the index we need.
  dblp.create_index(
      keys = [
          ("references", TEXT),
          ("title", TEXT),
          ("abstract", TEXT),
          ("venue", TEXT),
          ("authors", TEXT),
          ("years", TEXT),
      ],
      default_language='none'
  )

  seconds_to_add_data = math.ceil(time() - start_time)
  print(f"Finished index creation and row insertion in {seconds_to_add_data}s! Running precomputations...")

  dblp.aggregate([
    {
        "$match": { # ignore venues that don't exist.
            "venue": {"$ne": ""}
        }
    },
    {
      "$lookup": {  # find all references for each publication
        "from": "dblp",
        "localField": "id",
        "foreignField": "references",
        "as": "referencing"
      }
    },
    {
      "$project": { # acquire size of said references count
        "id": 1,
        "venue": 1,
        "num_of_references": {
          "$size": "$referencing"
        }
      }
    },
    {             # group by venue and count the venue_count and the references of each venue
      "$group": {
        "_id": "$venue",
        "venue_count": {
          "$sum": 1
        },
        "num_of_references": {
          "$sum": "$num_of_references"
        }
      }
    },
    {         # material push
      "$merge": {
        "into": "material-view-test"
      }
    }
  ])
  
  seconds_to_construct = math.ceil(time() - start_time)
  print(f"Document store constructed and precomputations computed in {seconds_to_construct}s!")
  
      
if __name__ == "__main__":
  load_json()
