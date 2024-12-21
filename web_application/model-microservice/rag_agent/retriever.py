import faiss
import json
import os
import fitz
import numpy as np
from llama_index.core import Document
from llama_index.packs.raptor import RaptorRetriever
from llama_index.core.node_parser import SentenceSplitter
from PyPDF2 import PdfReader, PdfWriter
from unstructured_client.models import operations, shared
# from rag_agent.summary_module import summary_module
from llama_index.core import (
    SimpleDirectoryReader,
    load_index_from_storage,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.core import Document
from llama_index.vector_stores.faiss import FaissVectorStore
from IPython.display import Markdown, display
from llama_index.core.node_parser import TokenTextSplitter
import fitz 
import numpy as np
from llama_index.core import Settings
import re
from io import BytesIO
import time

from rag_agent.utils import client_table, text_embed_model, query_embed_model, client_unstructured, llm

def table_summary(html_code):
    """
    Generate a concise summary of a table from its HTML representation.

    This function uses a large language model to create a retrieval-optimized 
    summary of a table, preserving all critical information including numerical data.

    Args:
        html_code (str): The HTML code representing the table to be summarized.

    Returns:
        str: A concise, information-rich summary of the table content.

    Example:
        >>> html_table = "<table>...</table>"
        >>> summary = table_summary(html_table)
        >>> print(summary)
        'Table summary with key insights...'
    """
    
    prompt_text = f"""You are an assistant tasked with summarizing tables for retrieval. \
    These summaries will be embedded and used to retrieve the raw table elements. \
    You will be given with html code of table, you have to return concise summary of table (without lossing any information , including numerical), well optimized for retrieval. Table:{html_code} Summary:"""

    summary = client_table.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt_text}],
        temperature=0.7,
        top_p=0.9,
        stream=False
    )
    return summary.choices[0].message.content

def jina_retriever(pdf_content, query, top_k):
    # pass
  pdf_document = fitz.open(stream=BytesIO(pdf_content), filetype="pdf")

  metadata = {}
  for page_num in range(len(pdf_document)):
      page_metadata = {"text": ""}
      page = pdf_document[page_num]

      page_text = page.get_text()
      page_metadata["text"] = page_text

      metadata[f"page_{page_num + 1}"] = page_metadata

  pdf_document.close()

  #constructing a FAISS vector store for text-based doc level retrieval.
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
          "text": page_text
      })
      count += 1

  query_embedding = query_embed_model.get_query_embedding(query)
  query_embedding = np.array([query_embedding], dtype="float32")
  distances, indices = index.search(query_embedding, top_k)

  #doc level retrieval

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
    gt_num.append(num)

  writer = PdfWriter()
  input_pdf  = PdfReader(BytesIO(pdf_content))
  for i in gt_num:
    writer.add_page(input_pdf.pages[i-1])

  output_pdf_stream = BytesIO()
  writer.write(output_pdf_stream)
  output_pdf_stream.seek(0) 

  data = output_pdf_stream.read()
  req = operations.PartitionRequest(partition_parameters=shared.PartitionParameters(files=shared.Files( content=data, file_name="temp.pdf") , strategy=shared.Strategy.HI_RES, languages=['eng'], ))
  try:
    res = client_unstructured.general.partition(request=req)
  except Exception as e:
    pass

  page_text = ""
  for element in res.elements:

      if element['type'] == 'Table':
          html = element["metadata"]["text_as_html"]
          text = table_summary(html)
          time.sleep(1)
          pdf_text += f" \n{text}\n"

      elif element['type'] == 'Title':
          text = element["text"]
          pdf_text += f"\n{text}\n"
      else :
          text = element["text"]
          pdf_text += f"  {text}"
  
  d = 1024  
  faiss_index2 = faiss.IndexFlatL2(d)
  vector_store = FaissVectorStore(faiss_index=faiss_index2)
  storage_context = StorageContext.from_defaults(vector_store=vector_store)
  
  splitter = TokenTextSplitter(chunk_size=900,chunk_overlap=200)
  chunks = splitter.split_text(pdf_text)
  documents = []
  for chunk in chunks:
    embedding = text_embed_model.get_text_embedding(chunk)  
    documents.append(Document(text=chunk, embedding=embedding))

  Settings.embed_model = text_embed_model
  index2 = VectorStoreIndex.from_documents(documents, storage_context=storage_context,)
  
  retriever = index2.as_retriever(top_k=top_k)
  return retriever

