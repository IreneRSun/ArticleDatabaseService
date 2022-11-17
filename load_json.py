from utils import get_collection
import json

BATCH_SIZE = 10000

def load_json():
  file = input("Enter JSON file name: ")
  try:
    f = open(file, 'r')
  except FileNotFoundError:
    print("The file "+ file + " does not exist!")
    quit()

  try:
    port = int(input("Enter port number: "))
  except ValueError:
    print("Invalid input!")
    quit()

  try:
    dblp = get_collection(port)
  except Exception as err:
    print("Connection error!", err)
    quit()
  
  dblp.drop()

  current_batch = []
  with f:
    for line in f:
      current_batch.append(json.loads(line.strip()))

      if len(current_batch) == BATCH_SIZE:
        dblp.insert_many(current_batch)
        current_batch = []

  if len(current_batch) > 0:
    dblp.insert_many(current_batch)

  print("Document Store constructed!")
      
if __name__ == "__main__":
  load_json()
