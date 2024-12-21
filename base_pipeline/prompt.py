'''
PROMPTs FOR INTERLEAVING 
'''

THOUGHT_PROMPT = """
As a Thought Agent, your role is to systematically analyze questions through retrieval and reasoning steps.
You will be provided with an AGENT INPUT containing previous Thoughts, Observations, and Reasoning steps.
Using this information, you need to determine whether the next step should be a RETRIEVAL or REASONING, and what the current
Thought is for which retrieval or reasoning would be performed. You should observe the previous steps and the given question
to determine the next direction.


IMPORTANT : THERE IS NO NEED TO GENERATE FURTHER RETRIEVAL OR REASONING CALLS ONCE YOU REALISE THE NECCESSARY CONTEXT TO ANSWER THE QUESTION HAS BEEN GATHERED.
ALWAYS CHECK THE AVAILABLE CONTEXT (given as agent input below) BEFORE CHOOSING.


Here's how to approach this process:

```
EXAMPLE :
User Query : "How many NVIDIA P100 GPUs were used to train the transformer model?"

RETRIEVAL THOUGHT : How many NVIDIA P100 GPUs were used to train the transformer model?
RAG ACTION: How many NVIDIA P100 GPUs were used to train the transformer model? --> 8 #output of RAG Action
REASONING THOUGHT : Based on the provided context, the number of GPUs was 8.
FINAL ANSWER : The number of GPUs used to train the transformer model was 8.

(End of Example)
```

Guidelines for thoughts:

RETRIEVAL THOUGHTS should:
- Directly ask for specific pieces of needed data in question format without mentioning unnecessary context about "documents" or "Acts" or "reports". For example, instead of "What is the definition of total disablement under the Workmen's Compensation Act?" simply ask, "What is the definition of total disablement?"
- DO NOT ask for specific entities that would other wise be generated from raw content, eg. what is the gross margin trend. Always ask for the raw data such as the gross margins in this case, and you will reason on this later.
- Be clear about what information is being sought.

Example: "What is Coca Cola's total dividends paid for FY2022?"

REASONING THOUGHTS should:
- State what calculation or analysis is needed
- Break complex calculations into steps
- Show clear mathematical working

Example: "Calculate the ratio by dividing total dividends by net income"

Key principles:

1. Each thought builds on previous ones
2. Clear progression from data gathering to calculation
3. Explicit about data sources and calculations
4. Shows step-by-step working
5. Provides a formatted final answer

I hope you understood the example.

AT EACH STEP YOU HAVE TO GENERATE A RETRIEVAL OR A REASONING THOUGHT.

DO NOT POINTLESSLY RE-GENERATE ANY THOUGHT. MAKE USE OF THE CONTEXT AND RE-USE THOSE ANSWERS WHENEVER NEEDED.

YOU CANNOT JUMP TO THE FINAL ANSWER.
ALWAYS GATHER CONTEXT AND USE IT TO BUILD YOUR ANSWER UP. PLEASE.

Now,

RETRIEVER: {retriever}
QUESTION: {question}
Below is the current conversation consisting of interleaving human and assistant messages.
AGENT INPUT: {agent_input}

OUTPUT:
"""

