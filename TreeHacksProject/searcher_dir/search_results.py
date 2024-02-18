###########
# SEARCH_RESULTS
# Defines class to store google search results
# A SearchResults object contains a:
# - query string
# - string number of results
# - list of (title, link) tuples
###########

class SearchResults:
    def __init__(self, query, num_results):
        self.query = query
        self.num_results = num_results
        self.results = []

    def add_result(self, title, link):
        self.results.append((title, link))

    def results(self):
        return self.results
    
    def num_results(self):
        return self.num_results
    
    def query(self):
        return self.query

    def display_results(self):
        print(f"Query: {self.query}")
        print(f"Number of Results: {self.num_results}")
        print("Search Results:")
        for title, link in self.results:
            print(f"Title: {title}")
            print(f"Link: {link}\n")