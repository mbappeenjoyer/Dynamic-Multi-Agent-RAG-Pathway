Dynamic Cache Index
===================

Overview
--------
The DynamicCacheIndex is a semantic search and embedding management system designed for efficient, dynamic vector-based indexing and retrieval. It makes use of the HNSW (Hierarchical Navigable Small World) indexing for high-performance nearest neighbor searches. HNSW maintains a graph-like structure, where nodes represent data points and edges connect neighbors, enabling dense multi-hop relations and retrieval, making it ideal for creating a memory system for Retrieval-Augmented Generation (RAG).

Initialization
--------------
.. py:class:: DynamicCacheIndex(dim=768, index_type='hnsw', space='cosinesimil', batch_size=32)
    Advanced semantic search and embedding cache management system.
    :param int dim: Embedding vector dimensionality (default: 768)
    :param str index_type: Type of index (default: 'hnsw')
    :param str space: Similarity space metric (default: 'cosinesimil')
    :param int batch_size: Number of embeddings to process per batch (default: 32)

Methods
---------
.. py:method:: add_chunk(chunk, query_metadata=None)

   Add a text chunk to the semantic index.

   :param str chunk: Text chunk to be indexed
   :param query_metadata: Optional metadata associated with the chunk
   :type query_metadata: str or dict, optional
   :return: Unique identifier for the added chunk
   :rtype: int or None

.. py:method:: search(query_vector, k=5)

   Perform semantic similarity search in the index.

   :param numpy.ndarray query_vector: Embedding vector to search against
   :param int k: Number of top similar results to retrieve (default: 5)
   :return: List of search results with chunk ID, distance, and metadata
   :rtype: list of (int, float, dict)

.. py:method:: query_and_cache(query, threshold=0.8, k=5)

   Execute a semantic search with intelligent caching.

   :param str query: Text query to search
   :param float threshold: Similarity threshold for caching (default: 0.8)
   :param int k: Number of top results to retrieve (default: 5)
   :return: List of search results
   :rtype: list of (int, float, dict) or None

.. py:method:: save_index(filename, save_data=True)

   Save the current index and metadata to disk.

   :param str filename: Base filename for saving
   :param bool save_data: Whether to save additional index data (default: True)

.. py:method:: load_index(filename)

   Load a previously saved index and metadata.

   :param str filename: Base filename of the index to load

.. py:method:: get_neighbors(chunk_id, k=5)

   Retrieve nearest neighbors for a specific chunk.

   :param int chunk_id: Unique identifier of the chunk
   :param int k: Number of neighbors to retrieve (default: 5)
   :return: Tuple of neighbor IDs and their distances
   :rtype: tuple

Recommended Usage
-----------------

.. code-block:: python

   # Initialize the dynamic cache index
   index = DynamicCacheIndex(dim=1064, batch_size=8)

   # Add chunks to the index
   index.add_chunk("Sample text chunk", {"query": "sample query"})
   index.add_chunk("Another text chunk", {"query": "another sample query"})

   # Perform a semantic search
   query = "Relevant information search"
   results = index.query_and_cache(query)

   # Save and load index
   index.save_index("my_semantic_index")
   index.load_index("my_semantic_index")

Requirements
------------

* numpy
* nmslib
* llama_index
* tqdm
* llama-index-embeddings-jinaai

Error Handling
--------------

The class includes comprehensive error handling for:

* Embedding model initialization
* Dimension mismatches
* Batch processing
* Index creation and searching