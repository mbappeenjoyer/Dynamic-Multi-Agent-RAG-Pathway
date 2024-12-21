from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from llama_index.llms.groq import Groq as groq_llama
from llama_index.embeddings.jinaai import JinaEmbedding
from groq import Groq as GroqClient
import unstructured_client
from typing import Optional
from prompt import *

load_dotenv()

supervisor_groq_api = os.getenv("SUPERVISOR_GROQ_API_KEY")
rag_agent_api = os.getenv('RAG_GROQ_API_KEY')
raptor_api = os.getenv('RAPTOR_GROQ_API_KEY')
client_api_key = os.getenv('CLIENT_GROQ_API_KEY')
together_api_key = os.getenv("TOGETHER_API_KEY")
unstructured_api_key = os.getenv("UNSTRUCTURED_API_KEY")
unstructured_api_url = os.getenv("UNSTRUCTURED_API_URL")
jina_api_key = os.getenv("JINAAI_API_KEY")
embed_jina_api_key = os.getenv('EMBED_JINA_API_KEY')

print(unstructured_api_key)

chat_llm = ChatGroq(model="llama-3.1-70b-versatile", api_key = supervisor_groq_api, temperature=0.1,)
chat_llm1 = ChatGroq(model="llama-3.1-70b-versatile", api_key = rag_agent_api)
llm = groq_llama(model="llama3-70b-8192", api_key = raptor_api)
client_table = GroqClient(api_key=client_api_key)

client_unstructured = unstructured_client.UnstructuredClient(
    api_key_auth=unstructured_api_key, server_url=unstructured_api_url,
)

text_embed_model = JinaEmbedding(
    api_key=embed_jina_api_key,
    model="jina-embeddings-v3",
    task="retrieval.passage",
)
query_embed_model = JinaEmbedding(
    api_key=embed_jina_api_key,
    model="jina-embeddings-v3",
    task="retrieval.query",
    dimensions=1024,
)

thought_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful Thought Generating Agent."),
    ("human", THOUGHT_PROMPT),
])

reasoning_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful Reasoning Agent."),
    ("human", REASONING_PROMPT),
])

jargon_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a jargon detecting agent."),
    ("human", JARGON_IDENTIFY_PROMPT)
])

rephrase_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a query rephraser agent."),
    ("human",  REPHRASE_PROMPT)
])

code_agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a function calling agent."),
    ("human", CODE_AGENT_PROMPT),
])

code_reflexion_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a function call reflexion agent."),
    ("human", CODE_REFLEXION_PROMPT),
])

failure_detection_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a callback failure agent."),
    ("human", FAILURE_DETECTION_PROMPT),
])

final_response_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a final response generator."),
    ("human", FINAL_RESPONSE_PROMPT),
])

confidence_score_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an excellent confidence score based critic agent."),
    ("human", CONFIDENCE_SCORE_PROMPT)
])

challenging_cases = ChatPromptTemplate.from_messages([
    ("system", "You are a challenging and edge cases generation agent"),
    ("human", EDGE_CASE_GEN),
])

ranker_instr = ChatPromptTemplate.from_messages([
    ("system", "You are a ranker agent"),
    ("human", RANKING_PROMPT),
])

error_analyser = ChatPromptTemplate.from_messages([
    ("system", "You are a error analysis agent"),
    ("human", ERROR_ANALYSIS),
])

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a final prompt agent"),
    ("human", PROMPT_REFLEXTION),
])

critic_agent_prompt_1 = ChatPromptTemplate.from_messages([
    ("system", "You are a response critic agent."),
    ("human", CRITIC_AGENT_PROMPT_1),
])
critic_agent_prompt_2 = ChatPromptTemplate.from_messages([
    ("system", "You are a response critic agent."),
    ("human", CRITIC_AGENT_PROMPT_2),
])

silent_error_reflexion = ChatPromptTemplate.from_messages([
    ("system", "You are a silent error reflexion agent."),
    ("human", SILENT_ERROR_REFLEXION),
])

class SilentError(Exception):
  """ Error used to define silent errors in API calls. """
  pass

def llm_response_if_memory_hit_found(query: str, chunk: str) -> Optional[str]:
    prompt = f"""You are an expert reasoning agent tasked with answering the query from the given chunk of data.
Follow these guidelines:
1. Directly answer the query using ONLY the information in the provided chunk
2. If the chunk does not contain sufficient information, respond with "INSUFFICIENT_CONTEXT"
3. Be concise and precise in your response

Example:
Query: What is the capital of France?
Chunk: France is a country in Western Europe. Its capital is Paris, known for the Eiffel Tower and rich cultural heritage.
Answer: The capital of France is Paris

Current Query: {query}
Chunk: {chunk}
Answer:"""

    try:
        response = chat_llm.invoke(prompt)

        cleaned_response = response.content.strip()

        if cleaned_response in ["INSUFFICIENT_CONTEXT"]:
            return None

        return cleaned_response

    except Exception as e:
        print(f"Error in LLM response generation: {e}")
        return None