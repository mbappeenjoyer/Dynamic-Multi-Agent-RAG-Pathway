import re
from langchain.prompts import ChatPromptTemplate
from rag_agent.supervisor_utils import  generate_agent_description, AgentCode, generate_pdf_name
from rag_agent.utils import *
from rag_agent.autoprompt import autoprompt
from copy import deepcopy
from llama_index.core.query_engine import RetrieverQueryEngine
import inspect
from llama_index.core.memory import VectorMemory
from llama_index.core.llms import ChatMessage
import traceback
from rag_agent.ragagent import RAGAGENT
from rag_agent.retriever import jina_retriever, raptor_retriever
from llama_index.embeddings.jinaai import JinaEmbedding
import sys
import re
from rag_agent.autoprompt import ToolError
import requests
import fitz
from io import BytesIO
from io import StringIO



out = sys.stdout

class SUPERVISOR_AGENT:
    """
    Resolve queries using provided tools, their descriptions, a PDF file path, and a user query. 

    Additionally, this function allows the user to ask follow-up questions.  
    The supervisor agent can handle errors during code execution by utilizing mechanisms such as `api_reflection`, `code_reflection`, and `silent_reflection`.
    """
    
    def __init__(self, tools, tools_aux, llm, tool_map, url, chat_id, rag_llm = chat_llm1 , reflextion_limit = 3, top_k = 5, max_steps = 10, raptor = True):
    
        self.tools = tools
        self.llm = llm
        self.raptor = raptor
        self.reflexion_limit = reflextion_limit
        self.tool_map = tool_map
        self.tools_aux = tools_aux
        self.url = url
        self.top_k = top_k
        self.scratchpad = ""
        self.responses = []
        self.query = ""
        self.chat_id = chat_id
        self.error_message = None
        self.error_agent_code = None
        self.api_reflextion_flag = False
        self.rag_response = False
        
        response = requests.get(self.url)
        response.raise_for_status()
        self.pdf_content = response.content
        pdf_content_fitz = fitz.open(stream=BytesIO(response.content), filetype="pdf")
        
        first_two_page_content = pdf_content_fitz[0].get_text()
        if len(pdf_content_fitz) >= 2:
          first_two_page_content = first_two_page_content + pdf_content_fitz[1].get_text()
        self.pdf_title = generate_pdf_name(first_two_page_content)
        
        self.agent = RAGAGENT(llm=rag_llm, embedding_dim=1024, thought_agent_prompt=thought_agent_prompt, reasoning_agent_prompt=reasoning_agent_prompt, max_steps=max_steps, url = self.url, pdf_content = self.pdf_content, raptor = self.raptor)
        self.logs = []
        self.vector_memory = VectorMemory.from_defaults(vector_store=None,
          embed_model=JinaEmbedding(api_key=os.getenv('JINAAI_API_KEY'), model="jina-embeddings-v3", task="retrieval.passage",),
          retriever_kwargs={"similarity_top_k": 2},)

    def run(self, query,  is_follow_up_question = False):
      """
      Generate an answer to the given query based on the query itself and previous responses. Additionally, ask for follow-up question.

      Args:
          query (str): The question asked by the user.
          follow_up_response (list, optional): A list of previous responses for context. Defaults to None.

      Returns:
          str: The answer to the query.
      """
      self.query = query
      
      if is_follow_up_question is False and self.api_reflextion_flag is False and self.rag_response is False:
          if self.raptor:
            retriever_agent = raptor_retriever(self.pdf_content, query, self.top_k)
          else :
            retriever_agent = jina_retriever(self.pdf_content, query, self.top_k)
          self.agent.engine = RetrieverQueryEngine.from_args(retriever_agent, llm=llm)
          self.agent.retriever = retriever_agent
      
      elif is_follow_up_question :
          facts = self.vector_memory.get(query)
          for i in range(len(facts)):
            self.responses.append(facts[i].content)
          self.scratchpad = f"Information :- {self.responses}"
       
      if self.api_reflextion_flag is False:
        self.curr_tools = deepcopy(self.tools)
        self.curr_tools_aux = deepcopy(self.tools_aux)
       
      if self.api_reflextion_flag == True and self.error_message != None:
        self.api_reflextion_flag = False
        error_message = self.error_message
        self.error_message = None
        error_agent_code = self.error_agent_code
        self.error_agent_code = None
        agent_code, func_response = self.code_reflexion(error_agent_code, error_message)
        
        if agent_code == "AGAIN BUILD" and func_response == None:
            pass   
        elif func_response == None:
          self.api_reflextion_flag = True
          return {"API_REFLEXTION_FLAG" : True,  "RAG_FLAG" : False, "Final_Answer" : agent_code.content, "Suggestions":None}
        
        elif self.rag_response == True :
          self.error_agent_code = agent_code
          return {"API_REFLEXTION_FLAG" : False , "RAG_FLAG" : True, "Final_Answer" : [agent_code.content, func_response], "Suggestions" : None}
        
        elif func_response == "API_REFLEXTION_FLAG" and self.api_reflextion_flag:
            return {"API_REFLEXTION_FLAG" : True,  "RAG_FLAG" : False, "Final_Answer" : agent_code.content, "Suggestions":None}
        
        elif agent_code == None and func_response == None:
            self.scratchpad = ""
            self.responses = []
            self.api_reflextion_flag = False
            return {"API_REFLEXTION_FLAG" : False,  "RAG_FLAG" : False, "Final_Answer" : None, "Suggestions":None}
        
        self.responses.append(func_response)
        self.scratchpad += '\n' + "Tool Call : " + str(agent_code.content) + "," + " Response : " + str(func_response)
                
      if self.rag_response == True and self.error_message != None:
        self.rag_response = False
        error_agent_code = self.error_agent_code
        self.error_agent_code = None
        error_message = self.error_message
        self.error_message = None
        agent_code, func_response = self.code_reflexion(error_agent_code, error_message)
        
        if agent_code == "AGAIN BUILD" and func_response == None:
            pass   
        elif func_response == None:
          self.api_reflextion_flag = True
          return {"API_REFLEXTION_FLAG" : True,  "RAG_FLAG" : False, "Final_Answer" : agent_code.content, "Suggestions":None}
        
        elif self.rag_response == True :
          self.error_agent_code = agent_code
          return {"API_REFLEXTION_FLAG" : False , "RAG_FLAG" : True, "Final_Answer" : [agent_code.content, func_response], "Suggestions" : None}
        
        elif func_response == "API_REFLEXTION_FLAG" and self.api_reflextion_flag:
            return {"API_REFLEXTION_FLAG" : True,  "RAG_FLAG" : False, "Final_Answer" : agent_code.content, "Suggestions":None}
        
        elif agent_code == None and func_response == None:
            self.scratchpad = ""
            self.responses = []
            self.api_reflextion_flag = False
            return {"API_REFLEXTION_FLAG" : False,  "RAG_FLAG" : False, "Final_Answer" : None, "Suggestions":None}
        
        self.responses.append(func_response)
        self.scratchpad += '\n' + "Tool Call : " + str(agent_code.content) + "," + " Response : " + str(func_response)
        
      self.api_reflextion_flag = False
      self.rag_response = False
      
      
      while (is_follow_up_question or self.responses == [] or self.responses[-1] != "end" ):
          is_follow_up_question = False
          agent_code, func_response = self.build_code()
          
          if agent_code == "AGAIN BUILD" and func_response == None:
            continue
          
          if self.rag_response == True :
            self.error_agent_code = agent_code
            return {"API_REFLEXTION_FLAG" : False , "RAG_FLAG" : True, "Final_Answer" : [agent_code.content, func_response], "Suggestions" : None}
             
          if func_response == "API_REFLEXTION_FLAG" and self.api_reflextion_flag:
            return {"API_REFLEXTION_FLAG" : True,  "RAG_FLAG" : False, "Final_Answer" : agent_code.content, "Suggestions":None}
          
          if agent_code == None and func_response == None:
            self.scratchpad = ""
            self.responses = []
            return {"API_REFLEXTION_FLAG" : False,  "RAG_FLAG" : False, "Final_Answer" : None, "Suggestions":None}
          
          self.responses.append(func_response)
          self.scratchpad += '\n' + "Tool Call : " + str(agent_code.content) + "," + " Response : " + str(func_response)

      final_response = self.llm.invoke(final_response_prompt.format_messages(query = self.query, code = self.scratchpad, responses = self.responses))
      self.vector_memory.put(ChatMessage.from_str(final_response.content, "user"))
      self.logs.append([self.query, final_response.content])
      
      self.scratchpad = ""
      self.responses = []
      return {"API_REFLEXTION_FLAG" : False, "RAG_FLAG" : False , "Final_Answer" : final_response.content, "Suggestions" : self.agent.get_random_questions_from_metadata()}

    def resolve_rag_jargon(self, clarification, feedback):
      agent_code = self.error_agent_code
      self.agent.clarification = clarification
      self.agent.reavaluate = True
      self.agent.feedback = feedback
      try:
        func_response, jargon, agent = self.tool_map["rag_agent"](*[self.agent.question, self.agent])
        self.agent = agent
        return  {"Final_Answer" : [agent_code.content, {"func_response" : func_response, "jargon" : jargon}], 'RAG_FLAG': True, "Suggestions" : None,  "CODE_REFLEXTION_FLAG" : False, "API_REFLEXTION_FLAG" : False}
      except Exception as e:
        error_message = traceback.format_exc()
        self.error_message = error_message
        return {"Final_Answer" : [agent_code.content, error_message], "CODE_REFLEXTION_FLAG" : True, 'RAG_FLAG': False, "API_REFLEXTION_FLAG" : False}
      
    def resolve_rag_flag(self):
      func_response = self.agent.answer
      agent_code = self.error_agent_code
      func_name, args_list = eval(agent_code.content)[0], eval(agent_code.content)[1]
      
      pos = self.curr_tools_aux.index(func_name)
      func_desc = self.curr_tools[pos]
      try :
        tool_call_reason = eval(agent_code.content)[2]
      except :
        tool_call_reason = "Reason is not Provided"
        
      critics = self.critic_agent(f'''{{"tool_name" : "rag_agent, "argument" : {args_list} , "reason" : {tool_call_reason}}}''',  func_desc,  func_response, self.scratchpad)

      if(eval(critics.content)["score"] == 1):

        self.remove_tool(agent_code)
        return {"response" : "Success", "FAULTY_API_FLAG" : True}
      
      self.responses.append(func_response)
      self.scratchpad += '\n' + "Tool Call : " + str(agent_code.content) + "," + " Response : " + str(func_response)
      return {"response" : func_response , "FAULTY_API_FLAG" : False} 
    
    def api_reflexion(self, agent_code):
      """
      Perform two tasks related to tool management:
      1. Create a new tool if no suitable tool is available to resolve a subtask of the query.
      2. Remove a tool if the response of the last tool call is incorrect and provide the response of the updated code after removal.

      Args:
          agent_code (list[str]): The faulty tool call, represented as a list containing:
                                  ["tool_name", [arguments], "Reasoning"].

      Returns:
          tuple:
              list[str]: The modified tool call after addressing the issue of Faulty Tool Call or No Tool .
              str: The response generated after modifying or removing the tool.
      """


      if(agent_code.content == "NONE" or self.curr_tools==[]):
        # return list of [response, bool] or [response]
        while True:
          # if 
          user_input = input("Would you like to provide Python code with args in the docstring? (yes/no): ").strip().lower()
          if user_input == "yes":
              user_code = input("Enter your Python code:\n")
              try:
                  function_name = re.search(r"def (\w+)\(", user_code).group(1)
                  if function_name in self.tool_map.keys():
                    continue
                  exec(user_code, globals())
                  sys.stdout = out

                  func = globals()[function_name]
                  if func.__doc__ == None:
                    continue

                  doc = f"{func.__doc__} + This function takes the {len(list(inspect.signature(func).parameters.keys()))} arguments :  {str(list(inspect.signature(func).parameters.keys()))}"

                  self.tool_map[function_name] = func
                  self.tools.append(doc)
                  self.tools_aux.append(function_name)

                  self.curr_tools.append(doc)
                  self.curr_tools_aux.append(function_name)

                  agent_code, func_response = self.build_code()
                  return agent_code, func_response

              except Exception as e:
                 pass
          elif user_input == "no":

            user_desc = input("Enter the precise description of the tool needed for the task.")
            tool_name = input("Also select a name for this tool (suggest cool names please) : ")
            while tool_name in self.tool_map.keys():
              tool_name = input("Select a new name for this tool (suggest cool names please) : ")
            prompt = autoprompt(user_desc, 1)
            sys.stdout = out
            pmt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", prompt)
            ])

            a = generate_agent_description(tool_name, user_desc, prompt)

            exec(a, globals())
            function_name = tool_name

            new_func = globals()[function_name]
            new_docs = new_func.__doc__
            sys.stdout = out
            new_docs = f"{new_func.__doc__} + This function takes the {len(list(inspect.signature(new_func).parameters.keys()))} arguments :  {str(list(inspect.signature(new_func).parameters.keys()))}"
            self.tools.append(new_docs)
            self.tools_aux.append(function_name)

            self.curr_tools.append(new_docs)
            self.curr_tools_aux.append(function_name)
            self.tool_map[function_name] = new_func

            agent_code, func_response = self.build_code()
            sys.stdout = out
            return agent_code, func_response
          else:
              continue
      else:
            func_name = eval(agent_code.content)[0]
            pos = self.curr_tools_aux.index(func_name)
            self.curr_tools_aux.remove(func_name)
            self.curr_tools.pop(pos)
            agent_code, func_response = self.build_code()
            return agent_code, func_response

    def code_reflexion(self, agent_code, error):
      '''
      Resolve the python error occured during execution of tool in build_code function
      
      Args : 
        agent_code(list[str]) : Last Tool Call
        error(str) : error occured during execution of tool call in build_code function
      
      Return :
        list[str] : Modified tool call
        str : Response of modified tool call
      '''
      
      count = 0
      agent_code = agent_code
      error = error

      while count < self.reflexion_limit:
          too = [{self.curr_tools[i] : self.curr_tools_aux[i]} for i in range(len(self.curr_tools))]
          agent_code = self.llm.invoke(code_reflexion_prompt.format_messages(query = self.query, error= error, tools = too, agent_code = agent_code))
          try:
              if agent_code.content is None or agent_code.content.lower() == "none" or eval(agent_code.content)[0].lower() == "none":
                agent_code.content = "NONE"
                self.api_reflextion_flag = True
                return agent_code, "API_REFLEXTION_FLAG"
              func_name, args_list = eval(agent_code.content)[0], eval(agent_code.content)[1]
              
              try :
                tool_call_reason = eval(agent_code.content)[2]
              except :
                tool_call_reason = "Reason is not Provided"

              if func_name not in self.curr_tools_aux:
                  raise ToolError(f"Incorrect tool '{func_name}' is called. It is not in the tool list. Try a different one.")

              pos = self.curr_tools_aux.index(func_name)
              func_desc = self.curr_tools[pos]

              critics = self.critic_agent(f'''{{"tool_name" : {func_name}, "args" : {args_list} , "reason" : {tool_call_reason}}}''',  func_desc , None, self.scratchpad)

              if(eval(critics.content)["score"] == 1):
                agent_code = self.silent_reflexion(agent_code.content, reason = eval(critics.content)["reasoning"])
                func_name, args_list = eval(agent_code.content)[0], eval(agent_code.content)[1]

              if func_name == 'rag_agent':
                query = args_list
                if self.agent.cache_index.process_pending_additions():
                  pass
                if query:
                    if self.agent.check_query_in_memory(query):
                        chunk = self.agent.check_memory_and_retrieve_for_supervisor(query)
                        func_response = llm_response_if_memory_hit_found(query, chunk)
                        agent_code = AgentCode(content="rag__agent")
                    else:
                        func_response, jargon, agent = self.tool_map[func_name](*[args_list, self.agent])
                        self.agent = agent
                        self.rag_response = True
                        return agent_code, {"func_response" : func_response, "jargon" : jargon}
              else:
                func_response = self.tool_map[func_name](*args_list)
              critics = self.critic_agent(f'''{{"tool_name" : {func_name}, "arguments" : {args_list} , "reason" : {tool_call_reason}}}''',  func_desc, func_response, self.scratchpad)

              if(eval(critics.content)["score"] == 1):
                self.remove_tool(agent_code)
                return "AGAIN BUILD", None
              return agent_code, func_response
            
          except Exception as e:
              sys.stdout = out
              error = traceback.format_exc()
              failure = self.detect_failure(agent_code, error)
              if eval(failure) == 1:
                  return agent_code, None
              else:
                  count += 1
      return None, None
    
    def build_code(self, agentcode = None):
      '''
        It return the tool called and its responses 
        
        Return :
          list[str] :- Tool Called
          str :- Response of tool
      '''
      tool_dict = [{self.curr_tools[i] : self.curr_tools_aux[i]} for i in range(len(self.curr_tools))]
      if agentcode == None :
        agent_code = self.llm.invoke(code_agent_prompt.format_messages(query = self.query, tools = tool_dict, scratchpad = self.scratchpad, responses = self.responses))
      else :
        agent_code = agentcode

      if agent_code.content.lower() == "end_tool" or eval(agent_code.content)[0].lower() == "end_tool":
          return agent_code, "end"
      try:
        if agent_code.content is None or agent_code.content.lower() == "none" or eval(agent_code.content)[0].lower() == "none":
          agent_code.content = "NONE"
          self.api_reflextion_flag = True
          return agent_code, "API_REFLEXTION_FLAG"

        func_name, args_list = eval(agent_code.content)[0], eval(agent_code.content)[1]
        
        try :
          tool_call_reason = eval(agent_code.content)[2]
        except :
          tool_call_reason = "Reason is not Provided"

        if func_name not in self.curr_tools_aux:
            raise ToolError(f"Incorrect tool '{func_name}' is called. It is not in the tool list. Try a different one.")

        pos = self.curr_tools_aux.index(func_name)
        func_desc = self.curr_tools[pos]

        critics = self.critic_agent(f'''{{"tool_name" : {func_name}, "argument" : {args_list} , "reason" : {tool_call_reason}}}''',  func_desc, None, self.scratchpad)

        if(eval(critics.content)["score"] == 1):
          agent_code = self.silent_reflexion(agent_code.content, reason = eval(critics.content)["reasoning"])
          func_name, args_list = eval(agent_code.content)[0], eval(agent_code.content)[1]

        if func_name == 'rag_agent':
            query = args_list
            if self.agent.cache_index.process_pending_additions():
              pass
            if query:
                if self.agent.check_query_in_memory(query):
                    chunk = self.agent.check_memory_and_retrieve_for_supervisor(query)
                    func_response = llm_response_if_memory_hit_found(query, chunk)
                    agent_code = AgentCode(content="rag__agent")
                else:
                    func_response, jargon, agent = self.tool_map[func_name](*[args_list, self.agent])
                    self.agent = agent
                    self.rag_response = True
                    return agent_code, {"func_response" : func_response, "jargon" : jargon}
        else:
          func_response = self.tool_map[func_name](*args_list)
          

        critics = self.critic_agent(f'''{{"tool_name" : {func_name}, "argument" : {args_list} , "reason" : {tool_call_reason}}}''',  func_desc,  func_response, self.scratchpad)
        if(eval(critics.content)["score"] == 1):
          self.remove_tool(agent_code)
          return "AGAIN BUILD", None

      except Exception as e:
          sys.stdout = out
          error_message = traceback.format_exc()
          failure = self.detect_failure(agent_code.content, error_message)
          a = eval(failure)
          if a == 1:
            self.remove_tool(agent_code)
            agent_code, func_response = self.build_code()
            return agent_code, func_response
          else:
            agent_code, func_response = self.code_reflexion(agent_code, e)
            if agent_code != None and func_response == None:
              if agent_code.content == "NONE" :
                self.api_reflextion_flag = True
                return agent_code, "API_REFLEXTION_FLAG"
              else :
                self.remove_tool(agent_code)
                agent_code, func_response = self.build_code()
                return agent_code, func_response
            elif agent_code == None and func_response == None:
              return agent_code, func_response
              

      return agent_code, str(func_response)
    
    def remove_tool(self, agent_code):
      func_name = eval(agent_code.content)[0]
      pos = self.curr_tools_aux.index(func_name)
      self.curr_tools_aux.remove(func_name)
      self.curr_tools.pop(pos)

    def detect_failure(self, agent_code, callback):
      """
      Detect the type of error in the tool call.

      Args:
          agent_code (list[str]): The tool call causing the error, represented as a list containing:
                                  ["tool_name", [arguments], "Reasoning"].
          callback (str): The error encountered during the execution of the tool call.

      Returns:
          str: "1" if the error is identified as significant, or "0" otherwise.
      """
      detection = self.llm.invoke(failure_detection_prompt.format_messages(agent_code = agent_code, traceback = callback, tools = self.curr_tools, descs = self.curr_tools_aux))
      return detection.content

    def critic_agent(self, agent_code,  desc, func_response, scratchpad):
      """
      Detect two potential issues in a tool call:
        1. Whether the arguments passed to the tool call are valid.
        2. Whether the response of the tool call aligns with the question asked.

      Args:
          agent_code (list[str]): The current tool call, represented as a list containing the tool name, arguments, and reasoning.
          desc (str): A description of the tool call's purpose or expected behavior.
          func_response (str): The response returned by the tool call.
          scratchpad (str): The history of previous tool calls, providing context.

      Returns:
          list: A list containing:
              - int: 0 if the tool call is correct, or 1 if the arguments are invalid or the response does not align with the query.
              - str: Reasoning explaining the result.
              Example: [0/1, "Reasoning"]
      """
      
      if func_response == None:
        response = self.llm.invoke(critic_agent_prompt_1.format_messages(query = self.query, code_last = agent_code, desc = desc, scratchpad = scratchpad))
      else :
        response = self.llm.invoke(critic_agent_prompt_2.format_messages(query = self.query, code_last = agent_code, response = func_response, desc = desc))
      return response
    
    def add_desc(self, user_desc, tool_name):
      if tool_name in self.tool_map.keys():
        return {"response" : "NAME_VALID", "error" : True}
      
      try :
        prompt = autoprompt(user_desc, 1)
        sys.stdout = out

        a = generate_agent_description(tool_name, user_desc, prompt)

        exec(a, globals())
        function_name = tool_name

        new_func = globals()[function_name]
      
      except Exception as e:
        sys.stdout = out
        error_message = traceback.format_exc()
        self.error_message = error_message
        return {"response" : "CODE_REFLEXTION", "error" : error_message}
      new_docs = new_func.__doc__
      sys.stdout = out
      new_docs = f"{new_func.__doc__} + This function takes the {len(list(inspect.signature(new_func).parameters.keys()))} arguments :  {str(list(inspect.signature(new_func).parameters.keys()))}"
      self.tools.append(new_docs)
      self.tools_aux.append(function_name)

      self.curr_tools.append(new_docs)
      self.curr_tools_aux.append(function_name)
      self.tool_map[function_name] = new_func
      
      return {"response " : "Success", "error" : False}
      
    def add_tool(self, user_code):
      function_name = re.search(r"def (\w+)\(", user_code).group(1)
      if function_name in self.tool_map.keys():
        return {"response" : "NAME_INVALID", "error" : False}
      exec(user_code, globals())
      sys.stdout = out

      func = globals()[function_name]
      if func.__doc__ == None:
        return {"response" : "DOC_INVALID", "error" : True}

      doc = f"{func.__doc__} + This function takes the {len(list(inspect.signature(func).parameters.keys()))} arguments :  {str(list(inspect.signature(func).parameters.keys()))}"

      self.tool_map[function_name] = func
      self.tools.append(doc)
      self.tools_aux.append(function_name)

      self.curr_tools.append(doc)
      self.curr_tools_aux.append(function_name)
      
      return {"response" : "Success", "error" : False}
    
    def silent_reflexion(self, code, reason):
      '''
      Resolves errors in the arguments of the tool call , if arguments are deemed invalid by the critic agent.
      
      Args:
          code (str): The current tool call containing potentially invalid arguments.

      Returns:
          list[str]: A corrected tool call with valid arguments, structured as:
                    ["tool_name", [args], "Reasoning"].
      '''
      response = self.llm.invoke(silent_error_reflexion.format(call = code, query = self.query, scratchpad = self.scratchpad, reason = reason))
      return response
    