###########
# SEARCHER
# Functions to return google search results and metadata from input queries
###########

#imports
import requests
import json
import TreeHacksProject.searcher_dir.search_results as sr
import re
import pickle
import os

#globals
api_key = "AIzaSyBS0PzyXcftLs2DzJ3bHd863l0I6uF_zVo" # google programmable search api key
cx = "e6fa68f5924a84919" # google search engine ID


# helper functions
def __send_request(query):
    """
    Given a search query string, returns a json with search responses and metadata
    """
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    else:
        print(f"Failed to fetch search results. Status code: {response.status_code}")
        return None

def __parse_response(results_dict):
    """
    given a google search json, create a search_results object
    """
    query = results_dict["queries"]["request"][0]["searchTerms"]
    num_results = results_dict["searchInformation"]["totalResults"]

    r = sr.SearchResults(query, num_results)

    for item in results_dict["items"]:
        r.add_result(item["title"], item["link"])
    return r

# public functions
def search(input_query):
    """
    Googles the input query and returns a SearchResults object containing
    results. Caches all searches, and checks the cache before running a google
    search
    """
    query = input_query.lower() #make lowercase
    query = re.sub(r'\s+', "_", query) #replace spaces with underscores

    #look for cached copy of search results
    cache_directory = "./TreeHacksProject/searcher_dir/cache/"
    for filename in os.listdir(cache_directory):
        if os.path.isfile(os.path.join(cache_directory, filename)):
            if query == filename[:-4]:
                with open(cache_directory + filename, 'rb') as results:
                    return pickle.load(results)
    
    #otherwise google and cache
    results = __parse_response(__send_request(input_query))
    filename = cache_directory + query + ".pkl"
    with open(filename, 'wb') as file:
        pickle.dump(results, file, pickle.HIGHEST_PROTOCOL)
    
    return results