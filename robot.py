import os
import sys
import requests
import queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlsplit
from threading import Thread


restricted_extensions= ['.pdf','.jpeg','.jpg','.doc','.txt','.rtf','.wpd','.avi','mpg','.wmv','.vob','.flv','.3gp',
                        '.mpg3','.wma','.wav','.mid''.java','.py','.cs','.php','.swift','.vb','.rss','.css','.cer',
                        '.asp','.aspx','.bmp','.tif','.gif','.png']

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
    reserved_characters  = ['&']
    for char in reserved_characters:
        str = str.replace(char,'%26')
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

def getrestricted_domains(seed_nodes):
    
    restricted_domains = []
    
    for node in seed_nodes:
        robots_url = node.url+'/robots.txt'
        result = requests.get(robots_url)
        status_code = result.status_code
        if status_code == 200: # OK
            result = result.text;
            for line in result.split("\n"):
                if line.startswith('Disallow:'):
                    split = line.split(' ', maxsplit=1)
                    domain = split[1].strip()      
                    if  domain not in restricted_domains:
                        restricted_domains.append(line)
        else:
            print("test")
    return restricted_domains

def task():
    print("DONE!")

def getseedsFromFile(filename):
    urls =  open(filename).readlines()
    seed_nodes = []
    for url in urls:
        n1 = Node(url)
        seed_nodes.append(n1)
        
    return seed_nodes

def createDirectory(directory_name):
    exists = os.path.exists(directory_name)
    if  not exists:
        os.makedirs(directory_name)

seed_nodes = getseedsFromFile(sys.argv[1])
max_pages = int(sys.argv[2])
hops = int(sys.argv[3])
output_dir = sys.argv[4]

#create directory
createDirectory(output_dir)

no_threads = 5
page_request_delay = 5000 # set to 1000ms = every second or 60 request a min

restricted_domains = getrestricted_domains(seed_nodes)

#setup the queue/frontier
q = queue.Queue()
visited =[]

#add all the seeds to the queue
for node in seed_nodes:
    pass
    #q.put(node)

found_pages =0
pages_maximum = 1000# just temporary we will use the preset 100000 later

#while queue is not empty
#while not q.empty() and (found_pages < pages_maximum):
   # node = q.get()    
    
    #proceed only if the node we found not visited or 5  nodes deep from  seed nodes
    #if(node.url not in visited and node.depth < 5):
         #add it to visited list /improve this later for checking similarity etc??
       # visited.append(node.url)
        
       # result = requests.get(node.url)
        
       # if(result.status_code == 200): #ok
           
            htmldoc = result.text
            soup = BeautifulSoup(htmldoc,'html.parser')
       
        #get the  links founds in the webpage and add them to queue
            child_nodes = get_children(soup,node,restricted_domains,seed_nodes)
            for child_node in child_nodes:
                q.put(child_node)
        
            #found_pages = found_pages+1
        
           # print("visited: "+ node.url + " depth: " + str(node.depth))
    #newThread = Thread(target=task)
    #newThread.start()