REASONING_PROMPT = """

Your role is to perform self reasoning for a given reasoning thought to help solve a provided question. You must follow the following steps:


 1.You will be provided with an AGENT INPUT containing previous Thoughts, Observations, and Reasoning steps.
 2.You have to follow the last generated REASONING THOUGHT in the AGENT INPUT and perform reasoning as instructed in the THOUGHT.
 3.You can use the past observations and Reasonings to perform the reasoning.
 4.Perform complete calculations/substitution and computaion.


Make sure all the above instructions are followed.

Please use the following output format:
```
REASONING: <your reasoning>
```

If the current reasoning step is the final answer to the input question and adresses it completely, use the following output format:

```
FINAL ANSWER: <your reasoning with all observation>
```

MAKE SURE FINAL ANSWER IS COMPLETE
STRICTLY INLCUDE ALL THE REQUIRED INFORMATION IN FINAL ANSWER [AFTER `FINAL ASNWER:`]
ONLY CONTENT AFTER `FINAL ANSWER :` WILL WE CONSIDERED AS FINAL ANSWER

```
Example Question: "What is Coca Cola's FY2022 dividend payout ratio (using total cash dividends paid and net income attributable to shareholders)? Round answer to two decimal places."
Example Flow:

RETRIEVAL THOUGHT: What is Coca Cola's total cash dividends paid for FY2022?
Observation: Located in the cash flow statement: Total cash dividends paid for FY2022 = $7,578 million
RETRIEVAL THOUGHT: What is Coca Cola's net income attributable to shareholders for FY2022?
Observation: Located in the income statement: Net income attributable to shareholders for FY2022 = $9,542 million
REASONING THOUGHT: Calculate dividend payout ratio using the formula:
Dividend Payout Ratio = Total Cash Dividends Paid / Net Income Attributable to Shareholders
REASONING: Let's calculate step by step:
1. Dividend Payout Ratio = $7,578 million / $9,542 million
2. = 0.7940
3. Round to two decimal places = 0.79

FINAL ANSWER: As Total cash dividends paid is $7,578 million and Net income attributable to shareholder is $9,542 million so we can conclude that Coca Cola's FY2022 dividend payout ratio was 0.79 or 79%.

(End of Example)
```
ONLY CONTENT AFTER `FINAL ANSWER :` WILL WE CONSIDERED AS FINAL ANSWER
NOTHING IS SUPPOSED TO BE GENERATED AFTER THE FINAL ANSWER.

Now,

RETRIEVER: {retriever}
QUESTION: {question}
AGENT INPUT: {agent_input}


OUTPUT:
"""

JARGON_IDENTIFY_PROMPT = """
As an expert Jargon Identifier, you will analyze a user query to identify any technical jargon, abbreviations, or specialized terms. Ensure that you examine each word and phrase carefully, as some jargon may be subtle or field-specific.

Follow the output format specified below: ['jargon1', 'jargon2', 'jargon3',...]. Properly wrap each identified jargon term in a list separated by commas.

If there are no jargon terms present, RETURN JUST the string None.
STRICTLY FOLLOW THE OUTPUT FORMAT MENTIONED ABOVE

Now, User query: {query}
Prev Jargons :  {prev_jargons}

OUTPUT:
"""

REPHRASE_PROMPT = """
Your task is to add clarifications to all instances of jargon in the provided query using the exact meanings or formulas from the given Jargon Dictionary. The goal is to ensure the query is understandable while maintaining its original context and intent.

**Rules:

- Add clarifications for jargon terms by including their corresponding definitions or formulas from the Jargon Dictionary alongside the original jargon term.
- If the definition includes a formula, include it in parentheses after the term, preserving the jargon term itself.
- If the jargon term is defined only with a formula, include both the original term and the formula together in the rephrased query.
- Do not remove or replace the jargon terms; instead, enhance the query by embedding clarifications.
- Ensure the revised query retains its readability, coherence, and natural flow without introducing unrelated changes.
- Use the provided dictionary exclusively for clarifications; do not infer or add any meanings beyond those provided.
- Ensure the rephrased query fully aligns with the original query in content and context.

STRICTLY FOLLOW THE ABOVE RULES
RETURN ONLY REPHRASED QUERY , NOT ANY CLARIFICATION AND TEXT

**Input:**
Query: {query}
Jargon Dictionary: {jargons}

Output:
"""

CONFIDENCE_PROMPT = """
You will be provided with a series of interleaved reasoning and retrieval steps which have led to a FINAL ANSWER, that will also be provided to you.
Based on the series of steps, you are to generate a CONFIDENCE SCORE for the FINAL ANSWER generated. The score must lie between 0 and 1 where a higher score means a greater confidence
in the generated answer.

- If final answer does not fully answer the query , then give low score

RETURN ONLY THE SCORE.

Now,
HISTORY OF SERIES OF INTERLEAVED REASONING AND RETRIEVAL : {steps},
FINAL ANSWER : {answer}

CONFIDENCE SCORE:"""

'''
SUPERVISOR PROMPT
'''

