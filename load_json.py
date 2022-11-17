from utils import get_collection
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
    dblp = get_collection(port)
  except Exception as err:
    print("Connection error!", err)
    quit()
  
  dblp.drop()

  with f:
    for line in f:
      dblp.insert_one(json.loads(line.strip()))

  print("Document Store constructed!")
      
if __name__ == "__main__":
  main()
  