from store import Store

# TODO: This function should be FIXED BEFORE submission.
# For debug purposes, the port is assumed to be 27017.
# otherwise we'd have to be prompted for the port 24/7 xd
def ask_for_port():
  if True:
    return 27017

  while True:
    try:
      port = int(input("What is the port?"))  
      return port
    except:
      print("That is not a valid port number!")


def main():
  port = ask_for_port()

  store = Store(port)
  store.show_main_menu()


if __name__ == "__main__":
  main()