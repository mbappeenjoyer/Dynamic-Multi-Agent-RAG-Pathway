Code and Reasoning Agent
========================

Overview
--------
The Code and Reasoning Agent is a dynamic reasoning agent designed to leverage Pathway's reactive framework for advanced Retrieval-Augmented Generation (RAG) and iterative query processing. It integrates tools, large language models (LLMs), and Pathway's computational capabilities for retrieval, reasoning, and adaptive tool management.

Initialization
--------------
.. py:class:: CodeandReasoningAgent(tools, tools_aux, llm, tool_map, path)

   Initialize the CodeandReasoningAgent with tools, a language model, and Pathway integration.

   :param list tools: List of available tools for agent operations.
   :param list tools_aux: Auxiliary tools list.
   :param object llm: Language model for generating responses.
   :param dict tool_map: Mapping of tool names to their implementation.
   :param str path: Path for Pathway-based operations and data retrieval.

Methods
-------
.. py:method:: answer_query(pw_ai_queries)

   Create a RAG response with adaptive retrieval using Pathway.

   :param pw.Table pw_ai_queries: Pathway table containing query input.
   :return: Pathway table with prompt and generated result.
   :rtype: pw.Table

   **Pathway Integration:**
   
   - Converts pandas DataFrame to Pathway table using `pw.debug.table_from_pandas`.
   - Processes queries within Pathway's reactive table framework.

.. py:method:: run(query, follow_up_response=None)

   Execute iterative query processing with reasoning.

   :param str query: Primary query to process.
   :param list follow_up_response: Optional context from previous responses.
   :return: Tuple containing the final response, logs, and logged tools.
   :rtype: tuple

.. py:method:: api_reflexion(agent_code)

   Perform API-level reflection and tool management.

   :param str agent_code: Code or instruction for tool reflection.
   :return: Tuple containing refined agent code and function response.
   :rtype: tuple

   **Pathway Integration:**

   - Dynamically manages tools within Pathway's flexible framework.
   - Supports runtime tool addition and modification.

.. py:method:: code_reflexion(agent_code, error)

   Handle code-level reflection and error correction.

   :param str agent_code: Current agent code.
   :param Exception error: Error encountered during execution.
   :return: Tuple containing refined agent code and function response.
   :rtype: tuple

.. py:method:: build_code()

   Build and execute tool calls with adaptive reasoning.

   :return: Tuple containing the selected tool code and its response.
   :rtype: tuple

   **Pathway Integration:**

   - Employs Pathway tables for prompt and model selection.
   - Facilitates interleaved reasoning and tool execution.

.. py:method:: detect_failure(agent_code, callback)

   Detect potential failures in tool execution.

   :param str agent_code: Code being analyzed.
   :param str callback: Error traceback or execution context.
   :return: Failure detection result.
   :rtype: str

.. py:method:: critic_agent(agent_code, desc, func_response, scratchpad)

   Critically analyze tool execution.

   :param str agent_code: Tool call details.
   :param str desc: Tool description.
   :param str func_response: Response from the tool.
   :param str scratchpad: Accumulated context.
   :return: Criticism or validation of tool execution.
   :rtype: str

.. py:method:: silent_reflexion(code, reason)

   Perform silent refinement of tool calls.

   :param str code: Original tool call.
   :param str reason: Refinement context.
   :return: Refined tool call.
   :rtype: str

.. py:method:: add_tool(tool_desc)

   Dynamically add a new tool to the agent's toolkit.

   :param str tool_desc: Description of the tool to be added.
   :return: Tuple containing refined agent code and function response.
   :rtype: tuple

.. py:method:: answer_interleaved_query(prompt)

   Perform interleaved retrieval and reasoning with Pathway.

   :param str prompt: Query to process.
   :return: Generated answer through interleaved reasoning.
   :rtype: str

   **Pathway Integration:**

   - Leverages Pathway's table-based LLM processing.
   - Alternates between retrieval and reasoning steps.
   - Supports dynamic query expansion and contextual refinement.

.. py:method:: _perform_retrieval_step(agent_input, query)

   Conduct a retrieval step using Pathway's query mechanism.

   :param str agent_input: Accumulated agent context.
   :param str query: Specific retrieval query.
   :return: Retrieved query results.
   :rtype: str

   **Pathway Integration:**

   - Uses `pw_ai_answer` for direct Pathway-based query resolution.

.. py:method:: _perform_reasoning_step(agent_input, query)

   Execute reasoning with LLM capabilities.

   :param str agent_input: Accumulated agent context.
   :param str query: Reasoning query.
   :return: Reasoning response.
   :rtype: str


Recommended Usage
-----------------
.. code-block:: python

   import pathway as pw

   # Initialize agent
   agent = CodeandReasoningAgent(tools, tools_aux, llm, tool_map, path)

   # Process a query
   query = "What are the implications of AI in finance?"
   response, logs, tools_used = agent.run(query)
   print(response)

Requirements
------------
* Pathway
* Jina embeddings for vector memory
* Compatible LLM for Pathway-based operations
* Tools mapped for dynamic execution

Error Handling
--------------
The class handles:

* Dynamic tool addition and failure detection.
* Code-level reflection and error refinement.
* Iterative reasoning and query expansion within Pathway's framework.