from typing import List
import json
import re
import numpy as np
import traceback

def create_utility_query_prompt(template=None, number=3, data=None):
    """
    Create a dynamic utility query generation prompt.

    Args:
        template (str, optional): Custom template for query generation. Defaults to None.
        number (int): Number of queries to generate. Defaults to 3.
        data (str): The data chunk for which queries are generated. Defaults to None.

    Returns:
        str: Formatted prompt string ready for query generation.
    """
    default_template = f"""You are an expert query generator agent. Given the data below, generate {number} distinct queries. Ensure each query is:
1. Single-hop (focuses on one specific aspect)
2. Clear and concise
3. Unique and relevant
4. All queries should have a clear and direct answer in the data, it shouldn't be ambiguous.

Respond STRICTLY in this EXACT JSON format:
{{
    "query_1": "First query text here",
    "query_2": "First query text here",
    "query_3": "First query text here"
}}

DATA:
{data}

Your Response:"""

    if template:
        return template.format(data=data)
    return default_template

class UtilityQueryGenerator:
    """
    A class for generating, filtering, and managing utility queries based on data chunks.

    Attributes:
        llm (object): Language model object used for generating queries.
        embedding_model (object): Model for calculating text embeddings.
        similarity_threshold (float): Threshold for determining query similarity.
    """

    def __init__(self, llm, embedding_model, similarity_threshold=0.8):
        """
        Initialize the UtilityQueryGenerator with LLM and embedding model.

        Args:
            llm (object): Language model instance.
            embedding_model (object): Embedding model instance.
            similarity_threshold (float): Similarity threshold for query filtering. Defaults to 0.8.
        """
        self.llm = llm
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold

    def generate_queries(self, chunk: str, max_retries: int = 1,
                         existing_graph_queries: List[str] = None,
                         max_queries: int = 3) -> List[str]:
        """
        Generate distinct and relevant queries based on the given data chunk.

        Args:
            chunk (str): Data chunk for which queries are generated.
            max_retries (int): Maximum number of retries for generating queries. Defaults to 3.
            existing_graph_queries (List[str], optional): Existing queries to filter against. Defaults to None.
            max_queries (int): Maximum number of queries to generate. Defaults to 3.

        Returns:
            List[str]: Filtered list of generated queries.
        """
        print(f"\nGenerating Utility Queries for Chunk (length: {len(chunk)}):")
        existing_graph_queries = existing_graph_queries or []

        for attempt in range(max_retries):
            try:
                truncated_chunk = chunk[:1000] + "..." if len(chunk) > 1000 else chunk
                print(f"  Attempt {attempt + 1}: Generating up to {max_queries} queries")

                formatted_prompt = create_utility_query_prompt(
                    number=max_queries,
                    data=truncated_chunk
                )

                response = self.llm.invoke(formatted_prompt).content

                try:
                    queries_dict = json.loads(response)
                except json.JSONDecodeError:
                    queries_dict = self.parse_json_response(response)

                potential_queries = [
                    queries_dict.get(f"query_{i}", "").strip()
                    for i in range(1, max_queries + 1)
                    if queries_dict.get(f"query_{i}")
                ]

                if not potential_queries:
                    continue

                filtered_queries = self.filter_queries(potential_queries, existing_graph_queries)

                print("Generated Queries:")
                for q in filtered_queries:
                    print(f"    - {q}")

                return filtered_queries

            except Exception as e:
                print(f" Query Generation Error (Attempt {attempt + 1}): {traceback.format_exc()}")

        print("Failed to generate utility queries after max retries")
        return []

    def parse_json_response(self, response):
        """
        Parse JSON response robustly with multiple fallback strategies.

        Args:
            response (str): Response from the LLM.

        Returns:
            dict: Parsed JSON object, or empty dictionary if parsing fails.
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

        try:
            cleaned_response = response.strip()
            cleaned_response = cleaned_response.replace("'", '"')
            cleaned_response = re.sub(r'(\w+):', r'"\1":', cleaned_response)
            return json.loads(cleaned_response)
        except Exception:
            print("Failed to parse JSON response")
            return {}

    def calculate_query_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate cosine similarity between two queries using embeddings.

        Args:
            query1 (str): First query text.
            query2 (str): Second query text.

        Returns:
            float: Cosine similarity between the two queries.
        """
        try:
            emb1 = self.embedding_model.get_text_embedding(query1)
            emb2 = self.embedding_model.get_text_embedding(query2)

            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)

            return dot_product / (norm1 * norm2)
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0

    def filter_queries(self, queries: List[str], existing_graph_queries: List[str]) -> List[str]:
        """
        Filter queries to ensure uniqueness and relevance.

        Args:
            queries (List[str]): List of generated queries.
            existing_graph_queries (List[str]): Existing queries to filter against.

        Returns:
            List[str]: Filtered list of unique queries.
        """
        print("\nQuery Filtering Process:")
        filtered_queries = []

        for query in queries:
            if not query:
                continue

            is_unique = True
            for graph_query in existing_graph_queries:
                similarity = self.calculate_query_similarity(query, graph_query)
                if similarity > self.similarity_threshold:
                    is_unique = False
                    break

            if is_unique:
                for filtered_query in filtered_queries:
                    similarity = self.calculate_query_similarity(query, filtered_query)
                    if similarity > self.similarity_threshold:
                        is_unique = False
                        break

            if is_unique:
                filtered_queries.append(query)
                print(f"Accepted query: {query}")

        return filtered_queries