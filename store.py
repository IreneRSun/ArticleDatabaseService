from utils import get_choice, get_collection, get_keyword, get_keywords, get_num
from author_searcher import AuthorSearchResults
from article_searcher import ArticleSearchResults
import uuid


class Store:
    def __init__(self, port):
        # Acquire MongoDB collection
        try:
            self.collection = get_collection("dblp", port)
        except Exception as err:
            print("Failed to establish MongoDB collection while constructing store!", err)
            quit()
        # Aquire MongoDB materialized view
        try:
            self.view = get_collection("venue-materialized-view", port)
        except Exception as err:
            print("Failed to establish MongoDB materialized view while constructing store!", err)
            quit()

    def show_main_menu(self):
        while True:
            # Which menu option does the user want to choose?
            chosen_choice = get_choice("What would you like to do?", [
                "Search for articles",
                "Search for authors",
                "List the top venues",
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
        print("To go back, enter a blank line")
        print("To quit, enter quit")
        # get keywords
        keywords = get_keywords()
        if not keywords:
            return
        # get matches
        search = ArticleSearchResults(self.collection, keywords)
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
        # get a number n from user
        print("To go back, enter a blank line")
        print("To quit, enter quit")
        print("Otherwise, enter how many venues to display")
        while True:
            n = get_num()
            if n == -1:
                return
            # get the top n venues
            top_venues = self.view.aggregate([
                {"$sort": {"venue_references": -1}},
                {"$limit": n}
            ])
            # display the info from the top venues
            count = 1
            for venue_info in top_venues:
                venue = venue_info["_id"]
                num_articles = venue_info["venue_count"]
                num_references = venue_info["venue_references"]
                print(f"{count} venue: {venue}, ",
                      f"number of articles: {num_articles}, ",
                      f"number of articles referencing venue: {num_references}")
                count += 1

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