CODE_AGENT_PROMPT = """
As an expert Python code-writing/function calling agent, you have to address a user query by decomposing it into individual steps[acc to tools provided], invoking a single function/tool call at each step until the task is fully resolved using these individual steps.
Before calling any tool, carefully examine "Tool Calling History" and "Responses". If the query cannot yet be fully answered, break it into next subtask and call the next tool to advance each subtask.

** DO NOT MAKE UNNECESSARY OR IRRELEVANT CALLS, AS IT WILL COST HUGE

** `NONE` IS A SPECIAL TOOL, USED TO CREATE TOOL WHEN THERE IS NO SUITABLE TOOL AVAILABLE
** USE RAG TO OBTAIN MORE INFORMATION OR TO ONLY GATHER EXPLICIT INFORMATION
** USE WEBSEARCH TOOL TO OBTAIN GENERAL INFORMATION OR USE IT TO ONLY GATHER EXPLICIT INFORMATION
** DO NOT USE RAG AGENT TO PERFORM ANY TYPE OF OPERATION ON EXISTING INFORMATION
** IF REQUIRED TOOL IS NOT AVAILABLE THEN CALL ["NONE", "NONE", '''Reasoning'''], not the RAG AGENT, DO NOT COMPROMISE WITH THE ACCURACY.
** CALL END TOOL WHEN FINAL ANSWER IS FOUND
** BEFORE CALLING TOOL, ENSURE THAT TOOL HAS CAPABILITIES TO PERFORM THAT TASK , `USE ITS DESCRIPTION TO DETERMINE`

RULES :

1. **Avoid Redundant Tool Calls**:
   - Before calling any tool, check the "Tool Calling History" and "Responses" to avoid repeating a call for data or tasks that have already been resolved.
   - If information has already been retrieved, use that data for subsequent tasks instead of calling the same tool again unnecessarily.

2. **Independence of Tools**:
   - Explicitly pass all relevant context and previously obtained information as arguments when invoking a tool , as All tools operate independently and lack access to prior tool calls, observations, or the user query. so
   - Example: If Step 1 retrieves DPO data, pass that output directly to a calculation tool for further processing rather than re-calling RAG to retrieve the same data.
   - Example: If Query asked to calculate something complex, and you have breakdown the problem into subtask, then pass all the previous relevant information to RAG

3. **Completion Check**:
   - Before calling a tool, confirm if all parts of the query have been addressed using the tool responses.
   - If all parts are fully answered, return: `["end_tool", ["end"], "All the question are answered]`.

4. **When No Suitable Tool Exists**:
   - IF THERE IS NO SUITABLE TOOL THEN DO NOT CALL RAG AGENT
   - If the task requires a tool not available in the tool list, or if the query cannot proceed further due to tool limitations, return: `["NONE",['''NONE'''], '''Reason why no suitable tool is available''']`.

5. **Output Format**:
   - Ouput should be a single tool call
   - For each unique step, call the relevant tool using this format:
     ```
     ["tool_name", ['''arg1''', arg2, ["arg3", "arg4"], {{"arg5":"arg6"}}, ........], '''Explain current query requirement and why this tool is best fit for it not others''']
     ```
   - Ensure all arguments align strictly with the tool’s purpose and input requirements.
   - ENSURE ALL THE ARGUMENTS FOLLOW THE OUTPUT FORMAT
   - MAINTAIN THE DATA TYPE OF ALL THE ARGUMENTS

6. **Step-by-Step Problem Solving**:
   - Build the solution incrementally, resolving one subtask at a time.
   - Ensure cost efficiency by minimizing redundant tool calls and avoiding unnecessary steps.
   - Do not jump to the final answer until all intermediate steps are complete.

Example Flow:
```
    `SUPPOSE` initially , only the tool1 and tool2 are present ; tool1 - perform document based qa task, tool2 - perform calculation, tool3 - add two number (args :- int a, int b)
    Query: "What is the square root of the 2500 + company's gross margin in FY 2023? Generate a translation of the answer into German?"

    # Step 1: ["tool1", ['''What was the gross margin in FY 2023?'''], '''As we need gross margin first , which we have to retrieve from document so calling tool1''']
      response The gorss margin of comapny is $2500

    # Step 2: ["tool3", [2500, 2500], '''As now we have to add two numbers , we will call tool3 , as, we have tool2 but tool3 is buillt for adding so calling it''' ]
      response The addition is 5000

    # Step 2: ["tool2", ['''What is the square root of 5000?'''], '''As now we have addition of 2500 , gross margin , we now have to calculate the square roor, which is a calculation task not a norma qa task so calling tool2, we can call tool1 but ''']
      response The square root of 2500 is 50

    # Step 3: ["NONE", ["NONE"], "There is no suffiecient tool for translating , as tool1 perform document based qa task , we can call it but is not made for it , while NONE is made for handling such task where there is no specific tool , and tool2 perform calculation and this is a translation task, so we reuire a addition tool so returning NONE"]
      response ADD tool3 in your tool list which can translate given text to any language provided in the query

    # Step 4: ["tool3", ['''Translate `Square root of grass margin 2500 is 50` into German''''], '''As tool3 is specifally designed to perform translation tool''']
      response translation

    # Step 5: ["end_tool", '''end''', "All the question are asnwered"]

````
End Of Example

IMPORTANT:
- IF THERE ARE NO RELEVANT TOOLS TO FURTHER ANSWER THE QUERY OR THE TOOL LIST IS EMPTY, RETURN NONE.
- `AVOID REPETATIVE CALLS, CAREFULLY EXAMINE THE PREVIOUS TOOL CALLING HISTORY.`
- VALUE OF ARGUMENT MUST ALIGN WITH THE TOOL DESCRIPTION:
   - Use only the input formats specified in the tool descriptions.
   - Arguments must strictly match the tool’s purpose and input requirements .

** RETURN ONLY THE SINGLE FUNCTION CALL.
STRICTLR FOLLOW THE RULES
STRICTLY FOLLOW THE OUTPUT FORMAT
STICK TO ONLY THE TOOLS PRESENT IN `PROVIDED TOOLS LIST`. DO NOT USE ANY OTHER TOOLS OR MAKE UP OR HALLUCINATE TOOLS.

Now,

Query : {query},
Tool Calling History : {scratchpad},
Responses : {responses},
Available tools : {tools},

OUTPUT:
"""

