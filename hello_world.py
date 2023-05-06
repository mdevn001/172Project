from simhash import Simhash
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

import simhash
import requests

reserved_characters  = ['!''#''$''&'"'"'('')''*''+'','"/"':'';''=''?''@''['']']

non_parsable_files = ['.pdf']

def encode_reserved(str):
    reserved_characters  = ['&']
    for char in reserved_characters:
        str = str.replace(char,'%26')
    return str


restricted_extensions= ['.pdf','.jpeg','.jpg','.doc','.txt','.rtf','.wpd','.avi','mpg','.wmv','.vob','.flv','.3gp',
                        '.mpg3','.wma','.wav','.mid''.java','.py','.cs','.php','.swift','.vb','.rss','.css','.cer',
                        '.asp','.aspx','.bmp','.tif','.gif','.png']
b ="https://quotes.toscrape.com"
a= "https://www.goodreads.com/quotes"




def exetension_valid(s):
    for ext in restricted_extensions:
        if ext in string:
            return True
    return False
    


#html_doc = requests.get(string).text
#soup = BeautifulSoup(html_doc,'html.parser')

#print(soup.getText())
    
    
    