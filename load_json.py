import pymongo
import json

def main():
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
    client = pymongo.MongoClient("localhost", port, serverSelectionTimeoutMS = 2000)
    client.server_info()
  except:
    print("Connection error!")
    quit()
  
  mini_project_2 = client.mini_project_2
  mini_project_2.dblp.drop()
  dblp = mini_project_2.dblp

  with f:
    for line in f:
      dblp.insert_one(json.loads(line.strip()))
      
if __name__ == "__main__":
  main()
  