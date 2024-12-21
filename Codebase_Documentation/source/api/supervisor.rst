Supervisor Agent
================

Overview
--------
The Supervisor Agent is the governing agent designed to handle user queries, leveraging tools, descriptions, and a RAG from a knowledge base. It supports iterative problem-solving, manages errors, and facilitates follow-up interactions with users. This agent ensures robust handling of tool calls and dynamically resolves execution errors.

Initialization
--------------
.. py:class:: SUPERVISOR_AGENT(tools, tools_aux, llm, tool_map, path, reflextion_limit = 10, top_k = 5, max_steps = 10)

   Initialize the SUPERVISOR_AGENT with the necessary tools, retrieval systems, and memory setup.

   :param list tools: Primary tools available for query resolution.
   :param list tools_aux: Auxiliary tools for fallback or extended processing.
   :param object llm: The language model used for generating responses.
   :param dict tool_map: A mapping of tool names to their descriptions.
   :param str path: File path for the PDF.
   :param reflextion_limit: The maximum attempts to modify agent_code and resolve the error.
   :type reflextion_limit: int, optional
   :param top_k: Number of top results to retrieve from retriver.
   :type top_k: int, optional
   :param max_steps: The maximum attempts allowed for the RAG agent to determine the final answer.
   :type max_steps: int, optional


Methods
-------
.. py:method:: run(query, follow_up_response=None)

   Generate an answer to the given query, utilizing previous responses for context and prompting follow-up questions.

   :param str query: The user's question.
   :param list follow_up_response: (Optional) List of responses from previous queries for additional context.
   :return: The answer to the user's query.
   :rtype: str

.. py:method:: api_reflexion(agent_code)

   Manage faulty tool calls by either modifying or removing a tool. This mechanism ensures optimal tool usage.

   :param list agent_code: The problematic tool call, structured as:
       ["tool_name", [arguments], "Reasoning"]
   :return: A tuple containing the modified tool call and the response generated after modification.
   :rtype: tuple

.. py:method:: code_reflexion(agent_code, error)

   Resolve Python execution errors during tool calls by modifying the tool's code.

   :param list agent_code: The last tool call that caused the error.
   :param str error: The error message generated during execution.
   :return: The modified tool call and its response.
   :rtype: tuple

.. py:method:: build_code()

   Retrieve the tool called and its response.

   :return: The tool call and its associated response.
   :rtype: tuple

.. py:method:: detect_failure(agent_code, callback)

   Detect the type of error in a tool call and categorize its severity.

   :param list agent_code: The erroneous tool call.
   :param str callback: The error message or code.
   :return: "1" if the error is significant, "0" otherwise.
   :rtype: str

.. py:method:: critic_agent(agent_code, desc, func_response, scratchpad)

   Evaluate the correctness of tool call arguments and their alignment with the query.

   :param list agent_code: The current tool call.
   :param str desc: A description of the tool call's purpose.
   :param str func_response: The response from the tool call.
   :param str scratchpad: Context from prior tool calls.
   :return: A list containing the evaluation result and reasoning.
   :rtype: list

.. py:method:: silent_reflexion(code, reason)

   Resolve invalid tool call arguments flagged by the `critic_agent`.

   :param str code: The tool call with potentially invalid arguments.
   :param str reason: Explanation of why the arguments are invalid.
   :return: A corrected tool call with valid arguments.
   :rtype: list

Error Handling
--------------
The Supervisor Agent employs robust mechanisms to detect and resolve errors:
* **API Reflection:** Identifies and handles missing or misconfigured tools.
* **Code Reflection:** Fixes execution errors in tool calls.
* **Silent Reflection:** Adjusts invalid arguments in tool calls.

Requirements
------------
* langchain
* llama_index
* jinaai for embeddings
* A compatible LLM for query generation

Recommended Usage
-----------------
The following demonstrates how to initialize and use the `SUPERVISOR_AGENT`:

.. code-block:: python

   # Initialize the agent
   agent = SUPERVISOR_AGENT(tools, tools_aux, llm, tool_map, "path/to/pdf")

   # Process a query
   answer = agent.run("What is the net revenue of the company and find 5% of it?")
   print(answer)