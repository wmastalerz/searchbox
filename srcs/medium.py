import os
import re
import json
import time
import requests
from typing import List
from bs4 import BeautifulSoup
from selenium import webdriver


class Story(object):

    def __init__(self, url: str):
        """ """
        self.url = url
        self.author = ''
        self.length = ''
        self.title = ''
        self.tags = []
        self.content = []

    def _get_title(self, article_element):
        """ Get the title of the story. """
        try:
            self.title = article_element.find('h1').text
        except Exception as e:
            print('Problem getting title:', e)

    def _get_author_length(self, article_element, paragraphs):
        """ Get the author name and length of the story. """
        try:
            length = None
            i = 1
            while length is None and i < len(paragraphs):
                
                if '·' in paragraphs[i].text and paragraphs[i].text.endswith('min read'):
                    length = paragraphs[i].text.split('·')[1]
                else:
                    i += 1

            if length is not None:
                self.length = length
                self.author = paragraphs[i - 1].text
                return i
            
            else:
                
                title_block = article_element.find(lambda tag: '·' in tag.text and \
                                                   tag.text.endswith(' min read'))
                length = ' '.join(title_block.strings).split('·')[1]
                
                self.length = ' '.join(length.split())
                
                self.author = list(title_block.strings)[1]
                return None

        except Exception as e:
            print('Problem getting author and length:', e)
            return None

    def _get_tags(self, soup):
        """ Get tags of the story. """
        pattern = r'\b[A-Z][a-z]*\b'
        try:
            li_element = soup.find_all('li')  
            for li in li_element:
                a_element = li.find_all('a')
                for a in a_element:
                    if ('/tagged/' in a['href'] or '/tag/' in a['href']) and '?' not in a['href']:
                        self.tags.append(a['href'].split('/')[-1])
            if not self.tags:
                matches = re.findall(pattern, soup)
                self.tags = matches[:3]
            if not self.tags:
                self.tags[0] = 'TBD'   
        except Exception as e:
            print('Problem getting tags:', e)

    def _get_content(self, paragraphs):
        """ Get content of the story. """
        try:
            for p in paragraphs:
                self.content.append(p.text)
                
                next_tag = p.next_element
                while next_tag is not None and next_tag.name != 'p':
                    
                    if next_tag.name == 'pre':
                        self.content.append(' '.join(next_tag.stripped_strings))
                    
                    elif next_tag.name == 'ol' or next_tag.name == 'ul':
                        self.content.append(' '.join(next_tag.stripped_strings))

                    next_tag = next_tag.next_element
        except Exception as e:
            print('Problem getting content:', e)

    def scrape(self, chrome: str = None, firefox: str = None):
        """
        Scrape the story to get the title, author name, length, tags
        and content.
        """
        
        driver = init_driver(chrome, firefox)
        
        driver.get(self.url)
        
        try:
            for p in driver.find_elements_by_xpath('//p'):
                time.sleep(0.1)
                driver.execute_script("arguments[0].scrollIntoView();", p)
        except:
            pass

        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        article_element = soup.find('article')
        
        if len(self.tags) == 0:
            self._get_tags(soup)

        
        if not self.title:
            self._get_title(article_element)

        
        if article_element is not None:
            paragraphs = article_element.find_all('p')
        else:
            raise requests.exceptions.HTTPError('Might not be a medium story url.')

        if len(paragraphs) <= 5:
            print(f'Error getting {self.url}')
            raise requests.exceptions.HTTPError('Blocked by the Medium website.')

        
        length_index = self._get_author_length(article_element, paragraphs)

        
        if length_index is not None:
            paragraphs = paragraphs[length_index + 1:]
        elif paragraphs[0].text.startswith('You have 2 free member-only'):
            paragraphs = paragraphs[1:]

        
        if len(self.content) == 0:
            self._get_content(paragraphs)

        
        driver.quit()

    def to_dict(self) -> dict:
        """ Return a dictionary of the contents. """
        return {
            'author': self.author,
            'length': self.length,
            'title': self.title,
            'tags': self.tags,
            'content': self.content
        }

    def to_json(self, json_file: str, load_exist: bool = True):
        """ Save the story into json file. """
        
        if load_exist and os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                loaded = json.load(f)
        else:
            loaded = {}

        loaded[self.url] = self.to_dict()
        with open(json_file, 'w') as f:
            json.dump(loaded, f, indent=4)


def get_lists(url: str, chrome: str = None, firefox: str = None) -> List[str]:
    """ Get urls of all public lists of a medium user. """
    driver = init_driver(chrome, firefox)
    
    username = url.split('/@')[1].split('/')[0]
    
    driver.get(url)
    trial = 0
    
    while len(driver.find_elements_by_tag_name('a')) == 0:
        time.sleep(0.1)
        trial += 1
        if trial == 30:  
            error_mssg = 'Maximum trial has been reached.'
            raise requests.exceptions.ConnectionError(error_mssg)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    lists = soup.find_all('a')
    list_urls = []
    for l in lists:
        
        if f'@{username}/list' in l['href'] and l['href'] not in list_urls:
            list_urls.append(l['href'])

    driver.close()
    
    list_urls = [l if l.startswith('http') else f'https://medium.com{l}' \
                 for l in list_urls]
    return list_urls


def get_story_from_list(list_url: str, waiting_time: int = 3,
                        chrome: str = None, firefox: str = None) -> List[str]:
    """ Get urls of all stories in a public medium list. """
    driver = init_driver(chrome, firefox)
    driver.get(list_url)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(waiting_time)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = soup.find_all('a')
    urls = []
    for link in links:
        if 'Read more' in link.text:
            if not link['href'].startswith('http'):
                urls.append(f'https://medium.com{link["href"].split("?source=")[0]}')
            else:
                urls.append(link['href'].split('?source=')[0])

    return urls


def init_driver(chrome: str, firefox: str):
    """ Init and return a web driver. """
    if chrome is not None:
        options = webdriver.chrome.options.Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(chrome, options=options)
    elif firefox is not None:
        options = webdriver.firefox.options.Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Firefox(firefox, options=options)
    else:
        raise ValueError('Please give either chrome or firefox webdriver path.')

    return driver
