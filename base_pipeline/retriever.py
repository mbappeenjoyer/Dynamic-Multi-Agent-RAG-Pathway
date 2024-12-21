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
from summary_module import summary_module
import re
import time

from utils import client_table, text_embed_model, query_embed_model, client_unstructured, llm

def image_summary(image_content):
    """
    Generate a concise summary of a image from its base64 representation.

    This function uses a large vision language model to create a retrieval-optimized 
    summary of a image, preserving all critical information including numerical data.

    Args:
        The base64 code representing the image to be summarized.

    Returns:
        str: A concise, information-rich summary of the image content.
    """
    image_summary = client_table.chat.completions.create(
          messages=[
              {
                  "role": "user",
                  "content": [
                      {"type": "text", "text": "Give the detailed summary of the given image , without loosing any information"},
                      {
                          "type": "image_url",
                          "image_url": {
                              "url": f'data:image/jpeg;base64,{image_content}',
                          },
                      },
                  ],
              }
          ],
          temperature = 0.7,
          model="llama-3.2-90b-vision-preview",
      )
    return image_summary.choices[0].message.content

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

def retriever(path, query, top_k):
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
  pdf_document = fitz.open(path)
  output_folder = "data"

  metadata = {}
  for page_num in range(len(pdf_document)):
      page_metadata = {"text": ""}
      page = pdf_document[page_num]

      page_text = page.get_text()
      page_metadata["text"] = page_text

      metadata[f"page_{page_num + 1}"] = page_metadata

  pdf_document.close()

  metadata_file_path = os.path.join(output_folder, "pdf_metadata.json")
  with open(metadata_file_path, "w", encoding="utf-8") as json_file:
      json.dump(page_metadata, json_file, indent=4)

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

  faiss.write_index(index, "faiss_index.bin")
  with open("faiss_metadata.json", "w", encoding="utf-8") as meta_file:
          json.dump(faiss_metadata, meta_file, indent=4)

  query_embedding = query_embed_model.get_query_embedding(query)
  query_embedding = np.array([query_embedding], dtype="float32")
  distances, indices = index.search(query_embedding, top_k)

  #doc level retrieval

  results = []
  for idx, distance in zip(indices[0], distances[0]):
      if idx == -1:
          continue
      print(idx+1)
      result_metadata = faiss_metadata[idx]
      result_metadata["distance"] = distance
      results.append(result_metadata)

  index = faiss.read_index("faiss_index.bin")
  with open("faiss_metadata.json", "r", encoding="utf-8") as meta_file:
      faiss_metadata = json.load(meta_file)

  gt_num=[]
  for result in results:
    num = int(re.search(r'\d+', result['page']).group())
    print(gt_num)
    gt_num.append(num)

  #re-writing the pages to a pdf since it is the expected input format of Unstructured.

  writer = PdfWriter()
  input_pdf = PdfReader(path)
  for i in gt_num:
    writer.add_page(input_pdf.pages[i-1])

  batch_filename = 'data/elements.pdf'
  with open(batch_filename, 'wb') as output_file:
      writer.write(output_file)

  with open(batch_filename, "rb") as f:
    data = f.read()
    req = operations.PartitionRequest(partition_parameters=shared.PartitionParameters(files=shared.Files( content=data, file_name=batch_filename) , strategy=shared.Strategy.HI_RES, languages=['eng'], extract_image_block_types=["Image"]))
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
          time.sleep(1)
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
  retriever = RaptorRetriever(docs,embed_model=text_embed_model,
        llm=llm, similarity_top_k=2,mode="collapsed",
        transformations=[SentenceSplitter(chunk_size=900, chunk_overlap=200)],)
  return retriever, gt_num