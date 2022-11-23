import os
import pymongo

class PaginationData:
  """
    Utility class for pagination calculations
  """
  def __init__(self, options = [], page_limit = None):
    self.options = options
    self.page_limit = page_limit
    self.page = 0

  def has_next_page(self):
    return (self.page_limit != None) and (len(self.get_options()) == self.page_limit) and (self.page * self.page_limit < len(self.options))

  def has_prev_page(self):
    return self.page > 0

  def next_page(self):
    assert self.has_next_page()
    self.page += 1

  def prev_page(self):
    assert self.has_prev_page()
    self.page -= 1

  def get_option_index(self, choice):
    """
      Given a 0-index choice based on the displayed options and indexes, 
      return the option index associated with it.
    """
    assert choice >= 0 and choice < len(self.get_options())
    if self.page_limit == None:
      return choice
    return self.page * self.page_limit + choice

  def get_options(self):
    """ Return all options to list on the current page. """
    if self.page_limit == None:
      return self.options

    start_option_index = (self.page * self.page_limit)
    end_option_index = (((self.page + 1) * self.page_limit))
    return self.options[start_option_index:end_option_index]

def get_collection(name, port):
  """ Utility function to acquire MongoDB connection. """
  client = pymongo.MongoClient("localhost", port, serverSelectionTimeoutMS = 2000)
  client.server_info()

  database = client["291db"]
  collection = database[name]

  return collection

def get_keyword():
  """ Retrieve a single keyword from the user. """
  clear()
  while True:
    inp = input("Enter a single keyword you would like to search for: ")
    if inp.strip() == "":
      return None

    parts = inp.split()
    if len(parts) > 1:
      clear()
      print("Please only enter 1 keyword!")
      continue

    return parts[0]

def display_line():
  print("-" * 80)

def show_list(desc = None, options = [], page_limit = None):
  """
    Utility function to quickly list options with pagination support.

    desc: Optional text to display before listing items
    options: List of strings to list
    page_limit: Optional limit of options to show per page (this does not include the back option if allow_backtracking is True)

    Example usage:
    show_list(desc="Look at these items!", options=["a", "b", "c"])
  """
  clear()

  pagination = PaginationData(options=options, page_limit=page_limit)
  while True:
    if desc != None:
      print(desc)
    
    # get options to display
    displayed_options = pagination.get_options()

    # do we need to show the prev/next options?
    if pagination.has_next_page():
      print("Type next to retrieve the next page")
    if pagination.has_prev_page():
      print("Type prev to retrieve the prev page")
    print("Enter a blank line to go to the previous menu")
    display_line()

    # display options
    for line in displayed_options:
      print(f"- {line}")

    # Get user input
    answer = input()
    
    # user input handlers
    clear()
    if answer == "next" and pagination.has_next_page():
      pagination.next_page()
      continue
    elif answer == "prev" and pagination.has_prev_page():
      pagination.prev_page()
      continue

    # exit condition
    if answer.strip() == "":
      return

def get_choice(desc = None, options = [], allow_backtracking = True, page_limit = None):
  """
    Utility function to quickly create menus.

    Returns the index of the selected option.
    If allow_backtracking is True, a value of -1 can be returned if the user wishes 
    to go exit without choosing a choice.

    desc: Optional text to display before listing options
    options: List of strings to display as options
    allow_backtracking: Should an option be present to exit this menu returning -1 as the option selected
    page_limit: Optional limit of options to show per page (this does not include the back option if allow_backtracking is True)

    Example usage:
    chosen_index = get_choice(desc="Choose an option!", options=["a", "b", "c"], page_limit=2)
  """
  
  # Edgecase where there are no options to choose and we are unable to backtrack leading to
  # program error where it is indeterminate of what value should be returned as -1 is not an option.
  assert len(options) > 0 or allow_backtracking
  clear()
  
  pagination = PaginationData(options=options, page_limit=10)
  while True:
    if desc != None:
      print(desc)

    # Retrieve options to be displayed
    displayed_options = pagination.get_options()

    # Should we display the next/prev option?
    if pagination.has_next_page():
      print("Type next to retrieve the next page")
    if pagination.has_prev_page():
      print("Type prev to retrieve the prev page")

    if allow_backtracking:
      print("Enter a blank line or select the back option to go to the previous menu")

    # Print line
    if desc != None or allow_backtracking:
      display_line()

    # Display options
    current_pos = 1
    for line in displayed_options:
      print(f"{current_pos}) {line}")
      current_pos += 1

    # Display back button if enabled
    if allow_backtracking:
      print(f"{current_pos}) Back")

    # Get user input
    answer = input()

    # Handle pagination requests
    if answer == "next" and pagination.has_next_page():
      pagination.next_page()
      clear()
      continue
    elif answer == "prev" and pagination.has_prev_page():
      pagination.prev_page()
      clear()
      continue

    if allow_backtracking and answer.strip() == "":
      return -1

    # Parse answer
    try:
      answer = int(answer)
    except ValueError:
      clear()
      print("Please input a valid option.")
      display_line()
      continue
    
    # Ensure chosen option is within displayed bounds
    if (answer < 1) or (answer > current_pos) or (answer == current_pos and not allow_backtracking):
      clear()
      print("Please input a valid option.")
      display_line()
      continue

    # Return result
    clear()
    if answer == current_pos:
      # If the user wishes to return to the previous page
      return -1
    else:
      # If the user has chosen a selection
      chosen_display_index = answer - 1
      return pagination.get_option_index(chosen_display_index)
    

def clear():
  """Clears the screen of any printed text using platform dependent commands"""

  if os.name.startswith("nt"):  # Windows
    os.system("cls")
  else: # Linux
    os.system("clear")