import sys
from io import StringIO
import sys
from utils import chat_llm
import re
import subprocess
import traceback
from prompt import RANKING_PROMPT, EDGE_CASE_GEN, ERROR_ANALYSIS, PROMPT_REFLEXTION, PROMPT_GENERATION_PROMPT, META_PROMPT, META_PROMPT_PART_2

history = []
error_analysis=[]


class ModuleInstallError(Exception):
  """Custom exception for module installation issues."""
  pass

class ToolError(Exception):
  """Custom exception for incorrect tool calling issue"""
  pass


def identify_challenging_examples(task_description, input_prompt):
  '''
  Generate challenging examples for given task_description using LLM
  
  Args :- 
    task_description(str, required) : 
  
  Return :-
    list : List of all challenging examples
  '''
  prmpt = EDGE_CASE_GEN.format(task_description = task_description, instruction = input_prompt)
  challenging_examples = chat_llm.invoke(prmpt)
  l1 = eval(challenging_examples.content)
  return l1

def annotate_challenging_examples(examples, input_prompt):
  '''
  Generate python code for each given example using llm and input_prompt
  
  Args :
    examples(list[str]) : List of challenging examples
    input_prompt(str) : Initial prompt for code generation
  
  Return : 
    list[dict] : List of dictionary object , 
                `{"question" : example, "code" : code}`
  '''

  annotated_examples = []
  for example in examples:
      prompt = input_prompt.format(query = example)
      annotation = chat_llm.invoke(prompt)
      annotated_examples.append({"question" : example, "code" : annotation.content})
  return annotated_examples

def annotate(annotations,  initial_prompt):
  """
  Analyze errors in generated code for each example and provide error details.

  Args:
    annotations (list[dict]): A list of dictionaries, where each dictionary represents a challenging example and its 
                              corresponding generated code in the format:
                              {"question": challenging example, "code": code}.
    input_prompt (str): The initial prompt used for code generation.

  Returns:
    list[dict]: A list of dictionaries for challenging examples where the generated code contains errors, including
              error analysis and scoring in the format:
              {"question": challenging example, "code": code, "Score": score}.
  """
  annots=[]
  schema = [0,1,2,3,4,5]
  for annotation in annotations:
    a = annotation["code"]
    q = annotation["question"]
    pattern = r'```python\n(.*?)\n```'
    matches = re.findall(pattern, a, re.DOTALL)
    parsed_response = matches[-1] if matches else None
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try :
      prev_model = " "
      while True :
            try:
              exec(parsed_response, globals())
              annot = sys.stdout.getvalue()
              break
            except ModuleNotFoundError as e:
              module_name = e.name
              if module_name == prev_model :
                raise ModuleInstallError(f"Installation failed for module '{{module_name}}': {{str(e)}}")
              prev_model = module_name
              subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
    except Exception as e:
      annot = traceback.format_exc()
    sys.stdout = old_stdout
    response = "Generated Code : " + parsed_response + "\n" + "Obtained output : " + str(annot)
    prmpt = RANKING_PROMPT.format(label_schema = schema, query = q , response =response, prompt = initial_prompt, code = a )
    annotat = chat_llm.invoke(prmpt).content
    prmpt_resp = eval(annotat)
    if prmpt_resp[0] < 4 :
        annots.append({"Query" : q, "Code": a, "Score" : annotat})
  return annots

def error_analysis_fun(input_prompt, annots):
  """
  Anlyze error in the code and given input_prompt for given challenging example using llm

  Args:
      input_prompt (str): prompt used for generating code for challenginf examples
      annots (list[dict]): A list of dictionaries for challenging examples where the generated code contains errors, including
                           error analysis and scoring in the format:
                           {"question": challenging example, "code": code, "Score": score}.

  Returns:
      str: Analysis of the error in the code and input_prompt
  """
  labels = [0,1,2,3,4,5]
  prmpt= ERROR_ANALYSIS.format(prompt=input_prompt, labels = labels, failure_cases = annots)
  analysis = chat_llm.invoke(prmpt).content
  history.append(input_prompt)
  error_analysis.append(analysis)
  
  return analysis

def calibrate_generation_prompt(input_prompt, history, error_analysis, task_desc, meta_prompt):
  """
  Refine the input prompt based on task details, history, and error analysis.

  Args:
      input_prompt (str): The prompt used for generating code for challenging examples.
      history (list[str]): A list of previously generated prompts.
      error_analysis (list[str]): A list of errors identified in the previously generated outputs.
      task_desc (str): A description of the task for which the code is being generated.
      meta_prompt (str): The base prompt used as a foundation for code generation.

  Returns:
      str: A refined prompt incorporating the task description, history, and error analysis.
  """
  prmpt = chat_llm.invoke(PROMPT_REFLEXTION.format(initial_prompt = input_prompt, history=history, error_analysis = error_analysis, task_description = task_desc, meta_prompt= meta_prompt))
  return prmpt.content

def tool_generator(task_description, num_iter):
  """
  Refine the base meta prompt iteratively for a given task description.

  Args:
      task_description (str): A brief description of the task for which the base prompt needs refinement.
      num_iter (int): The number of iterations to refine the base prompt.

  Returns:
      str: The refined prompt after the specified number of iterations.
  """
  global history , error_analysis
  history = []
  error_analysis=[]
  for i in range(num_iter):
    prompt = chat_llm.invoke(PROMPT_GENERATION_PROMPT.format(task_description = task_description , meta_prompt= META_PROMPT))
    challenging_examples = identify_challenging_examples(task_description, prompt.content)
    prompt = prompt.content + META_PROMPT_PART_2
    annotations = annotate_challenging_examples(challenging_examples, prompt)
    annots = annotate(annotations,  prompt)
    error_analysis_fun(prompt, annots)
    prompt = calibrate_generation_prompt(input_prompt= prompt, history = history, error_analysis = error_analysis, task_desc = task_description, meta_prompt = META_PROMPT + META_PROMPT_PART_2)
  return prompt