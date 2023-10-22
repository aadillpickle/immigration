from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import os
import pinecone
from dotenv import load_dotenv
load_dotenv()
from langchain.vectorstores import Pinecone
import spacy

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))

pinecone.init(
    api_key=PINECONE_API_KEY,
    environment=PINECONE_ENV
)

nlp = spacy.load('en_core_web_sm')

index_name = "uscis-embeddings"
all_docs = []

def process_chunk(chunk):
    doc = nlp(chunk, disable=["ner", "tagger"])
    return [sent.text for sent in doc.sents]

chunks = []
chunk = ""
with open('data.txt', 'r') as f:
    for line in f:
        if len(chunk) + len(line) < 1000000:  # Adjust as per the limit you want to set
            chunk += line
        else:
            chunks.extend(process_chunk(chunk))
            chunk = line

    # Process the last chunk
    if chunk:
        chunks.extend(process_chunk(chunk))

for text in chunks:
    doc = Document(page_content=text, metadata={})
    all_docs.append(doc)

docsearch = Pinecone.from_documents(all_docs, embeddings_model, index_name=index_name)

# Perform the search
query = "how to immigrate to the usa as a tech entrepreneur?"
docs = docsearch.similarity_search_with_score(query)

for doc, score in docs:
    print(f"Score: {score}")
    print(f"Document: {doc}")
    print()
