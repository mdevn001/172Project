import os
import sys
import requests
import queue
import copy
from simhash import Simhash
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlsplit
from threading import Thread
from multiprocessing import Pool, Value
import time


restricted_extensions= ['.pdf','.jpeg','.jpg','.doc','.txt','.rtf','.wpd','.avi','mpg','.wmv','.vob','.flv','.3gp',
                        '.mpg3','.wma','.wav','.mid''.java','.py','.cs','.php','.swift','.vb','.rss','.css','.cer',
                        '.asp','.aspx','.bmp','.tif','.gif','.png','.js$','.js','.svg']

def extension_valid(string):
    
    for ext in restricted_extensions:  
        if ext in string:
            return False
    return True
    

class Node:

        def __init__(self,url):
            self.parent = None
            self.depth = 0;
            self.url =url
            
        def assign_parent(self,parent):
            self.parent = parent;
            self.depth = parent.depth+1;

def can_get_page(url,restricted_domains,base_seeds):
    result = urlsplit(url)  
    #we are not linking into restricted domains from robot.txt
    for path in restricted_domains:
        if(path in url):
            return False
        
     #check if we are in the base domains we specified in the seed_txt
    seed_hosts = []
    for node in base_seeds:
      res = urlsplit(node.url)
      seed_hosts.append(res.hostname)
    
    if(result.hostname in seed_hosts):
        return True
    else:
        return False
    
      
def get_children(soup,parent,restricted_domains,base_seeds):
    
    children = []
    
    for link in soup.find_all('a'):      
        child_url = link.get('href')
        
        result = urlsplit(child_url)
        #we got here a relative url /something/something/resource
        
        if result.hostname == None:
            child_url = urljoin(parent.url,child_url)
            
        if valid_url(child_url):
            cleaned_url = clean_url(child_url)
            if can_get_page(cleaned_url,restricted_domains,base_seeds):
                child_node= Node(cleaned_url)
                child_node.assign_parent(parent)
                children.append(child_node)
        
    return children



# simple function for encoding ambersand can include more characters later
def encode_reserved(str):
    reserved_characters  = ['&',' ']
    for char in reserved_characters:
        if(char == '&'):
            str = str.replace(char,'%26')
        else:
            if(char ==' '):
                str =  str.replace(char,'%20')
    return str

#start stripping out the url so we can only get html
def clean_url(url):
    url = url.strip()
    url = encode_reserved(url)
    result = urlsplit(url)
    return url


#validate whether the url falls within ther requirements
def valid_url(child_url):
    
    result = urlsplit(child_url)
    # we only want http and maybe https links         
    if result.scheme == "http" or result.scheme == "https":
        if result.netloc != None:
            if extension_valid(result.path):
                return True
    return False

def getrestricted_domains(seeds):
    
    restricted_domains = []
    seeds_cpy =  copy.deepcopy(seeds)
    
    for seed in seeds_cpy:
        robots_url = urljoin(seed,'/robots.txt')
        result = requests.get(robots_url)
        status_code = result.status_code
        if status_code == 200: # OK
            result = result.text
            for line in result.split("\n"):
                if line.startswith('Disallow:'):
                    split = line.split(' ', maxsplit=1)
                    domain = split[1].strip()
                    domain = domain.replace('*','') # some robots use * to dictate any
                    if  domain not in restricted_domains:
                        restricted_domains.append(line)
                        
                    #adds any relative paths to our seeds
                if line.startswith('Allow:'):
                    split = line.split(' ', maxsplit=1)
                    domain = split[1].strip()
                    domain = domain.replace('*','') # some robots use * to dictate any
                    crawlable_url = urljoin(seed,domain)
                    if(crawlable_url not in seeds and domain  != '/' and extension_valid(crawlable_url)):
                        print("added: "+ crawlable_url+ " to list of crawlable paths.")
                        seeds.append(crawlable_url)
    return restricted_domains

def getseedsFromFile(filename):
    urls =  open(filename).readlines()
    seeds = []
    for url in urls:
        seeds.append(url)
    return seeds

def createDirectory(directory_name):
    exists = os.path.exists(directory_name)
    if  not exists:
        os.makedirs(directory_name)

max_pages = int(sys.argv[2])
hops = int(sys.argv[3])
output_dir = sys.argv[4]

#create directory
createDirectory(output_dir)

page_request_delay = 1 # every 20 seconds send 5 requests or 15 requests a min

seeds = getseedsFromFile(sys.argv[1])
seed_nodes = []

restricted_domains = getrestricted_domains(seeds)

for seed in seeds:
    seed = seed.strip()
    n1 = Node(seed)
    seed_nodes.append(n1)

#setup the queue/frontier
q = queue.Queue()
visited =[]
hashes = [] #hashed documents for comparing similiarity


#add all the seeds to the queue
for node in seed_nodes:
    q.put(node)

def save_html_page(soup,output_dir):
    result = urlsplit(node.url)
    filename =result.hostname+result.path
    filename =output_dir+'/'+filename.replace('/','_')+".html"
    file = open(filename,'w+',encoding='utf-8')
    file.write(str(soup))
    file.close()
 
downloaded_pages = 0  
max_pages = 10000

while (not q.empty() and downloaded_pages < max_pages):
    node = q.get()   
     #proceed only if the node we found not visited or 5  nodes deep from  seed nodes
    if(node.url not in visited and node.depth < hops):
         #add it to visited list /improve this later for checking similarity etc??
        visited.append(node.url)
        result = requests.get(node.url)
        
        if(result.status_code == 200): #ok
           
            htmldoc = result.text
            soup = BeautifulSoup(htmldoc,'html.parser')
       
        #get the  links founds in the webpage and add them to queue
            child_nodes = get_children(soup,node,restricted_domains,seed_nodes)
            for child_node in child_nodes:
                q.put(child_node)
        
            save_html_page(soup,output_dir)
            downloaded_pages = downloaded_pages +1
            print("visited: "+ node.url + " depth: " + str(node.depth))
            time.sleep(page_request_delay)

if q.empty():
    print("finished all links crawled in queue.")
else:
     if(downloaded_pages>=max_pages):
         print("we have hit the document download limit : " + max_pages +"pages")