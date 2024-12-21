from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
import numpy as np
from rag_agent.utils  import client_table
import os 

    
def generate_agent_description(name, tool_desc, prompt):
    """
    Generate a function description as a string.

    Args:
        name (str): The name of the function.
        tool_desc (str): A description of what the function/tool does.
        prompt (str or ChatPromptTemplate): The prompt used by the function.

    Returns:
        str: A formatted function definition as a string.
    """
    # Ensure the prompt is properly formatted as a string
    if isinstance(prompt, ChatPromptTemplate):
        prompt_str = repr(prompt)  # Serialize ChatPromptTemplate as a string
    else:
        prompt_str = repr(prompt)
    str1 = f"""
def {name}(query):
    '''
    Name: {name}
    Description: {tool_desc}
    Args:
        query (str): The query to be passed to the agent .
                     Example: "Args"

    Returns:
        str: A string response
    '''
    annotation = chat_llm.invoke({prompt_str}.format(query=query)).content
    pattern = r'```python\\n(.*?)\\n```'
    matches = re.findall(pattern, annotation, re.DOTALL)
    parsed_response = matches[-1] if matches else None
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        if parsed_response:
            exec(parsed_response)
            annot = sys.stdout.getvalue()
        else:
            annot = "No valid Python code found in the response."
    except Exception as e:
        annot = traceback.format_exc()
    finally:
        sys.stdout = old_stdout
    return str(annot)
"""
    return str1

def generate_pdf_name(first_two_page_content):
    prompt_text = f"""You are an assistant tasked with generating title for give pdf content. \
    You are provided with the content of first two pages of the pdf content \
    You have to return short , concise title that is relevant to the pdf
    Title should not be long that 3-4 words
    Return only title 
    Pdf Content:{first_two_page_content} 
    Title:"""

    title = client_table.chat.completions.create(
        model="llama-3.1-70b-versatile",  # Specify the model you want to use
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=0.7,         # Control randomness
        top_p=0.9,               # Sampling control for nucleus sampling
        stream=False             # Change to True if you want streaming responses
    )
    return title.choices[0].message.content

class AgentCode:
    def __init__(self, content):
        self.content = content