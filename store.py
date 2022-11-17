from utils import get_choice, get_collection

class Store:
  def __init__(self, port):
    # Acquire MongoDB collection
    try:
      self.collection = get_collection(port)
    except Exception as err:
      print("Failed to establish MongoDB collection while constructing store!", err)
      quit()

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

      # Run action selected
      if chosen_choice == 0:
        # search for articles
        self.show_article_search()

      elif chosen_choice == 1:
        # search for authors
        self.show_author_search()

      elif chosen_choice == 2:
        # list the venues
        self.show_list_venues()

      elif chosen_choice == 3:
        # add an article
        self.show_add_article()

      elif chosen_choice == 4:
        # quit program
        return

  def show_article_search(self):
    pass

  def show_author_search(self):
    pass

  def show_list_venues(self):
    pass

  def show_add_article(self):
    pass