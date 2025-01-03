Default Tools
=============

Overview
--------
Provides pre-built tools available for use by the supervisor

Functions
---------

.. py:function:: rag_agent(query: str) -> str

   Used for answering queries based on context retrieved from user-provided documents.

   :param query: The query to be passed to the RAG agent.
      Example: "What was Nike's gross margin in FY 2022?"
   :return: The response from the RAG agent, along with the confidence score.
   :raises RuntimeError: If an error occurs during the retrieval or response generation process.

Recommended Usage:

.. code-block:: python

   query = "What is the revenue of Nike for FY 2022?"
   response = rag_agent(query)
   print(response)


.. py:function:: calculator(query: str) -> str

   Make a calculation-based query to receive a response. Accepts one argument.

   :param query: The query to be passed to the calculator agent, which can be a set of sentences or a single sentence.
      Example: "What is five times 12?"
   :return: The response from the calculator agent.
   :raises ValueError: If the parsed response cannot be executed properly.

Recommended Usage:

.. code-block:: python

   query = "What is five times 12?"
   result = calculator(query)
   print(result)


.. py:function:: graph(query: str) -> str

   Generates a graph based on the query and saves it as a `.png` file.

   :param query: The query to be passed to the graph agent, specifying the type and data of the graph.
      Example: "Create a bar chart of sales data for Q1."
   :return: The file path where the graph is saved or an error message if generation fails.
   :raises Exception: If an error occurs while generating the graph.

Recommended Usage:

.. code-block:: python

   query = "Create a bar chart of sales data for Q1"
   graph_response = graph(query)
   print(graph_response)


.. py:function:: download_txt(content: str, filename: str = "output.txt") -> str

   Saves the given content to a `.txt` file in the current working directory.

   :param content: The text content to be saved.
   :param filename: The name of the file to save the content to (default: "output.txt").
   :return: A confirmation message indicating that the file has been saved successfully.
   :raises IOError: If there is an error while saving the file.

Recommended Usage:

.. code-block:: python

   content = "This is some content to save."
   filename = "output.txt"
   result = download_txt(content, filename)
   print(result)


.. py:function:: web_search_agent(query: str) -> str

   Retrieves general online information from available sources based on the query.

   :param query: The query to search online.
      Example: "Who is the prime minister of India?"
   :return: The response from the web search agent.
   :raises ConnectionError: If there is an issue with the web search API.

Recommended Usage:

.. code-block:: python

   query = "Who is the prime minister of India?"
   web_search_result = web_search_agent(query)
   print(web_search_result)


.. py:function:: end_tool(query: str) -> str

   Ends the question-answering process.

   :param query: This must be the string "end".
   :return: The string "end".
   :raises ValueError: If the query is not "end".

Recommended Usage:

.. code-block:: python

   query = "end"
   end_response = end_tool(query)
   print(end_response)