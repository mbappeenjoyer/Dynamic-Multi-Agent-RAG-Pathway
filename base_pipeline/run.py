from dotenv import load_dotenv
from supervisor import SUPERVISOR_AGENT
from default_tools import TOOLS, TOOLS_AUX, TOOL_MAP
from utils import chat_llm
import nltk
nltk.download('punkt_tab')
import os

document_path = input("Please enter the document path: ")
query = input("Please enter your query: ")

supervisor = SUPERVISOR_AGENT(TOOLS, TOOLS_AUX, chat_llm, TOOL_MAP, document_path)
res = supervisor.run(query)

print(res)
