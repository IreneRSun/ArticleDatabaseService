class TopVenues:
    def __init__(self, collection):
        self.col = collection
        self.venues = dict()
        self.add_venue_info()

    def add_venue_info(self):
        # get venue and article count for venue
        venue_articles = self.col.aggregate([
            {
                "$match": {
                    "venue": {"$ne": ""}
                }
            },
            {"$group":
                {
                    "_id": {"venue": "$venue"},
                    "num_articles": {"$sum": 1}
                }
            }
        ])
        # add them to the self.venues dictionary
        for va in venue_articles:
            venue = va["_id"]
            num_articles = va["num_articles"]
            self.venues[venue] = [num_articles]

    def load_venue_info(self):
        # creates an on-demand view, not used
        collection.aggregate([
            {
                "$match": {
                    "venue": {"$ne": ""}
            },
            {
                "$lookup": {
                    "from": "dblp",
                    "localField": "id",
                    "foreignField": "references",
                    "as": "referencing"
                }
            },
            {
                "$project": {
                    "id": 1,
                    "venue": 1,
                    "referencing": 1
                }
            },
            {"$merge": {"into": "referencing"}}
        ])

    def get_top_venues(self, n):
        #---------implement---------
        # find top n venues by getting the number of articles referencing each venue 
        # and sorting accordingly
        # then add info to self.venues
        # and return a list of the top n venues in order
        pass

    def show_venues(self, n):
        count = 0
        venues = self.get_top_venues(n)
        for venue in venues:
            num_articles = self.venues[venue][0]
            num_references = self.venues[venue][1]
            print(f"{count} id: {venue}, ",
                  f"number of articles: {num_articles}, ",
                  f"number of references to venue's articles: {num_references}")
            count += 1
