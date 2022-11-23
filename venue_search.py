class TopVenues:
    def __init__(self, collection, referencing_view):
        self.col = collection
        self.rcol = referencing_view
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
            venue = va["_id"]["venue"]
            num_articles = va["num_articles"]
            self.venues[venue] = [num_articles]

    def get_top_venues(self, n):
        #---------implement---------
        # find top n venues by getting the number of articles referencing each venue
        # and sorting accordingly
        # then add info to self.venues
        # and return a list of the top n venues in order
        venue_references = self.rcol.aggregate([
            {
                "$group": {
                    "_id": {"venue": "$venue"},
                    "num_referencing": {"$sum": {"$size": "$referencing"}}
                }
            },
            {"$sort": {"num_referencing": -1}},
            {"$limit": n}
        ])
        venues = []
        for vr in venue_references:
            venue = vr["_id"]["venue"]
            venues.append(venue)
            num_referencing = vr["num_referencing"]
            self.venues[venue].append(num_referencing)
        return venues

    def show_venues(self, n):
        count = 1
        venues = self.get_top_venues(n)
        for venue in venues:
            num_articles = self.venues[venue][0]
            num_references = self.venues[venue][1]
            print(f"{count} venue: {venue}, ",
                  f"number of articles: {num_articles}, ",
                  f"number of references to venue's articles: {num_references}")
            count += 1
