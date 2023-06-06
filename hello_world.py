from simhash import Simhash
import json
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import queue
import threading
import simhash
import requests
import time

restricted_extensions= ['.pdf','.jpeg','.jpg','.doc','.txt','.rtf','.wpd','.avi','mpg','.wmv','.vob','.flv','.3gp',
                        '.mpg3','.wma','.wav','.mid''.java','.py','.cs','.php','.swift','.vb','.rss','.css','.cer',
                        '.asp','.aspx','.bmp','.tif','.gif','.png','.js$','.js','.svg','#']

def extension_valid(string):
    
    for ext in restricted_extensions:  
        if ext in string:
            return False
    return True
   
value = "#test"

if(extension_valid(value)):
    print("YES")
else:
    print ("NO")







