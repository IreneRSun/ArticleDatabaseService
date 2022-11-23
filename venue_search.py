class TopVenues:
    def __init__(self, venue_view):
        self.view = venue_view
        self.venues = self.load_venues()

    def load_venues(self):
        # get sorted list of venue info
        ordered_venues = self.view.aggregate([
            {"$sort": {"venue_references": -1}}
        ])
        return list(ordered_venues)

    def show_venues(self, n):
        # print the first n items of self.venues
        for i in range(0, n):
            venue = self.venues[i]
            num_articles = venue["venue_count"]
            num_references = venue["venue_references"]
            print(f"{i+1} venue: {venue}, ",
                  f"number of articles: {num_articles}, ",
                  f"number of references to venue's articles: {num_references}")
