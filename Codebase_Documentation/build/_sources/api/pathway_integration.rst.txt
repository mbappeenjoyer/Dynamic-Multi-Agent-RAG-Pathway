Pathway Integration
===================

Overview
--------
Pathway is a high-performance, low-latency data processing framework designed to efficiently handle live data and streaming. Our integration optimizes the orchestration of AI-powered tasks, including seamless data transformation, asynchronous execution, and the retrieval and embedding of information. By embedding advanced models such as Groq Chat, Jina Embedding, and Raptor Retriever into Pathway's ecosystem, we enable smooth interactions between components, creating flexible and context-aware workflows for rapid processing. The integration also supports distributed operations, caching, and real-time data processing, providing the tools to effortlessly build scalable and intelligent applications that adapt to dynamic requirements.

.. toctree::
   :maxdepth: 1
   :caption: Content

   pathway/groqchat
   pathway/jinaembedding
   pathway/InterleavedRAGQuestionAnswerer
   pathway/CodeAndReasoningAgent
   pathway/RaptorRetriever
   
Modules
-------

- **Groq Chat**: A Pathway-integrated wrapper for Groq's chat API, enabling seamless asynchronous interactions and caching mechanisms for efficient LLM-based communication within Pathway workflows.
- **Jina Embedding**: Pathway wrapper for Jina's embedding API, allowing users to leverage powerful, scalable embedding models for text and document processing within the Pathway framework.
- **Interleaved RAG Question Answerer**: An advanced retrieval-augmented generation (RAG) model in Pathway, utilizing dynamic retrieval and reasoning for adaptive question-answering across multiple knowledge sources.
- **Code And Reasoning Agent**: A Pathway-enabled agent that integrates code generation and error reflection, providing robust tool management and dynamic reasoning capabilities for executing tasks and refining agent responses.
- **Raptor Retriever**: A hierarchical document retrieval system that supports adaptive retrieval modes and flexible metadata-based filtering, optimizing search operations in Pathway’s distributed data framework.

Glossary
--------
:ref:`genindex`