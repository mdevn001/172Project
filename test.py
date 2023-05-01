import requests
import queue
from bs4 import BeautifulSoup
from urllib.parse import urljoin


seed_urls = ['https://quotes.toscrape.com']
q = queue.Queue();
visited =[]

def get_children(soup,parent_url):
    children = []
     
     #handles relative urls
    for link in soup.find_all('a'):
        child_url = link.get('href')
        abs_url = urljoin(parent_url,child_url)
        children.append(abs_url)    
        
    return children
    

#add all the seeds to the queue
for url in seed_urls:
    q.put(url)

#while queue is not empty
while (not q.empty()):
     #get link from queue
     url = q.get()
     if(url not in visited):
         #add it to visited list /improve this later for checking similarity etc??
        visited.append(url)
     
        #convert it to soupable parsable document
        htmldoc = requests.get(url).text
        soup = BeautifulSoup(htmldoc,'html.parser')
     
        #get child links
        children = get_children(soup,url)
          
     #add child links to queue
        for child in children:
            q.put(child)
            pass
    
     #save document 
        file = open('html_docs/'+url.split('/')[-1]+'.html','w')
        file.write(soup.prettify())
        file.close()

