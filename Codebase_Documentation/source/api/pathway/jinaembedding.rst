JinaEmbedder Class
==================
Pathway wrapper for Jina's embedding API, enabling seamless integration of Jina embeddings into Pathway workflows.

Overview
--------
The `JinaEmbedder` class serves as a Pathway-compatible wrapper for Jina's embedding API. It provides functionality for embedding text data using Jina's powerful models and is designed to integrate smoothly with Pathway's data processing pipelines.

Features:

- **Customizable Models**: Support for various Jina embedding models.
- **Pathway Integration**: Enables embedding directly in Pathway transformations.
- **Flexible Configuration**: Additional parameters for task-specific embeddings and model initialization.

Initialization
--------------
.. py:class:: JinaEmbedder(model, api_key=None, call_kwargs={}, task="retrieval.passage", **sentencetransformer_kwargs)

   Initialize the embedder with the desired Jina model and configuration.

   :param str model: Model name or path for the Jina embedding model.
   :param str api_key: (Optional) API key for authentication with Jina's service.
   :param dict call_kwargs: (Optional) Additional arguments for embedding calls.
   :param str task: Task to perform with the embedding model (default: "retrieval.passage").
   :param sentencetransformer_kwargs: (Optional) Keyword arguments for initializing SentenceTransformers (if applicable).

   **Example**:

   .. code-block:: python

      from pathway.xpacks.llm import embedders
      embedder = embedders.JinaEmbedder(
          model="your-model-name",
          api_key="your-api-key",
          task="classification"
      )

Methods
-------
**Embedding Execution**
~~~~~~~~~~~~~~~~~~~~~~~
.. py:method:: wrapped(input, **kwargs)

   Embed the input text using the Jina embedding model.

   :param str input: The text to embed.
   :param kwargs: Optional additional arguments for fine-tuning the embedding call.
   :return: The embedding result as a NumPy array.
   :rtype: np.ndarray

   **Example**:

   .. code-block:: python

      import pathway as pw
      embedder = JinaEmbedder(model="your-model-name")
      table = pw.debug.table_from_markdown('''
          | txt |
          |-----|
          | "Hello world" |
          | "Pathway integration with Jina" |
      ''')
      result = table.select(ret=embedder(pw.this.txt))

Pathway Integration
-------------------
- **Table Compatibility**: Easily integrate with Pathway tables for bulk text embedding.
- **Lazy Evaluation**: Supports Pathway's streaming and lazy computation semantics.

Example Usage
-------------
1. **Basic Initialization**:

   .. code-block:: python

      embedder = JinaEmbedder(
          model="jinaai/all-MiniLM-L6-v2",
          api_key="your-api-key",
          task="retrieval.passage"
      )

2. **Pathway Table Embedding**:

   .. code-block:: python

      import pathway as pw
      embedder = JinaEmbedder(model="your-model-name")
      text_table = pw.debug.table_from_markdown('''
          | txt |
          |-----|
          | "Pathway is great for ML workflows" |
          | "Jina embeddings are robust" |
      ''')
      embedded_table = text_table.select(ret=embedder(pw.this.txt))

3. **Fine-Tuning with Additional Parameters**:

   .. code-block:: python

      embedder = JinaEmbedder(
          model="jinaai/all-MiniLM-L6-v2",
          call_kwargs={"normalize": True},
          task="semantic.search"
      )
      embedding = embedder.wrapped("Custom embedding example.")

Error Handling
--------------
Handles:

- Invalid model or API key configuration.
- Issues during embedding calls, ensuring graceful fallback mechanisms.

Dependencies
------------
- **Jina AI Embedding API**: Required for model execution.
- **Pathway**: For integration within data processing pipelines.
- **NumPy**: For handling embedding outputs as arrays.