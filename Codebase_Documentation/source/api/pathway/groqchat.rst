GroqChat Class
==============
A Pathway-integrated wrapper for Groq Chat services, enabling seamless asynchronous and cached LLM interactions within Pathway data processing pipelines.

Overview
--------
The `GroqChat` class extends `BaseChat` to provide a specialized interface for Groq's chat completion API. It integrates directly with Pathway's reactive framework to support:

- **Asynchronous Execution**: Uses Pathway's async_executor for non-blocking API calls.
- **Caching Mechanisms**: Reduces redundant API calls using configurable cache strategies.
- **Retry Strategies**: Handles failed requests with Pathway's robust retry mechanisms.
- **Native Integration**: Supports Pathway's column expressions and JSON data types for data transformation workflows.
- **Flexible Configuration**: Allows customization of API behavior through Pathway's UDFs.

Initialization
--------------
.. py:class:: GroqChat(capacity=10, retry_strategy=None, cache_strategy=None, model=None, api_key=None, **groq_kwargs)

   Initialize a GroqChat instance for Pathway-integrated workflows.

   :param int capacity: Maximum concurrent API calls (default: 10).
   :param udfs.AsyncRetryStrategy retry_strategy: Strategy for handling failed requests.
   :param udfs.CacheStrategy cache_strategy: Strategy for caching API responses.
   :param str model: Specific Groq model to use (e.g., `'llama-2-70b-chat'`).
   :param str api_key: Groq API key. Defaults to the `GROQ_API_KEY` environment variable.
   :param dict **groq_kwargs: Additional keyword arguments for customizing Groq API calls.

   :raises ValueError: If no API key is provided or discoverable.

Example:
--------
.. code-block:: python

   # Creating a GroqChat instance in a Pathway workflow
   chat = GroqChat(
       capacity=10, 
       model='llama-2-70b-chat', 
       temperature=0.7
   )

Methods
-------
.. py:method:: __wrapped__(messages, **kwargs)

   Core method for executing Groq API calls within Pathway's execution context.

   :param list[dict] | pw.Json messages: Chat messages for the API call. 
      Supports both standard Python lists and Pathway JSON objects.
   :param dict **kwargs: Additional API call configurations.
   :return: Extracted text response from Groq API or `None` if the call fails.
   :rtype: str | None

   **Pathway Integration:**

   - Decodes Pathway JSON objects for API compatibility.
   - Supports seamless integration with Pathway's transformation pipelines.

.. py:method:: __call__(messages, **kwargs)

   Enables direct column-wise transformations in Pathway data streams.

   :param pw.ColumnExpression messages: Pathway column of messages to process.
   :param dict **kwargs: Additional call-specific configurations.
   :return: Transformed column with API responses.
   :rtype: pw.ColumnExpression

   **Pathway Integration:**

   - Converts column expressions directly into API calls.
   - Maintains Pathway's evaluation and streaming semantics.

.. py:method:: _accepts_call_arg(arg_name)

   Validates additional configuration arguments for Groq API calls.

   :param str arg_name: Name of the argument to validate.
   :return: Whether the argument is supported by the Groq API.
   :rtype: bool

Pathway Integration Highlights
------------------------------
- **Async Execution**: Allows non-blocking interactions with Groq APIs.
- **Caching**: Improves efficiency in data-intensive workflows by reusing prior responses.
- **Column Transformations**: Supports direct manipulation of Pathway data streams.
- **Retry Strategies**: Leverages Pathway's retry mechanisms for robust error handling.

Requirements
------------
- Pathway framework installed.
- Groq API key configured via the environment or passed explicitly.
- Compatible Pathway workflows and UDFs for integration.

Error Handling
--------------
Handles:

- Missing API key issues.
- Retryable API call failures.
- Invalid configuration arguments via `_accepts_call_arg`.

Recommended Usage
-----------------
1. Initialize `GroqChat` with desired configurations.
2. Use the `__call__` method to apply transformations directly in Pathway pipelines.
3. Utilize caching and retry strategies to optimize API interactions.