import pathway as pw 
from pathway.xpacks.llm.embedders import SentenceTransformerEmbedder
from pathway.xpacks.llm.splitters import TokenCountSplitter
from pathway.xpacks.llm.parsers import ParseUnstructured
from pathway.stdlib.indexing import BruteForceKnnFactory, BruteForceKnnMetricKind
from pathway.xpacks.llm.document_store import DocumentStore
from pathway.xpacks.llm.question_answering import BaseRAGQuestionAnswerer
from pathway.xpacks.llm.llms import HFPipelineChat

import base64
import os
import fitz
import json

# llm = HFPipelineChat(model="gpt2", temperature=0.05, capacity=8)
class InputSchema(pw.Schema):
  page_number : int
  data : str 

os.makedirs("JINA" , exist_ok=True)
data_sources = []
data_sources.append(
    pw.io.jsonlines.read(
        "./JINA/",
        schema = InputSchema,
        mode="streaming",
        with_metadata=True,
    )
)
embedder = SentenceTransformerEmbedder(model="jinaai/jina-embeddings-v3", trust_remote_code=True, call_kwargs={"task": "retrieval.passage"})
splitter = TokenCountSplitter(max_tokens=400)

parser = ParseUnstructured()

# retriever_factory = BruteForceKnnFactory(reserved_space=1000, embedder=embedder, metric=BruteForceKnnMetricKind.COS, dimensions=1536)

# document_store = DocumentStore(docs=data_sources, parser=parser, splitter=splitter, retriever_factory=retriever_factory)

# question_answerer = BaseRAGQuestionAnswerer(llm=llm, indexer=document_store)

import logging

import pathway as pw
from dotenv import load_dotenv
from pathway.xpacks.llm.vector_store import VectorStoreServer
from pathway.xpacks.llm.servers import DocumentStoreServer
from pydantic import BaseModel, ConfigDict, InstanceOf

# To use advanced features with Pathway Scale, get your free license key from
# https://pathway.com/features and paste it below.
# To use Pathway Community, comment out the line below.
pw.set_license_key("demo-license-key-with-telemetry")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()


class App(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

    with_cache: bool = True
    terminate_on_error: bool = False

    def run(self) -> None:
        server = VectorStoreServer(  *data_sources,
         embedder= embedder,
        )
        server.run_server(
            host = self.host,
            port = self.port,
            with_cache=self.with_cache,
            threaded = True
        )

    model_config = ConfigDict(extra="forbid")


if __name__ == "__main__":
    app = App(host="0.0.0.0",port=8000)
    app.run()