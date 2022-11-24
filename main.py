from store import Store
from load_json import load_json

# TODO: This function should be FIXED BEFORE submission.
# For debug purposes, the port is assumed to be 27017.
# otherwise we'd have to be prompted for the port 24/7 xd
def ask_for_port():
  while True:
    try:
      port = int(input("What is the port? "))  
      return port
    except:
      print("That is not a valid port number!")


def main():
  load_data = input("Do you want to load data? (y/n): ").lower()
  if (load_data == "y" or load_data == "yes"):
    port = load_json()
  elif (load_data == "n" or load_data == "no"):
    port = ask_for_port()
  else:
    print("Invalid input!")
    quit()
  store = Store(port)
  store.show_main_menu()


if __name__ == "__main__":
  main()
