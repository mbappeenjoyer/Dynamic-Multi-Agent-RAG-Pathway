import re
import random
from dynamic_cache_index import DynamicCacheIndex
from utility_query_generator import UtilityQueryGenerator
from datetime import datetime
import numpy as np
from tqdm import tqdm
from utils import rephrase_prompt, jargon_prompt, text_embed_model, chat_llm1, llm
import os
import fitz
import faiss
import time
from retriever import table_summary, image_summary
from llama_index.core import Document
from utils import client_unstructured, query_embed_model, chat_llm1
from unstructured_client.models import operations, shared
import json
from PyPDF2 import PdfReader, PdfWriter
from llama_index.core.query_engine import RetrieverQueryEngine

class RAGAGENT:
    def __init__(self,
                 llm=chat_llm1,
                 embedding_dim=1024,
                 thought_agent_prompt=None,
                 reasoning_agent_prompt=None,
                 retrieval_agent_prompt=None,
                 utility_query_template=None,
                 max_steps=15,
                 similarity_threshold=0.8,
                 retriever = None,
                 path = None):

        if path == None:
          raise ValueError("Value of Path Is No provided")
        """
        Initialize the RAG agent with necessary configurations.

        Args:
            llm (object): The language model used for query generation and processing.
            embedding_dim (int): Dimension of the embedding vectors. Default is 1024.
            thought_agent_prompt (str, optional): Prompt for the thought agent.
            reasoning_agent_prompt (str, optional): Prompt for the reasoning agent.
            retrieval_agent_prompt (str, optional): Prompt for the retrieval agent.
            utility_query_template (str, optional): Template for generating utility queries.
            max_steps (int): Maximum steps for processing a query. Default is 15.
            similarity_threshold (float): Threshold for memory similarity. Default is 0.8.
        """
        self.embedding_dim = embedding_dim
        self.cache_index = DynamicCacheIndex(dim=embedding_dim, batch_size=16)
        self.thought_agent_prompt = thought_agent_prompt
        self.retrieval_agent_prompt = retrieval_agent_prompt
        self.reasoning_agent_prompt = reasoning_agent_prompt
        self.max_steps = max_steps
        self.llm = llm
        self.path = path
        self.retriever = retriever
        self.engine = None
        self.page_num = []
        self.similarity_threshold = similarity_threshold
        self.utility_query_template = utility_query_template
        self.utility_query_generator = UtilityQueryGenerator(llm=chat_llm1, embedding_model=text_embed_model, similarity_threshold=0.8)
        self.previous_queries = {} 
        self.__reset_agent()
        self.text_embed_model = text_embed_model
        
    def check_memory_and_retrieve(self, query):
        """
        Check if a query exists in memory and retrieve the best match based on similarity.

        Args:
            query (str): The query string to search in memory.

        Returns:
            str: The best matching chunk from memory, or None if no match is found.
        """
        try:
            if not query:
                return None

            self.previous_queries[query] = self.previous_queries.get(query, 0) + 1

            if self.previous_queries[query] > 2:
                print(f"Query repeated too many times: {query}")
                return "FORCE_REASONING"

            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return None

            results = self.cache_index.search(query_embedding, k=5)
            if not results:
                return None

            best_match = None
            best_distance = float('inf')

            MAX_DISTANCE = 0.3

            for id, distance, metadata in results:
                if distance < self.similarity_threshold and distance < best_distance and distance < MAX_DISTANCE:
                    chunk = metadata.get('chunk', '')
                    if chunk:
                        best_match = chunk
                        best_distance = distance
            if best_match:
                print(f"Memory hit found with distance {best_distance:.3f}")
                return best_match

            return None

        except Exception as e:
            print(f"Error in memory check: {e}")
            return None

    def check_memory_and_retrieve_for_supervisor(self, query):
        """
        Retrieve the best match for a query from memory for supervisory tasks.

        Args:
            query (str): The query string to search in memory.

        Returns:
            str: The best matching chunk, or None if no match is found.
        """
        try:
            if not query:
                return None

            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return None

            results = self.cache_index.search(query_embedding, k=5)
            if not results:
                return None

            best_match = None
            best_distance = float('inf')

            for id, distance, metadata in results:
                if distance < self.similarity_threshold and distance < best_distance:
                    chunk = metadata.get('chunk', '')
                    if chunk:
                        best_match = chunk
                        best_distance = distance
            if best_match:
                print(f"Memory hit found with distance {best_distance:.3f}")
                print(f"DEBUG:{best_match}")
                return best_match

            return None

        except Exception as e:
            print(f"Error in memory check: {e}")
            return None

    def add_to_memory(self, query, chunk, query_type='original',
                      original_query=None, metadata=None):
        """
        Add a query and its associated chunk to memory with metadata.

        Args:
            query (str): The query string.
            chunk (str): The chunk of data to store.
            query_type (str, optional): The type of query (e.g., 'original', 'retrieval'). Default is 'original'.
            original_query (str, optional): The original query string.
            metadata (dict, optional): Additional metadata to associate with the chunk.

        Returns:
            bool: True if the chunk was successfully added, False otherwise.
        """
        try:
            full_metadata = {
                'query': query,
                'query_type': query_type,
                'original_query': original_query or query,
                'chunk': chunk,
                'timestamp': datetime.now().isoformat()
            }

            if metadata:
                full_metadata.update(metadata)

            print("DEBUG: Attempting to add chunk with metadata:")
            print(full_metadata)

            chunk_id = self.cache_index.add_chunk(chunk, full_metadata)

            if chunk_id is not None:
                print(f"✅ Added to memory: {query} (Type: {query_type})")
                print(f"DEBUG: Chunk ID: {chunk_id}")
                return True
            else:
                print(f"❌ Failed to add to memory: {query}")
                return False

        except Exception as e:
            print(f"Memory addition error: {e}")
            return False

    def get_existing_graph_queries(self):
        """
        Retrieve all existing graph queries from the memory cache.

        Returns:
            list: A list of query strings stored in memory.
        """
        return [
            metadata.get('query', '')
            for metadata in self.cache_index.metadata.values()
            if 'query' in metadata
        ]

    def generate_utility_queries(self, chunk, max_queries,existing_graph_queries):
        """
        Generate utility queries for a given data chunk.

        Args:
            chunk (str): The data chunk for generating queries.
            max_queries (int): Maximum number of queries to generate.
            existing_graph_queries (list): List of existing graph queries to avoid duplicates.

        Returns:
            list: Generated utility queries.
        """
        return self.utility_query_generator.generate_queries(chunk,max_queries,existing_graph_queries)

    def get_embedding(self, text):
        """
        Generate an embedding vector for a given text.

        Args:
            text (str): The input text for which to generate an embedding.

        Returns:
            np.ndarray: The generated embedding vector, or None if an error occurs.
        """
        try:
            embedding = self.cache_index.text_embed_model.get_text_embedding(text)
            if isinstance(embedding, list):
                embedding = np.array(embedding)

            # Ensure embedding matches cache index dimension
            if embedding.shape[0] != self.embedding_dim:
                print(f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {embedding.shape[0]}")

                # Truncate or pad to match expected dimension
                if embedding.shape[0] > self.embedding_dim:
                    embedding = embedding[:self.embedding_dim]
                else:
                    embedding = np.pad(embedding, (0, self.embedding_dim - embedding.shape[0]), mode='constant')

            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def print_memory_metadata(self):
      """
      Print metadata for all chunks in the memory cache
      """
      print("\n===== MEMORY CACHE METADATA =====")

      if not hasattr(self, 'cache_index'):
          print("No cache index found.")
          return

      if not self.cache_index.metadata:
          print("Memory cache is empty.")
          return

      for idx, (chunk_id, metadata) in enumerate(self.cache_index.metadata.items(), 1):
          print(f"\n--- Memory Entry {idx} ---")
          print(f"Chunk ID: {chunk_id}")

          for key, value in metadata.items():
              print(f"{key}: {value}")

          chunk = metadata.get('chunk', 'No chunk text')
          print(f"Chunk Preview: {chunk[:200]}..." if len(chunk) > 200 else f"Chunk: {chunk}")

      print(f"\nTotal memory entries: {len(self.cache_index.metadata)}")

    def check_query_in_memory(self, query, threshold=0.95):
        """
        Check if a query exists in memory using similarity scores.

        Args:
            query (str): The query to check.
            threshold (float, optional): Similarity threshold. Default is 0.9.

        Returns:
            bool: True if a similar query exists, False otherwise.
        """
        try:
            query_embedding = self.text_embed_model.get_text_embedding(str(query))

            for metadata in self.cache_index.metadata.values():
                cached_query = str(metadata.get('query', ''))

                cached_query_embedding = self.text_embed_model.get_text_embedding(cached_query)

                similarity = np.dot(query_embedding, cached_query_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(cached_query_embedding)
                )

                if similarity >= threshold:
                    return True

            return False

        except Exception as e:
            print(f"Error checking query similarity: {e}")
            return False

    def run(self,  question, reset = None, agent_input = ''):
        """
        Execute the agent to process a query and generate a response.

        Args:
            retriever (object): The retrieval engine.
            question (str): The query or question to process.
            reset (bool, optional): Whether to reset the agent's state before running.

        Returns:
            str: The final answer generated by the agent, or None if processing fails.
        """

        if reset:
            self.__reset_agent()
        self.question = question
        self.answer = None
        self.agent_input = ''
        self.agent_input = agent_input
        self.jargons = []

        with tqdm(total=self.max_steps, desc="Processing", leave=True) as pbar:
            while not self.finished and self.step_n < self.max_steps:
                self.step()
                pbar.update(1)

                if self.answer:
                    final_answer = self.answer.replace("FINAL ANSWER:", "").strip()
                    return final_answer

            if not self.answer:
                print("\nNo response generated - agent failed to reach a conclusion")
                return None
        if self.step_n >= self.max_steps:
            print("Max steps limit reached")
            self.answer = None
        return self.answer

    def step(self):
        """
        Perform a single step in the agent's processing workflow, including thought generation, 
        retrieval, and memory updates.
        """
        thought_response = self.prompt_thought_agent()
        self.agent_input += ' ' + thought_response
        thought = self.agent_input.split('\n')[-1]
        print(thought)
        if thought_response is None:
                return

        if "RETRIEVAL" in thought:
            query = thought[20:]

            memory_result = self.check_memory_and_retrieve(query)

            if memory_result == "FORCE_REASONING":
                reasoning_response = self.prompt_reasoning_agent(force_completion=True)
                if reasoning_response is None:
                  pass
                reasoning_response = "\nFINAL ANSWER:" + reasoning_response
                self.agent_input += reasoning_response
                self.finished = True
                self.answer = reasoning_response
            elif memory_result:
                self.agent_input += f'\nOBSERVATION: {memory_result}'
                return
            try:
                retrieved_chunks = self.retriever.retrieve(query)
                if not retrieved_chunks:
                    return
                
                existing_graph_queries = self.get_existing_graph_queries()
                for i, chunk in enumerate(retrieved_chunks, 1):

                    if not chunk.text:
                        continue
                    chunk_result = self.engine.query(chunk.text)

                    # Add chunk and summary to memory
                    self.add_to_memory(
                        query=query,
                        chunk=str(chunk.text),
                        query_type='retrieval',
                        metadata={
                            'chunk_index': i,
                            'summarized_chunk_text': chunk_result
                        }
                    )

                    # Generate utility queries
                    try:
                        utility_queries = self.utility_query_generator.generate_queries(
                            chunk=str(chunk_result),
                            max_queries=2,
                            existing_graph_queries=existing_graph_queries
                        )

                        for utility_query in utility_queries:
                            if utility_query and utility_query != query:
                                self.add_to_memory(
                                    query=utility_query,
                                    chunk=str(chunk_result),
                                    original_query=query,
                                    query_type='utility'
                                )
                                existing_graph_queries.append(utility_query)

                    except Exception as e:
                        pass

                    self.agent_input += f'\nOBSERVATION: {chunk_result}'

            except Exception as e:
                import traceback
                traceback.print_exc()

            query_result = self.engine.query(thought[20:])
            query_conc = str(query_result)
            print(f'\n RAG ACTION: {query}\n')
            self.agent_input += f'\nOBSERVATION: {query_conc}'

        elif "REASONING" in self.agent_input.split('\n')[-1]:
            reasoning_response = self.prompt_reasoning_agent()
            if reasoning_response is None:
                pass
            elif "FINAL ANSWER" in reasoning_response:
                print(reasoning_response)
                self.agent_input += reasoning_response
            else:
                print(self.agent_input.split('\n')[-1], reasoning_response)
                self.agent_input += reasoning_response


        if "FINAL ANSWER" in self.agent_input.split('\n')[-1]:
            self.finished = True
            flag = input("However, we are not so sure about the correctness of the answer. Would you like us to re-evaluate? (yes/no)")
            if flag.lower() == "yes":
              clarity = print("In order to improve the question answering process, we would need you to guide us with the following terms. Kindly provide a description of the same : ")
              jargon_check = self.jargon_check(self.question)
              if jargon_check != "None":
                  l1 = eval(jargon_check)
                  clarified_jargons = []
                  for i in l1:
                    clarity = input(f"Provide the description for {i} : ")
                    clarified_jargons.append({i:clarity})
                    self.jargons.append(i)
                  enhanced_query = self.rephrase(self.question, clarified_jargons)
                  self.question = enhanced_query
                  new_docs = self.retrieve_docs( self.question)
                  if new_docs != None :
                    for doc in new_docs:
                        self.retriever.index.insert(doc)
                    self.engine = RetrieverQueryEngine.from_args(self.retriever, llm=llm)


              feedback = input("Enter your feedback or any clarification :- ")
              self.question = str(self.question) + "Feedback : " + str(feedback)

              print("Enhanced Query : " + self.question)
              self.answer = self.run(self.retriever, self.question, True, agent_input = '\n'.join(self.agent_input.split('\n')[:-2]))
            self.answer = self.agent_input.split('\n')[-1]
        self.step_n += 1

        if self.step_n >= self.max_steps:
            final_reasoning = self.prompt_reasoning_agent(force_completion=False)
            if final_reasoning:
                self.answer = final_reasoning
                self.finished = True

    def jargon_check(self, query):
        """
        Identifies jargon terms in the user's query.

        Args:
            query (str): The query to be analyzed for jargon.

        Returns:
            str: A list of identified jargon terms or "None" if no jargon is found.
        """
        jargon = self.llm.invoke(jargon_prompt.format_messages(query = query, prev_jargons = self.jargons))
        return jargon.content

    def rephrase(self, query , jargons):
        """
        Rephrases the user's query by defining and explaining jargon terms.

        Args:
            query (str): The original query that may contain jargon.
            jargons (str): A list or string of jargon terms identified in the query.

        Returns:
            str: The rephrased query with jargon terms defined.
        """
        rephrase = self.llm.invoke(rephrase_prompt.format_messages(query = query, jargons = jargons))
        return rephrase.content

    def prompt_thought_agent(self):
        """
        Generate a thought process for the agent using the thought agent prompt.

        Returns:
            str: The generated thought response from the LLM.
        """
        expression = None
        llm_input = self.thought_agent_prompt.format_messages(retriever=self.retriever, question=self.question, agent_input=self.agent_input)
        response = self.llm.invoke(llm_input).content
        return self.parse_llm_response(response, expression)

    def prompt_reasoning_agent(self, force_completion=False):
        """
        Generate reasoning for the agent using the reasoning agent prompt.

        Args:
            force_completion (bool): If True, overrides constraints to generate a response.

        Returns:
            str: The generated reasoning response from the LLM.
        """
        expression = f'REASONING'
        try:
            if force_completion:
                prompt = (self.reasoning_agent_prompt + "\nNote: Please provide a final answer based on all information gathered so far.")
            else:
                prompt = self.reasoning_agent_prompt

            llm_input = prompt.format_messages(retriever=self.retriever, question=self.question, agent_input=self.agent_input)
            response = self.llm.invoke(llm_input).content
            if force_completion and "FINAL ANSWER" not in response:
                response = f"FINAL ANSWER: {response}"
            return self.parse_llm_response(response, expression)
        except Exception as e:
            return None

    def parse_llm_response(self, response, expression):
        parsed_response = None
        if "FINAL ANSWER" in response:
            return response
        elif expression is None:
            if "RETRIEVAL THOUGHT" in response:
                expression = 'RETRIEVAL THOUGHT'
                self.agent_input += f'\n{expression}'
                pattern = re.compile(f"{expression}\s*(.*)")
                matches = pattern.findall(response)
                parsed_response = matches[-1] if matches else None
            elif "REASONING THOUGHT" in response:
                expression = 'REASONING THOUGHT'
                self.agent_input += f'\n{expression}'
                pattern = re.compile(f"{expression}\s*(.*)")
                matches = pattern.findall(response)
                parsed_response = matches[-1] if matches else None
        elif "REASONING" in expression:
            self.agent_input += f'\n{expression}'
            pattern = re.compile(r"REASONING\s*(.*)", re.DOTALL)
            matches = pattern.findall(response)
            parsed_response = matches[-1] if matches else None
        else:
            print(f'\nIncorrect {expression} {response}\n')

        if parsed_response is None:
            print(f'\nIncorrect {expression}\n')
        return parsed_response

    def get_random_questions_from_metadata(self):
        """
        Retrieve random follow-up query suggestions from the memory cache.

        Args:
            None

        Returns:
            str: A string of randomly selected follow-up query suggestions, formatted with numbered list items.
        """
        if not self.cache_index.metadata:
            print("Memory cache is empty.")
            return ""

        queries = []
        for metadata in self.cache_index.metadata.values():
            if 'query' in metadata:
                query = metadata['query']
                if isinstance(query, list):
                    queries.extend(query)
                else:
                    queries.append(query)

        if len(queries) < 3:
            random_questions = queries
        else:
            random_questions = random.sample(queries, 3)

        return '\n'.join([f"{idx + 1}. {question}" for idx, question in enumerate(random_questions)])

    def retrieve_docs(self, query):
      pdf_document = fitz.open(self.path)
      output_folder = "data"
      metadata = {}
      for page_num in range(len(pdf_document)):
          page_metadata = {"text": ""}
          page = pdf_document[page_num]
          page_text = page.get_text()
          page_metadata["text"] = page_text
          metadata[f"page_{page_num + 1}"] = page_metadata
      pdf_document.close()

      dimension = 1024
      index = faiss.IndexFlatL2(dimension)
      faiss_metadata = []
      count = 1
      for page, content in metadata.items():
          page_text = content["text"]
          page_embedding = text_embed_model.get_text_embedding(page_text)
          page_embedding = np.array([page_embedding], dtype="float32")
          index.add(page_embedding)
          faiss_metadata.append({
              "page": page.split("_")[-1],
              "text": page_text})
          count += 1
          
      query = str(query)
      query_embedding = query_embed_model.get_query_embedding(query)
      query_embedding = np.array([query_embedding], dtype="float32")
      top_k = min(10, len(metadata))
      distances, indices = index.search(query_embedding, top_k)

      results = []
      for idx, distance in zip(indices[0], distances[0]):
          if idx == -1:
              continue
          result_metadata = faiss_metadata[idx]
          result_metadata["distance"] = distance
          results.append(result_metadata)

      gt_num=[]
      for result in results:
        num = int(re.search(r'\d+', result['page']).group())
        if gt_num in self.page_num:
            continue
        gt_num.append(num)

      #re-writing the pages to a pdf since it is the expected input format of Unstructured.
      
      if len(gt_num) == 0:
          return None
      else:
          top_k = min(len(gt_num), 3)
          gt_num = gt_num[:top_k]

      writer = PdfWriter()
      input_pdf = PdfReader(self.path)
      for i in gt_num:
        writer.add_page(input_pdf.pages[i-1])

      batch_filename = 'data/elements.pdf'
      with open(batch_filename, 'wb') as output_file:
          writer.write(output_file)

      with open(batch_filename, "rb") as f:
        data = f.read()
        req = operations.PartitionRequest(partition_parameters=shared.PartitionParameters(files=shared.Files( content=data, file_name=batch_filename) , strategy=shared.Strategy.HI_RES, languages=['eng'],  extract_image_block_types=["Image"]))
        try:
          res = client_unstructured.general.partition(request=req)
        except Exception as e:
          print(e)

      page_metadata={}
      for element in res.elements:

          page_num = element["metadata"]["page_number"]
          if page_metadata.get(f"page_{page_num}", None) is None:
              page_metadata[f"page_{page_num}"] = ""

          if element['type'] == 'Table':
              html = element["metadata"]["text_as_html"]
              text = table_summary(html)
              time.sleep(2)
              page_metadata[f"page_{page_num}"] += f" \n{text}\n"

          elif element['type'] == 'Title':
              text = element["text"]
              page_metadata[f"page_{page_num}"] += f"\n{text}\n"
          elif element['type'] == 'Image':
              base64_reper = element["metadata"]["image_base64"]
              text = image_summary(base64_reper)
              time.sleep(1)
              page_metadata[f"page_{page_num}"] += f" \n{text}\n"
          else :
              text = element["text"]
              page_metadata[f"page_{page_num}"] += f"  {text}"
      docs = [Document(text=content, metadata={"page_number": page_num})
            for page_num, content in page_metadata.items()]
      return docs
  
    def __reset_agent(self):
        """
        Reset the agent's internal state, including input and step count.
        """
        self.step_n = 1
        self.answer = ''
        self.finished = False
        self.agent_input = ''
        self.previous_queries.clear()