CODE_REFLEXION_PROMPT = """
As an expert Code Reflexion agent, your task is to analyze and resolve errors in tool calls or Python code implementations. You will refactor the given Python code and ensure the tool calls are accurate, valid, and aligned with the query requirements. If no tool can resolve the query, provide a reasoned output indicating the limitation.

Inputs Provided:

Query: The task or problem description.
Previous Code: The last implementation of the Python code.
Error: The specific error encountered during execution.
Available Tools: A list of tools that can be used to resolve the query.
Workflow for Error Resolution:

** `NONE` IS A SPECIAL TOOL, USED TO CREATE TOOL WHEN THERE IS NO SUITABLE TOOL AVAILABLE
** IF `rag_agent IS IN TOOLS LIST ` then USE `rag_agent` TO OBTAIN MORE INFORMATION OR TO ONLY GATHER EXPLICIT INFORMATION IF PROVIDED 

Analyze the Problem:
- Understand the Query: Identify the intended functionality.
- Review the Error:
  - Categorize the issue, e.g.:
     Tool not present in the list. -> IN THIS CASE CHANGE THE TOOL
     Incorrect arguments. -> IN THIS CASE MODIFY ARGUMENTS
     Tool execution failure. -> IN THIS CASE CHANGE THE TOOL
     Python syntax or logic errors. -> IN THIS CASE DECIDE ACCORDING TO THE ERROR
     Limitations of available tools. -> CHANGE THE TOOL OR RETURN `NONE`
  - Examine the Code: Identify how the current implementation deviates from the query requirements or tool descriptions.

- Resolve the Issue:
  - Select the Correct Tool:
    Ensure the tool matches the task described in the query.
    If no tool is suitable, provide a reason and return NONE.
  
  - Validate Arguments:
     Refactor the arguments to align with the tool's description.
     Ensure correct data types and proper format.

  - Refactor for Correct Execution:
    If a tool execution fails due to code errors, fix those issues.
    Ensure the refactored implementation resolves the original query.

  - Handle Missing Tools:
    If no tool can address the query, return: ["NONE", ["NONE"], "Reason why no suitable tool is available."]

Rules to Follow:

Strictly Use Available Tools:
 - Use only tools provided in the list.
 - Do not create or assume unavailable tools.

Argument Accuracy:
 - Align all arguments with tool descriptions.
 - Avoid redundant or unnecessary tool calls.

Clear Justifications:
 - Provide an explanation for tool selection and adjustments.
 - If no tools fit, clearly justify the NONE response.

Output Format:
 - Return a single valid tool call in the following format: ["tool_name", [arg1, arg2, ...], "Explanation for tool choice and alignment with the query."]
 - If no suitable tool exists: ["NONE", ["NONE"], "Reason why no suitable tool is available."]

Key Considerations:
 - Address both tool selection and execution errors.
 - Maintain precision in tool call formatting.
 - Avoid repeating errors from the previous implementation.
 - Provide clear and actionable explanations in all outputs.

** RETURN ONLY THE SINGLE FUNCTION CALL.
STRICTLY FOLLOW THE OUTPUT FORMAT
STICK TO ONLY THE TOOLS PRESENT IN `Available TOOLS LIST`. DO NOT USE ANY OTHER TOOLS OR MAKE UP OR HALLUCINATE TOOLS.



Query : {query},
Previous Code (erroneous) : {agent_code},
Error : {error},
Available tools : {tools}

"""

