Utils Module
============

.. automodule:: utils
   :members:
   :undoc-members:
   :show-inheritance:

Environment Variables
---------------------

.. py:data:: groq_api_key
   :annotation:

   API key for Groq services, loaded from environment variables.

.. py:data:: together_api_key
   :annotation:

   API key for Together AI services, loaded from environment variables.

Language Models
---------------

.. py:data:: chat_llm

   ChatGroq language model configuration using Llama 3.1 70b Versatile.

.. py:data:: text_embed_model

   JinaEmbedding model for text embedding, configured for passage retrieval.

.. py:data:: query_embed_model

   JinaEmbedding model for query embedding, configured with specific dimensions.

Prompt Templates
----------------

.. py:data:: thought_agent_prompt

   ChatPromptTemplate for the Thought Generating Agent.

.. py:data:: reasoning_agent_prompt

   ChatPromptTemplate for the Reasoning Agent.

Utility Functions
-----------------

.. py:function:: llm_response_if_memory_hit_found(query: str, chunk: str) -> Optional[str]

   Generate a response from a given query and context chunk using the chat language model.

   :param query: The input query to be answered
   :param chunk: The context chunk containing potential answer information
   :return: A generated response or None if insufficient context