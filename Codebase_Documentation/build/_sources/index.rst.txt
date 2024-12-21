Pathway: Multi-Agent RAG Documentation
======================================

Overview
--------
This multi-agent RAG system autonomously retrieves, analyzes, and synthesizes information from multiple sources, with a memory feature to enhance context retention. A supervisor agent coordinates RAG and other tools, dynamically selecting the best approach for complex queries. It handles simple questions or those requiring reasoning over multiple paragraphs to generate a final response. The system can also create tools spontaneously based on user descriptions, with human-in-the-loop integration and pathway support.

.. toctree::
   :maxdepth: 1
   :caption: Content

   api/pathway_integration
   api/retriever
   api/summary_module
   api/dynamiccacheindex
   api/utilityquerygenerator
   api/ragagent
   api/autoprompt
   api/supervisor
   api/default_tools

Modules
-------

- **Pathway Integration**: enabling seamless data transformation, asynchronous execution, and efficient retrieval and embedding, enhancing dynamic, context-aware processing workflows.
- **Retriever**: offers advanced PDF retrieval and processing capabilities using semantic search techniques
- **Summary Module**: provides document summarization capabilities by chunking large texts and generating concise summaries using the BART transformer model.
- **Dynamic Cache Index**: offers a semantic search and embedding management system designed for efficient, dynamic vector-based HNSW indexing and retrieval
- **Utility Query Generator**: creates unique, single-hop queries for RAG workflows, ensuring relevance and diversity through similarity filtering.
- **RAG Agent**: is designed to process complex queries using a Retrieval-Augmented Generation (RAG) system, integrating thought generation, reasoning, and retrieval with memory management to generate precise, context-aware responses
- **Auto Prompt**: is an intent-based algorithm that dynamically generates tools to create Python code for solving tasks.
- **Supervisor**: handles user queries, using tools and RAG for iterative problem-solving, error handling, and seamless follow-ups
- **Predefined Tools**: provides pre-built tools available for use by the supervisor

Glossary
--------
:ref:`genindex`