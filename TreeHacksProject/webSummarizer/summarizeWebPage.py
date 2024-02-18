import requests  
import pandas as pd  
from bs4 import BeautifulSoup  
from openai import OpenAI
from dotenv import load_dotenv
import os
import hashlib
  


secret_key = str(os.environ["OPENAI_API_KEY"])



def __getdata(url):  
    """
    Uses BeautifulSoup to extract the text data from webpage

    :param url: The URL of the webpage to extract data from
    :return: The text data from the webpage
    :raises ValueError: If there is no textual data that can be extracted using this method
    """
    r = requests.get(url)  
    soup = BeautifulSoup(r.text, 'html.parser')
    string = ""
    if soup.title is not None:
        string = "Title: "
        string += soup.title.string
    string += " \n Headers \n"
    headers = ["h1", "h2", "h3", "h4", "h5", "h6"]
    for header in headers:
        for data in soup.find_all(header):
            string += data.get_text() + "\n"
    string += "\n Body: \n"
    for data in soup.find_all("p"):
        if len(string.split()) > 600: 
            break
        string += data.get_text()
    return string 

def __wordCap(string, cap):
    """
    Caps the number of words in a string (to lessen token usage)

    :param string: The string to be capped
    :param cap: The number of words to cap the string at
    :return: The capped string
    """
    return " ".join(string.split()[:cap])


def __summarize(webpage_Data):
    """
    Uses OpenAI's GPT-3.5 model to summarize the webpage data and return a summary of the webpage
    
    :param webpage_Data: The data from the webpage to be summarized
    :return: A summary of the webpage data
    :raises ValueError: If the webpage data is too short to summarize
    """
    if len(webpage_Data) < 100:
        return("Summary not available for this page.")
    webpage_Data = __wordCap(webpage_Data, 450)
    data = {
        "model": "gpt-3.5-turbo-0125",  
        "messages": [
            {"role": "system", "content": "You are an assistant tasked with helping elderly people utilize the internet in their daily lives. Your job is to summarize the following webpage and tell the user in a friendly way what they can find on the website so that they can figure out which site is best for what they are looking for. Keep your response under 100 words."},
            {"role": "user", "content": webpage_Data},
        ],
        "max_tokens": 200,  
        "temperature": 0.7  
    }

    
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json"
    }

    endpoint = "https://api.openai.com/v1/chat/completions"
    response = requests.post(endpoint, json=data, headers=headers)

    
    if response.status_code == 200:

        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Summary not available for this page."

def get_summary(link):
    link_hash = hashlib.sha256(link.encode('utf-8')).hexdigest()

    #look for cached copy of search results
    cache_directory = "./TreeHacksProject/webSummarizer/cache/"
    for filename in os.listdir(cache_directory):
        if os.path.isfile(os.path.join(cache_directory, filename)):
            if str(link_hash) == filename[:-4]:
                with open(cache_directory + filename, 'r') as summary:
                    return summary.read()
                
    # cache results
    summary = __summarize(__getdata(link))
    with open(cache_directory + str(link_hash) + ".txt", 'w') as file:
        file.write(summary)
    return summary
