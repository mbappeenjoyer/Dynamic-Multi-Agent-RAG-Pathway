Interleaved RAG Question Answerer
=================================

Overview
--------
The `InterleavedRAGQuestionAnswerer` is an advanced Retrieval-Augmented Generation (RAG) system designed for dynamic question-answering using Pathway's reactive processing framework. It leverages interleaved reasoning and retrieval to iteratively refine answers. This integration allows for scalable, distributed, and efficient query processing.

Initialization
--------------
.. py:class:: InterleavedRAGQuestionAnswerer(llm, default_llm_name=None, short_prompt_template=prompts.prompt_short_qa, long_prompt_template=prompts.prompt_qa, summarize_template=prompts.prompt_summarize, strict_prompt=False, interleave_depth=3)

   Initialize the `InterleavedRAGQuestionAnswerer` with Pathway's computational graph integration.

   :param llm: Language model integrated with Pathway for reactive computation.
   :param str default_llm_name: Default model name for Pathway-based inference (optional).
   :param pw.UDF short_prompt_template: Pathway User-Defined Function for handling short queries (default: `prompts.prompt_short_qa`).
   :param pw.UDF long_prompt_template: Pathway UDF for complex queries (default: `prompts.prompt_qa`).
   :param pw.UDF summarize_template: Pathway UDF for summarizing results (default: `prompts.prompt_summarize`).
   :param bool strict_prompt: Flag indicating whether to enforce strict prompt handling (default: `False`).
   :param int interleave_depth: Maximum iterations for interleaved reasoning (default: `3`).

Methods
-------
.. py:method:: answer_query(pw_ai_queries)

   Generate a RAG response using Pathway's reactive table transformation.

   :param pw.Table pw_ai_queries: Input query table for reactive computation.
   :return: Transformed table containing computed query responses.
   :rtype: pw.Table

   **Example:**

   .. code-block:: python

       import pathway as pw

       # Sample query table
       query_table = pw.Table.from_rows([{"query": "Who are the stakeholders impacted by the new policy?"}])

       # Initialize question answerer
       question_answerer = InterleavedRAGQuestionAnswerer(llm=my_llm)

       # Generate responses using Pathway
       response_table = question_answerer.answer_query(query_table)
       response_table.view()

.. py:method:: answer_interleaved_query(prompt)

   Execute interleaved reasoning through Pathway's streaming computation framework.

   :param str prompt: Query processed using Pathway's reactive graph.
   :return: Final answer generated via iterative retrieval and reasoning.
   :rtype: str

   **Example:**

   .. code-block:: python

       # Query for interleaved reasoning
       prompt = "Explain the impact of the scheme on the total current liabilities?"

       # Generate interleaved response
       response = question_answerer.answer_interleaved_query(prompt)
       print(response)

.. py:method:: _perform_retrieval_step(agent_input, query)

   Conduct a retrieval step using Pathway's efficient data lookup mechanisms.

   :param str agent_input: Context processed in Pathway's stateful computation.
   :param str query: Retrieval query transformed within the reactive pipeline.
   :return: Retrieved information from Pathway-managed sources.
   :rtype: str

.. py:method:: _perform_reasoning_step(agent_input, query)

   Execute a reasoning step via Pathway's distributed computation model.

   :param str agent_input: Accumulated context in Pathway's computation graph.
   :param str query: Reasoning query processed reactively.
   :return: Reasoning response generated through iterative streaming.
   :rtype: str

Recommended Usage
-----------------
.. code-block:: python

   import pathway as pw

   question_answerer = InterleavedRAGQuestionAnswerer(llm=llm)

   # Create a Pathway query table
   query_table = pw.Table.from_rows([{"query": "How does collateralized debt obligation (CDO) work?"}])

   # Answer queries using Pathway
   response_table = question_answerer.answer_query(query_table)
   response_table.view()

Requirements
------------
* Pathway
* Custom prompts for short, long, and summarization queries
* Language model compatible with Pathway's computational graph

Error Handling
--------------
The class includes robust mechanisms for handling:

* Reactive query transformations in Pathway.
* Iterative retrieval and reasoning failures.
* Prompt validation and enforcement based on the `strict_prompt` parameter.
* Depth constraints in interleaved reasoning loops.