def raptor_retriever(pdf_content, query, top_k):
  """
    Retrieve and process relevant pages from a PDF document based on a semantic query.

    This function extracts text and metadata from a PDF document, constructs a FAISS-based vector index for semantic search, and processes retrieved content. It returns a `RaptorRetriever` object for performing advanced semantic queries.

    Args:
        path (str): File path to the input PDF document.
        query (str): Semantic query to search within the document.
        top_k (int): Number of top-k most relevant pages to retrieve.

    Returns:
        RaptorRetriever: A query engine equipped to perform semantic search over the document.

    Raises:
        FileNotFoundError: If the specified PDF file does not exist.
        ValueError: If the query is empty or top_k is not a positive integer.

    Example:
        >>> query_engine = retriever('document.pdf', 'research methodology', top_k=3)
        >>> response = query_engine.query("Summarize the key findings")
  """
  pdf_document = fitz.open(stream=BytesIO(pdf_content), filetype="pdf")

  metadata = {}
  for page_num in range(len(pdf_document)):
      page_metadata = {"text": ""}
      page = pdf_document[page_num]

      page_text = page.get_text()
      page_metadata["text"] = page_text

      metadata[f"page_{page_num + 1}"] = page_metadata

  pdf_document.close()

  #constructing a FAISS vector store for text-based doc level retrieval.
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
          "text": page_text
      })
      count += 1

  query_embedding = query_embed_model.get_query_embedding(query)
  query_embedding = np.array([query_embedding], dtype="float32")
  distances, indices = index.search(query_embedding, top_k)

  #doc level retrieval

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
    gt_num.append(num)

  #re-writing the pages to a pdf since it is the expected input format of Unstructured.

  writer = PdfWriter()
  input_pdf  = PdfReader(BytesIO(pdf_content))
  for i in gt_num:
    writer.add_page(input_pdf.pages[i-1])

  output_pdf_stream = BytesIO()
  writer.write(output_pdf_stream)
  output_pdf_stream.seek(0)  # Reset the stream position for reading

  data = output_pdf_stream.read()
  req = operations.PartitionRequest(partition_parameters=shared.PartitionParameters(files=shared.Files( content=data, file_name="temp.pdf") , strategy=shared.Strategy.HI_RES, languages=['eng'], ))
  try:
    res = client_unstructured.general.partition(request=req)
  except Exception as e:
    pass

  page_metadata={}
  for element in res.elements:

      page_num = element["metadata"]["page_number"]
      if page_metadata.get(f"page_{page_num}", None) is None:
          page_metadata[f"page_{page_num}"] = ""

      if element['type'] == 'Table':
          html = element["metadata"]["text_as_html"]
          text = table_summary(html)
          time.sleep(1)
          page_metadata[f"page_{page_num}"] += f" \n{text}\n"

      elif element['type'] == 'Title':
          text = element["text"]
          page_metadata[f"page_{page_num}"] += f"\n{text}\n"
      else :
          text = element["text"]
          page_metadata[f"page_{page_num}"] += f"  {text}"
  docs = [Document(text=content, metadata={"page_number": page_num})
        for page_num, content in page_metadata.items()]
  retriever = RaptorRetriever(docs,embed_model=text_embed_model,
        llm=llm, similarity_top_k=2,mode="collapsed",
        transformations=[SentenceSplitter(chunk_size=900, chunk_overlap=200)],)
  return retriever