from dotenv import load_dotenv
import wikitextparser as wtp
import requests
import json
import os

load_dotenv()

def search_wikipedia(term, num = 5):
    """
    Searches wikipedia for the given term
    :param term: Term to search on wikipedia
    :param num: Number of pages to search
    :return:Returns a list of 5 pages from wikipedia
    """

    headers = {
        'Authorization': os.getenv('wiki_auth_token')
    }

    paramaters = {
        'q': term,
        'limit':  num
    }

    url  = "https://api.wikimedia.org/core/v1/wikipedia/en/search/page"

    response = requests.get(url, params=paramaters, headers=headers).content
    pages_dirs = json.loads(response)['pages']

    pages = [x['title'] for x in pages_dirs]

    return pages

def get_page(title):
    """
    Returns the page object from wikipedia given a title
     :param title: Title of the page to search on wikipedia
     :return: Page object from wikipedia
     """
    
    headers = {
        'Authorization': os.getenv('wiki_auth_token')
    }

    url  = "https://api.wikimedia.org/core/v1/wikipedia/en/search/page"

    paramaters = {
        'q': title,
        'limit':  1
    }

    response =requests.get(url, params=paramaters, headers=headers).content
    page_key = json.loads(response)['pages'][0]["key"]

    url = " https://api.wikimedia.org/core/v1/wikipedia/en/page/" + page_key
    response = requests.get(url, headers=headers).content
    
    page = json.loads(response)
    return page
    

def create_sections(wikiText:str):
    """
    Extract the sections from wikipedia
      :param wikiText: Text from the wikipedia page
      :ruturn: a list of dictionaries that have section titles and content of the sections
     """
    
    parsed = wtp.parse(wikiText)
    raw_sections = parsed.sections
    sections = []
    
    for section in raw_sections:
        title = section.title
        content = section.contents

        section_dict = {
            "title": title,
            "content": content
        }

        sections.append(section_dict)
    
    return sections