FAILURE_DETECTION_PROMPT = """
As an expert failure detection agent, you will be provided with the query, your last Python code implementation, the error traceback in your last implementation, and a list of
available tools. Your task is to review the traceback and follow the guidelines mentioned below:

1. If the error traceback is an APIError  RETURN 1.
2. If the tool generated DOES NOT EXIST in the Available Tools list given to you, RETURN 0.
3. If the error traceback is a SilentError, RETURN 0.
4. Else, if the traceback implies a python error, that is, the arguments have been passed wrongly, or not in the correct order or the correct data type, RETURN 0.

DO NOT RETURN ANYTHING ELSE EXCEPT THE INTEGER VALUES.

Now,

Previous code (wrong) : {agent_code},
Error traceback :{traceback},
Available Tools : {tools},
Descriptions of available tools : {descs}

OUTPUT:
"""

CRITIC_AGENT_PROMPT_1 = """
You are an expert critic agent tasked with evaluating tool arguments. For each tool call, you will be provided with:
- The user query.
- The tool call with reasoning why it is called.
- The arguments passed to the tool.
- A history of prior tool calls and responses.

Your goal is to assess whether the `arguments` are valid and relevant in the given context and the tool's function. Follow these guidelines:

### RULES:

- Analyze the scratchpad to understand the current progress toward solving the query.
- Focus on the `args` list (tool arguments).
- Check if the arguments are valid and make sense in the context of the user query.
- Tool is called to perform the subtask of the actual query
- PROPERLY ANALYZE THE REASONING WHY TOOL HAS BEEN CALLED

- If the arguments are nonsensical or completely irrelevant and not relevant to the query and any of its subtask RETURN:
  ```json
  {{
    "score": 1,
    "reasoning": "Explanation of why the arguments are invalid."
  }}
  ```
- Otherwise, RETURN:
  ```json
  {{
    "score": 0,
    "reasoning": "Explanation of why the arguments are valid and align with the query."
  }}
  ```


## OUTPUT FORMAT (JSON-safe):
- Ensure the output is strictly formatted as:
  ```json
  {{
    "score": 0 or 1,
    "reasoning": "Your reasoning , within double inverted comma."
  }}

### IMPORTANT:
- Keep reasoning concise
- SCORE MUST BE AN INTEGER VALUE: `0` OR `1`.

** STRICTLY FOLLOW THE OUTPUT FORMAT

Now, evaluate the following:
Query: {query}
Tool Call: {code_last}
Tool Description: {desc}
Tool Calling History: {scratchpad}

OUTPUT:

"""

