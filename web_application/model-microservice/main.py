from flask import Flask, jsonify, request
from rag_agent.supervisor import SUPERVISOR_AGENT
from rag_agent.default_tools import TOOLS, TOOLS_AUX, TOOL_MAP
from rag_agent.utils import chat_llm
import nltk
import dill as pickle
import os
from io import BytesIO
import requests
from flask_cors import CORS
import fitz
from copy import deepcopy

# nltk.download('punkt_tab')

class_supervisors = {}
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


@app.route('/<string:id>/<string:chat_id>/query', methods=['POST'])
def query(id, chat_id):
    #POST request with{
    #   'url' : '',
    #   'query' : ''
    # }
    data = request.get_json()
    
    if class_supervisors.get(id, None) == None:
        class_supervisors[id] = []
    
    supervisor = next((obj for obj in class_supervisors[id] if obj.chat_id == chat_id), None)
    
    if supervisor == None:
        supervisor = SUPERVISOR_AGENT(deepcopy(TOOLS), deepcopy(TOOLS_AUX), chat_llm, deepcopy(TOOL_MAP), data["url"], chat_id)
        if class_supervisors.get(id, None) == None:
            class_supervisors[id] = []    
        class_supervisors[id].append(supervisor)
        output = supervisor.run(data["query"])
        
        return jsonify({ "response" : output }) 
    
    
    output = supervisor.run(data["query"], True)
    
    return jsonify({ "response" : output })

@app.route('/<string:id>/<string:chat_id>/get_conversations', methods=['GET'])
def get_conversations(id, chat_id):
    #GET request with{
    #   'url' : ''
    # }
    # data = request.get_json()
    
    if class_supervisors.get(id, None) == None:
        class_supervisors[id] = []
    
    supervisor = next((obj for obj in class_supervisors[id] if obj.chat_id == chat_id), None)

    if supervisor == None : 
        return jsonify({ "conversations" : [] })

    conversations = supervisor.logs
    
    return jsonify({ "conversations" : conversations })

@app.route('/<string:id>/<string:chat_id>/add_tool', methods=['POST'])
def add_tools(id, chat_id):
    #POST request with{
    #   'url' : '',
    #   'query' : '',
    #   'user_code' : ''
    # }
    
    data = request.get_json()
    
    if class_supervisors.get(id, None) == None:
        return jsonify({ "response" : "ID not found" })
    supervisor = next((obj for obj in class_supervisors[id] if obj.chat_id == chat_id), None)
    res = supervisor.add_tool(data["user_code"])
    
    return jsonify(res) 
    
@app.route('/<string:id>/<string:chat_id>/add_tool_desc', methods=['POST'])
def add_tools_desc(id, chat_id):
    #POST request with{
    #   'url' : '',
    #   'user_desc' : '',
    #   'func_name' : '',
    #   'query' : '',
    # }
    data = request.get_json()
    
    if class_supervisors.get(id, None) == None:
        return jsonify({ "response" : "ID not found" , "error" : True})
    
    supervisor = next((obj for obj in class_supervisors[id] if obj.chat_id == chat_id), None)
    
    res = supervisor.add_desc(data["user_desc"], data["func_name"])
    
    if res["error"] != "NAME_INVALID":
        return jsonify({ "response" : "Success" , "error" : False})
    return jsonify({ "response" : res["error"] , "error" : True})
    
@app.route('/<string:id>/<string:chat_id>/clarify_rag', methods=['POST'])
def clarify_rag(id, chat_id):
    #POST request with{
    #   'url' : '',
    #   're_evaluate' : '',
    #   'clarification' : '',
    #   'feedback' : '',
    #   'query' : ''
    # }
    data = request.get_json()
    if class_supervisors.get(id, None) == None:
        return jsonify({ "response" : "ID not found" })
    supervisor = next((obj for obj in class_supervisors[id] if obj.chat_id == chat_id), None)
    
    if data["re_evaluate"] == True:
        output = supervisor.resolve_rag_jargon(data["clarification"], data["feedback"])
        if output["CODE_REFLEXTION_FLAG"] == False:
            return jsonify({"response" : output})
        output = supervisor.run(data["query"])
        return jsonify({ "response" : output }) 
    else : 
        output= supervisor.resolve_rag_flag()
        output = supervisor.run(data["query"])
        return jsonify({ "response" : output })
       
@app.route('/<string:id>/get_history', methods=['GET'])
def get_history(id):
    history = []
    
    if class_supervisors.get(id, None) == None:
        return jsonify({ "history" : history })
    
    for obj in class_supervisors[id]:
        history.append([
                {
                    "chat_id" : obj.chat_id, 
                    "pdf_title" : obj.pdf_title, 
                    "url" : obj.url
                }
            ])
    
    return jsonify({ "history" : history })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)