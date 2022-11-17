from utils import get_choice, get_collection
import uuid

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
    abstract = None
    authors = input("Enter names of authors separate by a comma and a white space: ").split(", ")
    n_citations = 0
    references = []
    title = input("Enter title of the article: ")
    venue = None
    year = input("Enter year of the article: ")
    
    # Generate unique article id
    while True:
      id = str(uuid.uuid4())
      if self.collection.find_one({"id": id}) == None:
        break
    
    data = {
      "abstract": abstract,
      "authors": authors,
      "n_citations": n_citations,
      "references": references,
      "title": title,
      "venue": venue,
      "year": year,
      "id": id
    }
    
    self.collection.insert_one(data)

    