CRITIC_AGENT_PROMPT_2 = """
You are an expert critic agent tasked with evaluating tool response. For each tool call, you will be provided with:
- Main query.
- Tool call with reasoning why it is called.
- Descripiton of the tool.
- Tool Call Response

Your goal is to assess whether whether the tool's response aligns with the question asked in tool call.
QUERY HAS BEEN BREAKDOWN INTO SUBPARTS AND GIVEN TOOL HAS BEEN CALLED TO ADRESS THAT PART ONLY
GIVEN TOOL IS CALLED TO ANSWER THE SUBPART OF THE QUERY AS EXPLAINED IN THE REASONING OF TOOL CALL

### RULES:
- Focus on the `response` (tool output).
- Check if the output is obviously incorrect or clearly unrelated to the question asked in `TOOL ARGUMENTS`, or cannot logically be the correct response for the given TOOL ARGUMENT and context.
  e.g., The value of 2*2 = 10000. This is clearly wrong, as 2*2 cannot possibly exceed even 10, since it is 4.
- If the tool's intent and functionality are correctly applied but the response indicates a legitimate limitation (e.g., no data for a given query), RETURN: 0
- If the response claims that response has been generated and saved to local device or provided location (e.g., file has been saved to your device, chart has been generated and save to your provided url ), RETURN: 0
- If the response partially addresses the query asked in tool call or tries to answer any subparts of the query or the tool's intent, RETURN: 0
- If the response is invalid or clearly unrelated to the tool call or cannot logically be correct, RETURN: 1
- Otherwise, RETURN: 0
  ```

## OUTPUT FORMAT (JSON-safe):
- Ensure the output is strictly formatted as:
  ```json
  {{
    "score": 0 or 1,
    "reasoning": "Your reasoning , within double inverted comma."
  }}

### IMPORTANT:
- KEEP REASONING CONCISE
- SCORE MUST BE AN INTEGER VALUE: `0` OR `1`.

STRICTLY FOLLOW THE OUTPUT FORMAT

Now, evaluate the following:
Tool Call: {code_last}
Tool Response: {response}
Tool Description: {desc}

OUTPUT:

"""

SILENT_ERROR_REFLEXION = """
As an expert Python code reflexion agent, your task is to refactor the faulty tool call provided to you.
The tool call is faulty in the sense, the arguments provided to the tool are incorrect. Using the original user query, the previous responses history, the tool call, tool description
you are to return the refactored tool call with the correct argument values, in the exact format as the input tool call.


Output Format:
 - Return a valid tool call in the following format AS IN TOOL CALL: ["tool_name", [arg1, arg2, ...], "Explanation for tool choice and alignment with the query."]


RETURN JUST THE REFACTORED TOOL CALL WITH THE CORRECT ARGUMENT VALUES IN THE EXACT FORMAT AS THE INPUT TOOL CALL.

STRICTLY FOLLOW THE OUTPUT FORMAT AS IN PRVIOUS TOOL CALL

Now,

Tool Call : {call},
Reason : {reason}
User query : {query},
Tool Calling Responses History : {scratchpad}


OUTPUT:
"""

FINAL_RESPONSE_PROMPT = """
As a final response generator, you will be provided with the user query, the tools called upto this point along with their arguments, and the corresponding responses received after invoking each tool.
Your task is to make use of these responses to generate the final answer to the user query.
Make the final answer short and crisp. As crisp as one can get.

Now,
Query : {query},
Tool calling history : {code},
Responses : {responses}


OUTPUT:
"""

CONFIDENCE_SCORE_PROMPT = """
You are an excellent confidence scoring prompt. You will be provided with the user query and a particular tool along with its description.
Your task is to generate a score between 0 and 1, indicating the confidence with which you think the tool can help in answering the user question.

A higher score means that the confidence that this tool is important to answering the query is high.

Examples:
```
Query : What is the product of 11 and 12.
Tool = Calculator
Desc : performs arithmetic calculations

Score : 0.9
```

RETURN ONLY THE SCORE
Now,
Query : {query},
Tool Name : {name},
Tool Desc : {desc}

CONFIDENCE SCORE:
"""

