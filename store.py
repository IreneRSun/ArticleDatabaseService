from utils import get_choice

class Store:
  def __init__(self):
    pass

  def show_main_menu(self):
    while True:
      options = [
        "Search for articles",
        "Search for authors",
        "List the venues",
        "Add an article",
        "Quit"
      ]
      chosen_choice = get_choice("What would you like to do?", options, allow_backtracking=False)

      if chosen_choice == 0:
        # search for articles
        pass
      elif chosen_choice == 1:
        # search for authors
        pass
      elif chosen_choice == 2:
        # list the venues
        pass
      elif chosen_choice == 3:
        # add an article
        pass
      elif chosen_choice == 4:
        # quit program
        return