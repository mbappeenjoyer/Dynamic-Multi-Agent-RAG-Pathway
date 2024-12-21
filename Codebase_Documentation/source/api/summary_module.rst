Summary Module
==============

Overview
--------
The SummaryModule class provides utilities for summarizing text documents using the BART transformer model. It is designed to handle large documents by chunking them into smaller pieces suitable for processing with the model's token limits. The module also supports asynchronous summarization of document clusters.

Initialization
--------------
.. py:class:: SummaryModule(model_name='facebook/bart-large-cnn')

   A module for summarizing text documents using a pre-trained BART model.

   :param str model_name: The name of the pre-trained model to use (default: 'facebook/bart-large-cnn').

Methods
-------
.. py:method:: chunk_document(document)

   Chunk a document into smaller parts while ensuring each part does not exceed the model's token limit.

   :param str document: The document to chunk.
   :return: A nested list where each inner list contains sentences from a single chunk.
   :rtype: List[List[str]]

.. py:method:: generate_summary(nested_sentences)

   Generate summaries for each chunk of text.

   :param List[List[str]] nested_sentences: A nested list of sentences representing the document chunks.
   :return: Summaries for each chunk.
   :rtype: List[str]

.. py:method:: summarize_document(document)

   Summarize an entire document by chunking it and processing each chunk iteratively.

   :param str document: The document to summarize.
   :return: The final combined summary of the document.
   :rtype: str

.. py:method:: generate_summaries(documents_per_cluster)

   Generate summaries for clusters of documents asynchronously.

   :param List[List[BaseNode]] documents_per_cluster: A list of document clusters, where each cluster contains `BaseNode` objects with text.
   :return: A list of summaries, one for each cluster.
   :rtype: List[str]

Recommended Usage
-----------------
.. code-block:: python

   import asyncio

   # Initialize the summary module
   summary_module = SummaryModule()

   # Summarize a single document
   document = "This is a long document that needs summarization."
   summary = summary_module.summarize_document(document)
   print("Summary:", summary)

   # Summarize clusters of documents asynchronously
   documents_per_cluster = [
       [BaseNode("First document in cluster 1"), BaseNode("Second document in cluster 1")],
       [BaseNode("Single document in cluster 2")]
   ]
   summaries = asyncio.run(summary_module.generate_summaries(documents_per_cluster))
   print("Cluster Summaries:", summaries)

Requirements
------------
* torch
* transformers
* nltk

Error Handling
--------------
The class ensures robust handling for:

* Large documents by chunking them into manageable sizes.
* Model token limits during text tokenization and summarization.
* Device compatibility (CPU or GPU).