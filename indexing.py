import json
from org.apache.lucene.document import Document, Field, TextField, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from java.nio.file import Paths

# Create an in-memory index
index_dir = RAMDirectory()
analyzer = StandardAnalyzer()
config = IndexWriterConfig(analyzer)
writer = IndexWriter(index_dir, config)

# Iterate over the JSON files and extract the required fields
file_path = "ucr_data.json"
for file_name in os.listdir(file_path):
    if file_name.endswith(".json"):
        with open(os.path.join(file_path, file_name), "r") as json_file:
            data = json.load(json_file)

            # Extract title, URL, and body from JSON data
            title = data["title"]
            url = data["url"]
            body = data["body"]

            # Create a PyLucene document
            doc = Document()
            doc.add(StringField("title", title, Field.Store.YES))
            doc.add(StringField("url", url, Field.Store.YES))
            doc.add(TextField("body", body, Field.Store.YES))

            # Add the document to the index
            writer.addDocument(doc)

# Commit and close the index writer
writer.commit()
writer.close()
