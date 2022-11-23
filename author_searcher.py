import re
from utils import show_list, get_choice

class AuthorSearchResults:
  def __init__(self, collection, keyword):
    self.collection = collection
    self.keyword = keyword

    results = collection.aggregate([
      { # search for author keyword. We filter out the other fields from having an impact on this later on
        "$match": {
          "$text": {  # use text indexing to help speed the process up
            "$search": keyword,
            "$language": "none",
            "$caseSensitive": False
          }
        }
      },
      { # extract the authors into their own fields
        "$unwind": {
          "path": "$authors"
        }
      },
      { # ensure the author should match the filter and is not based on the other fields
        "$match": {
          # Allow "firstname KEYWORD lastname" or like "KEYWORD-random lastname" etc etc but not partial matches
          "authors": re.compile(f".*(^| |-){keyword}( |-|\\.|$)", flags=(re.IGNORECASE))
        }
      },
      { # group by authors and count the publications they appear in
        "$group": {
          "_id": "$authors",
          "count": {
            "$sum": 1
          }
        }
      }
    ])

    # Prepare menu data
    authors = []  # stores author names
    displayed_options = []  # displayed text
    for row in results:
      authors.append(row["_id"])
      displayed_options.append(f"{row['_id']} ({row['count']} publications)")

    # store for display_results usage
    self.authors = authors
    self.displayed_options = displayed_options

  def display_results(self):
    # ask for author they want to select
    choice = get_choice(desc=f"Search results for {self.keyword} ({len(self.authors)} in total)", options=self.displayed_options, page_limit=10)

    # If the user wants to go back
    if choice == -1:
      return
    
    # retrieve the author chosen
    author = self.authors[choice]
    
    # find all publications by this author
    results = self.collection.aggregate([
      { # speeds up querying. the match query below ensures that the same publications as the above query are returned.
        "$match": {
          "$text": {  # use text indexing to help speed the process up
            "$search": self.keyword,  # we use the same keyword just in case using the author name gives diff results
            "$language": "none",
            "$caseSensitive": False
          }
        }
      },
      { # all publications should match the author we are looking up specifically.
        "$match": {
          "authors": author
        }
      },
      { # sort in desc by year
        "$sort": {
          "year": -1
        }
      },
      { # return the title, year, and venue. thanks mongodb!!
        "$project": {
          "title": 1,
          "year": 1,
          "venue": 1
        }
      }
    ])
    
    # display result
    displayed_results = []
    for row in results:
      displayed_results.append(f"{row['title']} (Venue: {row['venue']}) (Published {row['year']})")

    # show list.
    show_list(desc=f"Articles published by {author} ({len(displayed_results)} in total)", options=displayed_results, page_limit=10)