'''
AUTO AGENT BUILDER PROMPT
'''

PROMPT_REFLEXTION = """
You are an expert prompt generator, specializing in transforming user descriptions into highly effective prompts. Your task is to produce a prompt following a strict format (the "meta prompt") that will generate Python code fulfilling the user's request.

*Meta Prompt Example*:
{meta_prompt}

Also,
Here is the previous prompt : {initial_prompt}

## Here is the history of all previously generated prompts.
{history}

This is the error analysis for the last prompt:
Note that the labels here lie on a scale - [1,2,3,4,5]. The higher score means the better performance.
ADD INSTRUCTION TO RESOLVE ERRORs AFTER ANALYZING
{error_analysis}.

Given the user’s task description below, and taking insights from the error analysis, replace <SHORT TASK SUMMARY> and  <insert detailed task definition here> in meta prompt to generate a prompt in the exact structure of the meta prompt that precisely captures the user’s requirements.
IT IS COMPULSORY TO FOLLOW THE STRUCTURE OF META PROMPT.

IMPORTANT :
- YOU CAN REPLACE ONLY <insert detailed task definition here> AND <SHORT TASK SUMMARY>  with the suitable content
- ADD INSTRUCTION TO RESOLVE ERRORS FROM ERROR ANALYSIS
  eg :- x function takes only two argument
- YOU HAVE TO STRICTLY FOLLOW FORMAT OF CODE AS EXPLAINED IN META PROMPT
- YOU CAN NOT CHANGE OTHER CONTENT IN THE INITIAL_PROMPT

*User Task Description*:
{task_description}

*Output*:
"""

EDGE_CASE_GEN = """ 
As an advanced language model you should create 2 highly challenging and unique samples for the task outlined below.
These samples should be intricately designed to test the limits of the task's instructions, challenging yet relevant to the task description.
**ENSURE THAT THESE SAMPLES DOES NOT REQUIRE ANY INPUT FROM THE USERS, ALL THE DATA MUST AVAILABLE IN THE GENERATED SAMPLE**

Task Description:
{task_description}

Task Instructions:
{instruction}

A sample means a question or a query that is challenging and falls in line with the task description and instruction.
It should be a natural language query , eg. What is ...?, Where is..? and so on.
OUTPUT SHOULD BE A LIST OFUNIQUE SAMPLE

Example :-
OUTPUT :- ['''Question 1''',  '''Question 2''' ]

### Requirements for Challenging Samples:
Keep in mind that the samples you are generating for the task are sent to a tool, that is implemented as a single function and not a series of functions. That is forbidden for our use case. DO NOT VIOLATE THIS CONDITION.
It IS COMPULSORY TO RETURN A LIST

Generate the samples keeping these requirements in mind.
RETURN ONLY THE SAMPLES.

OUTPUT:
"""

ERROR_ANALYSIS = """ 
Assistant is a large language model designed to provide a high quality analysis for every task.
Here is the prompt instructions that was given to the model: {prompt}

An expert ranker evaluated the model's performance on the given task description.
and rank according to the following scale: {labels}

Here is a list of challenging cases for the given prompt and their rank:
Challenging Cases: {failure_cases}

Note that the ranker labels are __absolutely correct__, but the prompts (task descriptions) AND GENERATED CODE may be incorrect and need modification.
Your task is to provide a brief analysis of the given prompt performance.
Guidelines:
1. The analysis should contain only the following information:
    - A summary of the common mistakes of the PROMPT AND CODE and the ways he can be improve his generation, try to cluster the failure cases into groups and describe each group.
2. The total length of your analysis should be less than 400 token!

Analysis:
"""

META_PROMPT = """
You are an excellent <insert detailed task definition here>.
Given a user input in the form of a string query , you have to ** return python programme ** to answer the ** query[provided by user] ** in context to task description. The returned value of the programme should be the answer to the query[provided by user].
On executing the code[python programme], the value returned must be the specific answer to the provided user query, not a general implementation.
NOTE :-
- Use only standard python libraries.
- Close files and clear matplotlib figure if used
- GENRATE CODE TO ANSWER USER PROVIDED QUERY ONLY

"""

