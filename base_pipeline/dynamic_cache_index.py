import nmslib
from typing import List, Dict, Tuple, Optional
import json
from tqdm import tqdm
import numpy as np
from llama_index.embeddings.jinaai import JinaEmbedding
import os

class DynamicCacheIndex:
    def __init__(self,
                 dim: int = 768,
                 index_type: str = 'hnsw',
                 space: str = 'cosinesimil',
                 batch_size: int = 32):
        
        """
            Initialize a Dynamic Cache Index for efficient semantic searching and embedding storage.

            Args:
                dim (int, optional): Dimensionality of the embedding vectors. Defaults to 768.
                index_type (str, optional): Type of index to use. Defaults to 'hnsw'.
                space (str, optional): Similarity space metric for distance calculation. 
                                        Defaults to 'cosinesimil' (cosine similarity).
                batch_size (int, optional): Number of embeddings to process in a single batch. 
                                            Defaults to 32.

            Attributes:
                dim (int): Dimension of embeddings
                batch_size (int): Batch size for processing embeddings
                metadata (dict): Storage for metadata associated with embeddings
                embeddings (list): List of stored embedding vectors
                id_counter (int): Unique identifier for each embedding
                index_created (bool): Flag indicating if the index has been created
                pending_additions (list): Temporary storage for embeddings to be added
                text_embed_model (object): Embedding model for text conversion

            Raises:
                ValueError: If initialization of the embedding model fails
        """
        self.dim = dim
        self.batch_size = batch_size
        self.metadata = {}
        self.embeddings = []
        self.id_counter = 0
        self.index_created = False
        self.pending_additions = []
        self.text_embed_model = None

        # Initializing the HNSW index
        self.index = nmslib.init(method=index_type, space=space)

        # Initializing the embedding model
        if not self.text_embed_model:
          try:
              self._init_embedding_model()
          except Exception as e:
              print("Failed to initialize embedding model during retry: ", e)

    def _init_embedding_model(self) -> None:
        """Initialize the embedding model with error handling"""
        try:
            jina_api_key = os.getenv("JINAAI_API_KEY")
            if not jina_api_key:
                raise ValueError("JINAAI_API_KEY environment variable not set")

            self.text_embed_model = JinaEmbedding(
                api_key=jina_api_key,
                model="jina-embeddings-v3",
            )
        except Exception as e:
            print(f"Failed to initialize embedding model: {e}")
            raise

    def process_pending_additions(self, force=False) -> bool:
        """
        Process and add pending embeddings to the HNSW index in batches.

        Args:
            force (bool, optional): Force processing even if batch is not full. 
                                    Defaults to False.

        Returns:
            bool: True if processing is successful, False otherwise

        Raises:
            ValueError: If embedding dimension is incorrect
        """
        if not self.pending_additions and not force:
            return False

        try:
            batches = [self.pending_additions[i:i + self.batch_size]
                      for i in range(0, len(self.pending_additions), self.batch_size)]

            with tqdm(total=len(batches), desc="Processing batches") as pbar:
                for batch in batches:
                    for embedding, metadata in batch:
                        if not isinstance(embedding, np.ndarray):
                            embedding = np.array(embedding)

                        if embedding.shape[0] != self.dim:
                            raise ValueError(f"Embedding dimension mismatch. Expected {self.dim}, got {embedding.shape[0]}")

                        self.index.addDataPoint(self.id_counter, embedding)
                        self.metadata[self.id_counter] = metadata
                        self.embeddings.append(embedding)
                        self.id_counter += 1
                    pbar.update(1)

            # Clear pending additions
            self.pending_additions = []

            # Recreate index with progress tracking
            print("Creating index...")
            self.index.createIndex(
                {'post': 2},
                print_progress=True
            )
            self.index_created = True
            print("Index updated successfully")
            return True

        except Exception as e:
            print(f"Error processing pending additions: {e}")
            return False

    def add_chunk(self, chunk: str, query_metadata: str = None) -> Optional[int]:
        """
        Add a text chunk to the dynamic cache index with embedded representation.

        Args:
            chunk (str): Text chunk to be embedded and indexed
            query_metadata (str, optional): Metadata associated with the chunk, 
                                            can be JSON string or dictionary

        Returns:
            Optional[int]: Unique identifier for the added chunk, or None if addition fails

        Raises:
            ValueError: For invalid embedding format or dimension mismatch
        """
        if not chunk:
            print("Empty chunk")
            return None

        try:
            if not self.text_embed_model:
                self._init_embedding_model()

            chunk_str = str(chunk)

            metadata = {}
            if query_metadata:
                try:
                    # Try to parse the metadata if it's a JSON string
                    if isinstance(query_metadata, str):
                        metadata = json.loads(query_metadata)
                    elif isinstance(query_metadata, dict):
                        metadata = query_metadata
                    else:
                        metadata = {'original_metadata': query_metadata}
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, store as is
                    metadata = {'original_metadata': query_metadata}

            if 'chunk' not in metadata:
                metadata['chunk'] = chunk_str

            chunk_embedding = self.text_embed_model.get_text_embedding(chunk_str)

            if not isinstance(chunk_embedding, (list, np.ndarray)):
                raise ValueError("Invalid embedding format")

            if isinstance(chunk_embedding, list):
                chunk_embedding = np.array(chunk_embedding)

            # Validate embedding dimension
            if chunk_embedding.shape[0] != self.dim:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.dim}, got {chunk_embedding.shape[0]}")

            self.pending_additions.append((
                chunk_embedding,
                metadata
            ))

            # Process if batch size reached
            if len(self.pending_additions) >= self.batch_size:
                self.process_pending_additions()

            return self.id_counter

        except Exception as e:
            print(f"Error adding chunk: {e}")
            return None

    def search(self,
              query_vector: np.ndarray,
              k: int = 5) -> List[Tuple[int, float, Dict]]:
        """
        Perform a k-nearest neighbors search on the HNSW index.

        Args:
            query_vector (np.ndarray): Embedding vector to search against the index
            k (int, optional): Number of top neighbors to retrieve. Defaults to 5.

        Returns:
            List[Tuple[int, float, Dict]]: A list of tuples containing:
                - Chunk ID
                - Distance/similarity score
                - Metadata dictionary

        Raises:
            Exception: For any errors during the search process
        """
        if not isinstance(query_vector, np.ndarray):
            try:
                query_vector = np.array(query_vector)
            except Exception as e:
                print(f"Failed to convert query vector to numpy array: {e}")
                return []

        if query_vector.shape[0] != self.dim:
            print(f"Query vector dimension mismatch. Expected {self.dim}, got {query_vector.shape[0]}")
            return []

        try:
            # Process any pending additions
            if self.pending_additions:
                if not self.process_pending_additions():
                    print("Failed to process pending additions")
                    return []

            if not self.index_created or len(self.embeddings) == 0:
                print("Index not created or empty")
                return []

            k = min(k, len(self.embeddings))
            ids, distances = self.index.knnQuery(query_vector, k=k) # retrieves the closest node and top k neighbours in the graph

            results = []
            for i, chunk_id in enumerate(ids):
                metadata = self.metadata.get(int(chunk_id), {})

                result_metadata = {
                    'query': metadata.get('query', 'No query found'),
                    'chunk': metadata.get('chunk', 'No chunk found'),
                    'query_type': metadata.get('query_type', 'unknown'),
                    'original_metadata': metadata
                }

                results.append((
                    int(chunk_id),
                    float(distances[i]),
                    result_metadata
                ))

            return results

        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def save_index(self, filename: str, save_data: bool = True) -> None:
        """
        Save the current index and its associated metadata to disk.

        Args:
            filename (str): Base filename for saving the index
            save_data (bool, optional): Whether to save additional index data. 
                                        Defaults to True.

        Raises:
            Exception: If there are issues during index or metadata saving
        """
        try:
            self.index.saveIndex(filename, save_data)

            metadata_file = f"{filename}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump({str(k): v for k, v in self.metadata.items()}, f)

            print(f"Index saved to {filename}")
            print(f"Metadata saved to {metadata_file}")

        except Exception as e:
            print(f"Error saving index: {e}")
            raise

    def load_index(self, filename: str) -> None:
        """
        Load a previously saved index and its metadata from disk.

        Args:
            filename (str): Base filename of the index to be loaded

        Raises:
            Exception: If there are issues during index or metadata loading
        """
        try:
            self.index.loadIndex(filename)

            metadata_file = f"{filename}_metadata.json"
            with open(metadata_file, 'r') as f:
                self.metadata = {int(k): v for k, v in json.load(f).items()}

            self.index_created = True
            print(f"Index loaded from {filename}")
            print(f"Metadata loaded from {metadata_file}")

        except Exception as e:
            print(f"Error loading index: {e}")
            raise

    def query_and_cache(self, query: str, threshold: float = 0.8, k: int = 5) -> Optional[List[Tuple[int, float, Dict]]]:
        """
        Execute a semantic search query and retrieve cached or similar results.

        Args:
            query (str): Text query to search in the index
            threshold (float, optional): Similarity threshold for caching. Defaults to 0.8.
            k (int, optional): Number of top results to retrieve. Defaults to 5.

        Returns:
            Optional[List[Tuple[int, float, Dict]]]: List of search results with 
            chunk ID, similarity score, and metadata, or None if no results found

        Raises:
            Exception: For any errors during query processing
        """
        try:
            if not self.text_embed_model:
                self._init_embedding_model()

            query_embedding = self.text_embed_model.get_text_embedding(query)

            results = self.search(query_embedding, k)

            if not results:
                print(f"No results found for query: {query}")
                return None

            parsed_results = []
            for id, distance, metadata in results:
                try:
                    if isinstance(metadata, str):
                        metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    pass
                parsed_results.append((id, distance, metadata))
            return parsed_results

        except Exception as e:
            print(f"Error in query_and_cache: {e}")
            return None

    def get_neighbors(self, chunk_id, k=5):
        """
        Retrieve nearest neighbors for a specific chunk in the HNSW index.

        Args:
            chunk_id (int): Unique identifier of the chunk to find neighbors for
            k (int, optional): Number of neighbors to retrieve. Defaults to 5.

        Returns:
            Tuple: 
                - neighbors (array): IDs of neighboring chunks
                - distances (array): Distances/similarities to those neighbors
        """
        neighbors, distances = self.index.knnQuery(self.embeddings[chunk_id], k=k)
        return neighbors, distances