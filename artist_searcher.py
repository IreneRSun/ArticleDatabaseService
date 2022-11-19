class ArticleSearchResult:
    def __init__(self, collection, keywords):
        self.col = collection
        self.keywords = keywords
        self.articles = self.retrieve()

    # retrieve all articles that match all those keywords
    def retrieve(self):
        # create search expression
        expr = []

        # construct expression for converting the year to a string
        convert = {
            "$addFields": {
                "str_year": {"$toString": "$year"}
            }
        }
        expr.append(convert)

        # construct expressions for each wildcard search
        for keyword in self.keywords:
            search = {
                "$match": {
                    "$or": [
                        {"title": {"$regex": keyword, "$options": "i"}},
                        {"authors": {"$regex": keyword, "$options": "i"}},
                        {"abstract": {"$regex": keyword, "$options": "i"}},
                        {"venue": {"$regex": keyword, "$options": "i"}},
                        {"str_year": {"$regex": keyword, "$options": "i"}},
                    ]
                }
            }
            expr.append(search)

        # find matches
        matches = self.col.aggregate(expr)

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
            
