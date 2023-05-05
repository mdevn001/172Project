import os
import sys
import requests
import queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from threading import Thread


class Node:

        def __init__(self,url):
            self.parent = None
            self.depth = 0;
            self.url =url
            
        def assign_parent(self,parent):
            self.parent = parent;
            self.depth = parent.depth+1;

def get_children(soup,parent):
    
    children = []
    
     #handles relative urls
    for link in soup.find_all('a'):
        child_url = link.get('href')
        abs_url = urljoin(parent.url,child_url)
        child_node= Node(abs_url)
        child_node.assign_parent(parent)
        children.append(child_node) 
        
    return children

def getrestricted_domains(seed_urls):
    
    restricted_domains = []
    
    for url in seed_urls:
        robots_url = url+'/robots.txt'
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
            print("request returned with status code : "+ str(status_code)) # if 404 means file not found no robot.txt
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

#restricted_domains = getrestricted_domains(seed_urls)

#setup the queue/frontier
q = queue.Queue()
visited =[]

#add all the seeds to the queue
for node in seed_nodes:
    q.put(node)

found_pages =0
pages_maximum = 10 # just temporary we will use the preset 100000 later

#while queue is not empty
while not q.empty() and (found_pages < pages_maximum):
    node = q.get()    
    
    #proceed only if the node we found not visited or 5  nodes deep from  seed nodes
    if(node.url not in visited or node.depth < 5):
         #add it to visited list /improve this later for checking similarity etc??
        visited.append(node.url)
        
        htmldoc = requests.get(node.url).text
        soup = BeautifulSoup(htmldoc,'html.parser')
       
        #get the  links founds in the webpage and add them to queue
        child_nodes = get_children(soup,node)
        for child_node in child_nodes:
            q.put(child_node)
        
        found_pages = found_pages+1
        
        print("visited: "+ node.url)
        
    #newThread = Thread(target=task)
    #newThread.start()