PROMPT_GENERATION_PROMPT = """
You are an expert prompt generator, specializing in transforming user descriptions into highly effective prompts. Your task is to produce a prompt following a strict format (the "meta prompt") that will generate Python code fulfilling the user's request.

**Meta Prompt Example**:
{meta_prompt}

Given the user’s description below, generate a prompt in the exact structure of the meta prompt that precisely captures the user’s requirements.
IT IS COMPULSORY TO FOLLOW THE ENTIRE META PROMPT .
- **MENTION THE TASK CLEARLY and in detailed way**

**User Task Description**:
{task_description}

# Example Of Task Desciption :-
Example 1 :- You are a expert python code generator , specializing in calculator agent that can generate code with repect to user requirement
Example 2 :- You are an expert python code generator , specializing in generating graph or chart tailored to user requirements

**Output**:
"""

RANKING_PROMPT = """ 
As an excellent critic agent, you will be provided with a user query, an LLM response and the PROMPT and CODE used to generate the response.
Your task is to rate the generated response based on the above factors, on a scale : {label_schema}, with a higher score meaning a better and more well rounded response. Provide the highest label if the output is perfect.

IF RESPONSE SAYS THERE IS ERROR IN CODE THEN ANALYZE THE CODE PROPERLY

STRICTLY FOLLOW THE SCALE. RETURN THE SCORE ALONG WITH YOUR SHORT CRISP REASONING FOR THE SAME.
REASONING SHOULD BE COMPLETE , SHORT, EXPLAINING THE ERROR
OUTPUT FORMAIT :- [INTEGER SCORE, '''REASONING''']

EXAMPLE :

EXAMPLE 1
[2, '''FUNCTION REQUIRE TWO ARGUMENTS BUT ONLY ONE IS PROVIDED''']

EXAMPLE 2
[4, '''EVERYTHING IS FINE BUT TASK DESCRIPTION CAN BE IMPROVED BY ADDING DETAILS''']

STRICTLY FOLLOW THE OUTPUT FORMAT

Now,
Query : {query},
Response : {response},
Prompt : {prompt},
Code : {code}

OUTPUT:
"""

META_PROMPT_PART_2 = '''

Here is an example of how the markdown code must LOOK LIKE:
Example 1:-
```python
<code/>
def func_name():
  <code/>
  def func_2():
    <code/>
  <code/>
  return ans
ans_user_query = func_name()
print(f"answert to the query " + str(ans_to_query))
```
Example 2 :-
```python
<code>
def func_name(args):
  <code>
  return ans
ans_user_query = func_name(args)
print(f"answert to the query " + str(ans_to_query))
```
Example 3 :-
```python
<code>
print(f"answert to the query " + str(ans_to_query))
```
Example 4 :-
```python
<code>
def func_name():
  <code>
  return ans
ans_user_query = func_name()
print(f"answert to the query " + str(ans_to_query))
```
IT IS COMPULSORY TO HAVE ONLY ONE PRINT STATEMENT IN THE CODE STATING CODE ANSWER OF THE QUERY , EVENT IF TASK IS LIKE SAVING THE FILE OR GENERATING THE CHART THEN PRINT FILE SAVE SUCCESSFULLY OR CHART GENERATED SUCCESSFULLY.
STRICTLY FOLLOW THE FORMAT SHOWN IN ABOVE EXAMPLES
STRICTLY FOLLOW  THE RULES EXPLAINED ABOVE
**USE ONLY SINGLE FUNCTION**
CODE SHOULD STRICTLY ANSWER ONLY AS ACCORDING TO THE USER QUERY

Now,
USER : <SHORT TASK SUMMARY> {query} #LEAVE THIS UNTOUCHED
OUTPUT:
'''

WEBSEARCH_PROMPT= """
You are a Answer synthesizer.
You will eb provided with the query and top 3 web search result
Using  ONLY web search result and query you have to generate answer to the query
- Do not use you existing information.
- Output format must be string like "Answer to the query is :- {{ans}}"

Now,
Query :- {query}
Web Search Result :- {response}

Output :-
"""