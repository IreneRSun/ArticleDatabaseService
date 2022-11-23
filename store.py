from utils import get_choice, get_collection, get_keyword
from author_searcher import AuthorSearchResults
import article_searcher
import uuid


class Store:
    def __init__(self, port):
        # Acquire MongoDB collection
        try:
            self.collection = get_collection("dblp", port)
        except Exception as err:
            print("Failed to establish MongoDB collection while constructing store!", err)
            quit()

    def show_main_menu(self):
        while True:
            # Which menu option does the user want to choose?
            chosen_choice = get_choice("What would you like to do?", [
                "Search for articles",
                "Search for authors",
                "List the venues",
                "Add an article",
                "Quit"
            ], allow_backtracking=False)

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
        # get keywords
        keywords = article_searcher.get_keywords()
        if not keywords:
            return
        # get matches
        search = article_searcher.ArticleSearchResults(self.collection, keywords)
        search.display_articles()
        # allow user to select articles
        while True:
            print("To select an article to see more information, enter the match number")
            num = get_num(limit=search.get_len())
            if num == -1:
                break
            search.select_article(num)

    def show_author_search(self):
        keyword = get_keyword()
        if keyword is not None:
            query = AuthorSearchResults(self.collection, keyword)
            query.display_results()

    def show_list_venues(self):
        pass

    def show_add_article(self):
        # Set up data
        abstract = None
        authors = input("Enter names of authors separate by a comma and a white space: ").split(", ")
        n_citations = 0
        references = []
        title = input("Enter title of the article: ")
        venue = None
        year = input("Enter year of the article: ")

        # Ask for unique article id
        while True:
            id = input("Enter ID of the article: ")
            if self.collection.find_one({"id": id}) is None:
                break

        # Insert data
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


# get a number from the user
def get_num(limit=float("inf")):
    while True:
        inp = input("Enter your input: ")
        if not inp.split():
            return -1
        if inp.lower() == "quit":
            quit()
        if inp.isdigit():
            if 0 < int(inp) <= limit:
                break
        print("Please enter a valid number")
    return inp
