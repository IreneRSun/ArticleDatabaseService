import os

# get keywords from user
def get_keywords():
    # print instructions
    print("Enter keywords to search for")
    print("Otherwise, to cancel this action, enter a blank line")
    print("If you wish to quit the program, enter quit")
    # get keywords
    keywords = input("Enter input: ")
    # check if the keyword is quit
    if keywords.lower() == "quit":
        quit()
    # return keywords
    keywords = keywords.split()
    return keywords

class ArticleSearchResult:
    def __init__(self, collection, keywords):
        self.col = collection
        self.keywords = self.process_keywords(keywords)
        self.articles = self.retrieve()

    # add double quotes to keyword string
    def double_quotes(self, keyword):
        return "\"" + keyword + "\""

    # process keywords into a string for searching
    def process_keywords(self, keywords):
        processed = map(self.double_quotes, keywords)
        processed = " ".join(processed)
        return processed

    # retrieve all articles that match all those keywords
    def retrieve(self):
        # find matches
        matches = self.col.aggregate([{
            "$match": {
                "$text": {
                    "$search": self.keywords
                }
            }
        }])

        return list(matches)

    # display id, title, year, and venue of each article in self.articles
    def display_articles(self):
        for i in range(1, len(self.articles) + 1):
            article = self.articles[i - 1]
            aid = article["id"]
            title = article["title"]
            authors = article["authors"]
            year = article["year"]
            venue = article["venue"]
            print(f"{i} id: {aid}, title: {title}, authors: {authors}, year: {year}, venue: {venue}")

    # get articles that reference the given article
    def get_referencing(self, aid):
        result = self.col.find({"references": aid})
        return result

    # select an article
    def select_article(self, num):
        # get the corresponding article
        index = num - 1
        article = self.articles[index]

        # print all fields of article
        aid = article["id"]
        title = article["title"]
        year = article["year"]
        venue = article["venue"]
        abstract = article["abstract"]
        authors = article["authors"]
        print(f"article id: {aid}, title: {title}, year: {year}, venue: {venue}, abstract: {abstract}, authors: {authors}")

        # prints fields for referencing articles
        referencing = self.get_referencing(aid)
        print("Referencing articles:")
        for r in referencing:
            rid = r["id"]
            rtitle = r["title"]
            ryear = r["year"]
            print(f"id: {rid}, title: {rtitle}, year: {ryear}")
