import os
import pymongo

def get_collection(port):
  """
    Utility function to acquire MongoDB connection.
  """
  client = pymongo.MongoClient("localhost", port, serverSelectionTimeoutMS = 2000)
  client.server_info()

  database = client["291db"]
  collection = database["dblp"]

  return collection

def display_line():
  print("-" * 80)

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
    chosen_index = get_choice("Choose an option!", ["a", "b", "c"])
  """
  
  # Edgecase where there are no options to choose and we are unable to backtrack leading to
  # program error where it is indeterminate of what value should be returned as -1 is not an option.
  assert len(options) > 0 or allow_backtracking
  clear()
  
  current_page = 0
  while True:
    if desc != None:
      print(desc)

    # Pagination setup
    in_need_of_pagination = page_limit != None
    is_on_first_page = current_page == 0  # Hide prev option
    is_on_last_page = (not in_need_of_pagination) # Calculated later if pagination is needed but used to hide next option

    # Retrieve options to be displayed
    if page_limit == None:
      # List all options without pagination
      displayed_options = options
    else:
      # Pagination is required
      start_option_index = (current_page * page_limit)
      end_option_index = (((current_page + 1) * page_limit))
      displayed_options = options[start_option_index:end_option_index]

      # Case scenario in which multiple pages are needed, list instructions
      if len(displayed_options) != len(options):
        # We will be using prev or next since not all options are displayed
        in_need_of_pagination = True

        # Should we display the next option?
        if end_option_index < len(options):
          print("Type next to retrieve the next page")
        else:
          is_on_last_page = True # Hide next option

        # Should we display the prev option?
        if current_page > 0:
          print("Type prev to retrieve the prev page")

    # Print line
    if desc != None:
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
    if answer == "next" and in_need_of_pagination and (not is_on_last_page):
      current_page += 1
      clear()
      continue
    elif answer == "prev" and in_need_of_pagination and (not is_on_first_page):
      current_page -= 1
      clear()
      continue

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

      # Handle pages
      if page_limit != None:
        # Return chosen_display_index with page offset
        return (page_limit * current_page) + chosen_display_index
      else:
        # No page offset present, return index chosen
        return chosen_display_index
    

def clear():
  """Clears the screen of any printed text using platform dependent commands"""

  if os.name.startswith("nt"):  # Windows
    os.system("cls")
  else: # Linux
    os.system("clear")