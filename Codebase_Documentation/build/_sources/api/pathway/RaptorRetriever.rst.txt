RaptorRetriever Class
======================
An advanced hierarchical document retrieval system utilizing the Raptor indexing technique. Designed for high-performance, adaptive retrieval in Pathway-integrated workflows.

Overview
--------
The `RaptorRetriever` class provides multi-level document abstraction and retrieval using hierarchical clustering. It integrates with Pathway's vector store client for distributed and metadata-driven document search.

Key Features:

- **Hierarchical Retrieval**: Multi-level abstraction using tree traversal or collapsed retrieval.
- **Dynamic Embedding**: Supports embedding and summarization modules for adaptive indexing.
- **Pathway Integration**: Streaming data ingestion, distributed retrieval, and seamless JSON-based operations.

Initialization
--------------
.. py:class:: RaptorRetriever(documents, tree_depth=3, similarity_top_k=2, mode="collapsed", **kwargs)

   Initialize the retriever with configurable parameters for indexing and retrieval.

   :param List[BaseNode] documents: Initial set of documents for indexing.
   :param int tree_depth: Number of hierarchical abstraction levels (default: 3).
   :param int similarity_top_k: Number of top-k documents to retrieve (default: 2).
   :param QueryModes mode: Retrieval strategy, either `'collapsed'` or `'tree_traversal'`.
   :param Optional[LLM] llm: Optional language model for summarization.
   :param Optional[BaseEmbedding] embed_model: Embedding model for vectorization.
   :param Optional[BasePydanticVectorStore] vector_store: Pathway vector store for retrieval.
   :param Optional[List[TransformComponent]] transformations: List of document transformation components.
   :param Optional[SummaryModule] summary_module: Module for summarization tasks.
   :param Optional[VectorStoreIndex] existing_index: Pre-existing vector store index.
   :raises ValueError: If required parameters are missing or misconfigured.

   **Pathway Integration Highlights**:

   - Connects with Pathway's vector store server.
   - Supports streaming JSON data ingestion for indexing.

Methods
-------
**Asynchronous Methods**
~~~~~~~~~~~~~~~~~~~~~~~~~
.. py:method:: insert(documents)

   Recursively insert and abstract documents into a hierarchical index.

   :param List[BaseNode] documents: Documents to insert and abstract.
   :rtype: None

   **Pathway Integration**:

   - Embeddings are generated and clustered.
   - Nodes are summarized and stored in the Pathway vector store.

.. py:method:: collapsed_retrieval(query_str)

   Perform direct similarity search in a flattened index.

   :param str query_str: Search query string.
   :return: Top-k retrieved documents.
   :rtype: Response

   **Pathway Integration**:

   - Leverages Pathway vector store for direct similarity searches.

.. py:method:: tree_traversal_retrieval(query_str)

   Perform hierarchical retrieval through tree traversal.

   :param str query_str: Search query string.
   :return: Hierarchically retrieved documents.
   :rtype: Response

   **Pathway Integration**:

   - Metadata filtering and multi-level retrieval using Pathway's client.

**Utility Methods**
~~~~~~~~~~~~~~~~~~~
.. py:method:: _get_embeddings_per_level(level=0)

   Retrieve embeddings for nodes at a specific abstraction level.

   :param int level: Target abstraction level (default: 0 for leaf nodes).
   :return: Embeddings of nodes at the specified level.
   :rtype: List[float]

.. py:method:: retrieve(query_str_or_bundle, mode=None)

   Synchronous document retrieval based on query and mode.

   :param QueryType query_str_or_bundle: Query string or bundle.
   :param QueryModes mode: Retrieval mode (`'collapsed'` or `'tree_traversal'`).
   :return: Retrieved documents with relevance scores.
   :rtype: List[NodeWithScore]

.. py:method:: aretrieve(query_str_or_bundle, mode=None)

   Asynchronous document retrieval based on query and mode.

   :param QueryType query_str_or_bundle: Query string or bundle.
   :param QueryModes mode: Retrieval mode (`'collapsed'` or `'tree_traversal'`).
   :return: Retrieved documents with relevance scores.
   :rtype: List[NodeWithScore]

.. py:method:: persist(persist_dir)

   Save the current index to a specified directory.

   :param str persist_dir: Directory path for storing the index.
   :rtype: None

.. py:classmethod:: from_persist_dir(cls, persist_dir, embed_model=None, **kwargs)

   Load a persisted index from a directory and create a new instance.

   :param str persist_dir: Directory containing the saved index.
   :param Optional[BaseEmbedding] embed_model: Embedding model for the index.
   :return: RaptorRetriever instance with the loaded index.
   :rtype: RaptorRetriever

Pathway Integration Highlights
------------------------------
- **Distributed Retrieval**: Uses Pathway's vector store for high-performance searches.
- **Metadata Filtering**: Enables fine-grained control over document selection.
- **Streaming Data Ingestion**: Direct JSON data ingestion for dynamic updates.

Use Cases
---------
1. **Hierarchical Search**: Retrieve contextually similar documents using multi-level clustering.
2. **Metadata-Based Filtering**: Perform targeted searches with embedded metadata.
3. **Dynamic Summarization**: Integrate summarization and embedding for adaptive retrieval workflows.

Error Handling
--------------
Handles:

- Missing or incompatible parameters during initialization.
- Errors during hierarchical document abstraction or embedding.
- Pathway client connectivity issues during retrieval.

Example Usage
-------------
.. code-block:: python

   # Initialize RaptorRetriever with hierarchical indexing
   retriever = RaptorRetriever(
       documents=my_documents,
       tree_depth=4,
       similarity_top_k=3,
       mode="tree_traversal"
   )

   # Perform asynchronous retrieval
   response = await retriever.collapsed_retrieval(query_str="How does quantitative easing (QE) work?")