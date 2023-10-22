import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone
import openai
from dotenv import load_dotenv

load_dotenv()

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"), 
    environment=os.getenv("PINECONE_ENV")  
)

embeddings_model = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))

index_name = "uscis-embeddings"

docsearch = Pinecone.from_existing_index(index_name, embeddings_model)

app = Flask(__name__)
CORS(app) 

@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.json
    question = data.get('question')
    if question:
        resp = get_response_from_question(question)
        return jsonify(resp)
    else:
        return jsonify({"error": "Question not provided"}), 400

def get_relevant_info_from_question(query):
    relevant_info = []
    docs = docsearch.similarity_search_with_score(query, k=5)

    for doc in docs:
        relevant_info.append(doc[0].page_content)
    return relevant_info

def get_response_from_question(query, messages=[]):
    relevant_info = get_relevant_info_from_question(query)
    prompt = f"You are an expert on customs and immigration policies in the united states. Your job is to assist people looking to immigrate to the USA to the best of your knowledge. Do not say anything untrue. Do not refer to yourself as an AI or large language model. Here is some relevant info on the prospective immigrants question: {relevant_info} \nProspective Immigrant:{query} \nExpert Response: "
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content":prompt}] + messages
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=PORT, debug=True)
