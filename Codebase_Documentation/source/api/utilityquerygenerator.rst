Utility Query Generator
=======================

Overview
--------
The UtilityQueryGenerator class generates concise, unique single-hop queries for data chunks, ideal for Retrieval-Augmented Generation (RAG) workflows. It ensures relevance and avoids redundancy through similarity-based filtering, enriching graph memory with diverse potential user queries.

Initialization
--------------
.. py:class:: UtilityQueryGenerator(llm, embedding_model, similarity_threshold=0.8)

   :param llm: The language model used for query generation.
   :type llm: Object
   :param embedding_model: The model used to calculate query embeddings.
   :type embedding_model: Object
   :param float similarity_threshold: Threshold for query uniqueness (default: 0.8).

Methods
-------
.. py:method:: generate_queries(chunk, max_retries=3, existing_graph_queries=None, max_queries=3)

   Generate distinct and relevant queries from the provided data chunk.

   :param str chunk: Text chunk for which queries are generated.
   :param int max_retries: Maximum retries in case of generation errors (default: 3).
   :param List[str] existing_graph_queries: Existing queries to ensure uniqueness (default: None).
   :param int max_queries: Maximum number of queries to generate (default: 3).
   :return: List of generated queries.
   :rtype: List[str]

Recommended Usage:

   .. code-block:: python

      generator = UtilityQueryGenerator(llm, embedding_model)
      queries = generator.generate_queries("Sample data chunk", max_queries=3)

.. py:method:: parse_json_response(response)

   Parse and validate JSON responses from the LLM with fallback strategies.

   :param str response: Raw JSON response from the LLM.
   :return: Parsed JSON object or an empty dictionary if parsing fails.
   :rtype: dict

.. py:method:: calculate_query_similarity(query1, query2)

   Calculate cosine similarity between two queries using embeddings.

   :param str query1: First query.
   :param str query2: Second query.
   :return: Cosine similarity score.
   :rtype: float

Recommended Usage:

   .. code-block:: python

      similarity = generator.calculate_query_similarity("query 1 text", "query 2 text")

.. py:method:: filter_queries(queries, existing_graph_queries)

   Filter queries to remove duplicates based on similarity threshold.

   :param List[str] queries: List of generated queries.
   :param List[str] existing_graph_queries: Existing queries to compare for uniqueness.
   :return: Filtered list of unique queries.
   :rtype: List[str]

Error Handling
--------------
The UtilityQueryGenerator class implements robust error handling for:

* Invalid JSON responses from the LLM.
* Similarity calculation issues.
* Query generation retries up to a configurable maximum.

Requirements
------------
* numpy
* json
* re
* A compatible LLM for query generation
* An embedding model
