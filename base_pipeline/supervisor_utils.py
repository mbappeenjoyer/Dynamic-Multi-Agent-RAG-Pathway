from langchain.prompts import ChatPromptTemplate
import numpy as np

    
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
    print({prompt_str}.format(query=query))
    annotation = chat_llm.invoke({prompt_str}.format(query=query)).content
    print("printing annotion")
    print(annotation)
    pattern = r'```python\\n(.*?)\\n```'
    matches = re.findall(pattern, annotation, re.DOTALL)
    parsed_response = matches[-1] if matches else None
    print("parsed response")
    print(parsed_response)
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        if parsed_response:
            exec(parsed_response)
            print(str(query) + "has been executed succefully." )
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

class AgentCode:
    def __init__(self, content):
        self.content = content