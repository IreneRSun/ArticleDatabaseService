from utils import get_collection
from time import time
from pymongo import TEXT
import math
import subprocess
import json

IMPORT_BATCH_SIZE = 10000
IMPORT_WORKERS = 20

VENUE_MATERIALIZED_VIEW_NAME = "venue-materialized-view"

def load_json():
  # Get JSON file
  file = input("Enter JSON file name: ")
  try:
    f = open(file, 'r')
  except FileNotFoundError:
    print("The file "+ file + " does not exist!")
    quit()

  # Get port number
  try:
    port = int(input("Enter port number: "))
  except ValueError:
    print("Invalid input!")
    quit()

  # Acquire MongoDB collection
  try:
    dblp = get_collection("dblp", port)
    materialView = get_collection(VENUE_MATERIALIZED_VIEW_NAME, port)
  except Exception as err:
    print("Connection error!", err)
    quit()
  dblp.drop()
  materialView.drop()

  # # track the start time of how long it takes to finish everything.
  start_time = time()

  importProc = subprocess.Popen(f"mongoimport --collection=dblp --file={file} --port {port} --numInsertionWorkers={IMPORT_WORKERS} --batchSize {IMPORT_BATCH_SIZE} --db 291db", shell=True, stdout=subprocess.PIPE)
  importProc.wait()

  # convert year to string
  dblp.aggregate([
    {
      "$addFields": {
        "year": { "$toString": "$year" }
      }
    },
    {
      "$merge": "dblp"
    }
  ])

  print(f"Finished writing all rows to database in {math.ceil(time() - start_time)}s! Running index creation...")
  
  # # Create the index we need.
  dblp.create_index(
      keys = [
          ("references", TEXT),
          ("title", TEXT),
          ("abstract", TEXT),
          ("venue", TEXT),
          ("authors", TEXT),
          ("year", TEXT),
      ],
      default_language='none'
  )

  seconds_to_add_data = math.ceil(time() - start_time)
  print(f"Finished index creation and row insertion in {seconds_to_add_data}s! Running precomputations...")

  # we need the amount of publications every venue has and also how many references to that venue
  # The gimmick behind this materialized view is that 
  # we first retrieve how many times a venue was used
  # and then we union that with how many times a venue was referenced
  # bypassing the need for the expensive lookup operation.
  dblp.aggregate([
          # FIRST, we need to retrieve how many times a venue was called
    {     # Filter out no venue publications
      "$match": {
        "venue": {"$ne": ""}
      }
    },

    {     # Group by the venue and publication, and also store
          # a count for how many times this venue was used in a publication.
          # we group by both when we are retrieving how many times a venue was referenced by a publication,
          # we will need to have the publication in order to retrieve the venue the publication belongs to.
      "$group": {
        "_id": {
          "venue": "$venue",
          "publication": "$id"
        },
        "venue_count": {
          "$sum": 1
        }
      }
    },    # At this point... we have a list of every unique publication/venue combo.
          # we also have the venue_count property to group later to get how many times a venue was used.

    {     # Now we need to union it with the amount of times a publication was referenced.
      "$unionWith": {
        "coll": "dblp",
        "pipeline": [
          {   # get rid of venues that don't exist 
            "$match": {
              "venue": {"$ne": ""}
            }
          },

          {   # extract the references array so that every reference is it's own document
            "$unwind": {
              "path": "$references"
            }
          },  # at this point we have EVERY publication that has a reference (and non-existing publications)

          {   # Group by the publication referenced so that we can figure out how often a
              # publication was referenced.
            "$group": {
              "_id": "$references",
              "publications_referencing_publication": { # store in an array the publications that
                "$push": "$id"                          # reference this reference for later on.
              },
            }
          },  # we have a list of every publication that is referenced and how often they are referenced.

          {   # modify the output of this union so that the _id shares the $_id.publication as our other
              # calculated dataset we are unionizing this with. (so that we can group it later)
            "$project": {
              "_id": {
                "publication": "$_id"
              },
              "publications_referencing_publication": "$publications_referencing_publication",
            }
          }
        ]
      }
    },  # at this point, we have two different datasets combined filled with structures below...
        # { "_id": { "publication": "...", "venue": "..." }, "venue_count": # } and 
        # { "_id": { "publication": "..." }, "publications_referencing_publication": ["...", ...] }

    {   # However... we need it so that we get the amount of times a venue was referenced...
        # not how many times a publication was referenced.
        # so we group based off of the publication which is shared between the two.
        # we also store the venue to finalize the result...
      "$group": {
        "_id": "$_id.publication",
        "venue_count": {
          "$sum": "$venue_count"
        },
        "publications_referencing_publication": {
          "$first": "$publications_referencing_publication"
        },
        "venue": {
          "$first": "$_id.venue"
        },
      }
    },  # at this point our dataset is filled with the structure below...
    # { "_id": "...", "venue_count": #, "publications_referencing_publication": ["...", ...], "venue": "..." }
    # Where _id is the publication. However, we want to find the amount of times the venue 
    # was referenced and used. NOT the publication.

    { # Before we can do so, we need to filter out any publication that does not exist within the dataset.
      # (some of the referenced publications don't exist in the dataset)
      # (so anything that doesn't have a matched venue should be removed)
      # (no venue implies no publication)
      "$match": {
        "venue": {
          "$ne": None
        }
      }
    },

    { # Finally, we group all the publications by venue instead.
      "$group": {
        "_id": "$venue",
        "venue_count": {
          "$sum": "$venue_count"
        },
        "array_of_publications_referencing_venue": { # create array of array of publications that ref this venue
          "$push": "$publications_referencing_publication"
        }
      }
    },

    { # Convert 2D array to 1D array
      "$set": {
        "publications_referencing_venue": {
          "$reduce": {
            "input": "$array_of_publications_referencing_venue",
            "initialValue": [],
            "in": {
              "$concatArrays": ["$$value", "$$this"]
            }
          }
        }
      }
    },

    { # We need to filter out duplicate publication origins.
      "$unwind": {
        "path": "$publications_referencing_venue"
      }
    },

    { # convert array to set.
      "$group": {
        "_id": "$_id",
        "publications_referencing_venue": {
          "$addToSet": "$publications_referencing_venue"
        },
        "venue_count": { "$first": "$venue_count" }
      }
    },

    { # we now have the venue_references
      "$set": {
        "venue_references": {
          "$size": "$publications_referencing_venue"
        }
      }
    },

    { # Save the results in this materialized view
      "$merge": VENUE_MATERIALIZED_VIEW_NAME
    }
  ])
  
  seconds_to_construct = math.ceil(time() - start_time)
  print(f"Document store constructed and precomputations computed in {seconds_to_construct}s!")
  return port
      
if __name__ == "__main__":
  load_json()
