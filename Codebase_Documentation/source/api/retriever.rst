Retriever
=========

Overview
--------
The Retriever is a document information retrieval pipeline designed to extract, embed, and search through document content with high precision and efficiency.

Functions
---------

.. py:function:: retriever(path: str, query: str, top_k: int) -> RaptorRetriever

   Main function to perform advanced document retrieval.

   :param path: Path to the PDF document
   :param query: Semantic search query
   :param top_k: Number of top results to retrieve
   :return: Configured Raptor Retriever instance for document search
   :raises FileNotFoundError: If PDF file is not found
   :raises ValueError: If query is empty or top_k is invalid

.. py:function:: table_summary(html_code: str) -> str

   Summarize table data for efficient retrieval.

   :param html_code: HTML representation of the table
   :return: Concise, retrieval-optimized table summary
   :rtype: str

Recommended Usage
-----------------

.. code-block:: python

   # Basic retrieval example
   query_engine = retriever('document.pdf', 'research methodology', top_k=3)
   response = query_engine.query("Summarize key findings")