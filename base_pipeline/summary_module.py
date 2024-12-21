import nltk
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from typing import List
from collections import namedtuple

BaseNode = namedtuple("BaseNode", ["text"])
nltk.download('punkt')

class SummaryModule:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-cnn"
        ) -> None:
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def chunk_document(self, document: str) -> List[List[str]]:
        """Chunk the document into smaller pieces with a maximum length of 1024 tokens."""
        nested = []
        sent = []
        length = 0

        for sentence in nltk.sent_tokenize(document):
            length += len(sentence)
            if length < 1024:
                sent.append(sentence)
            else:
                nested.append(sent)
                sent = [sentence]
                length = len(sentence)

        if sent:
            nested.append(sent)
        return nested

    def generate_summary(self, nested_sentences: List[List[str]]) -> List[str]:
        """Generate a summary for each chunk of text with <= 1024 tokens."""
        summaries = []

        for nested in nested_sentences:
            # Join sentences into a single string
            text_chunk = ' '.join(nested)

            # Tokenize and move input to the correct device with explicit max_length
            input_tokenized = self.tokenizer.encode(
                text_chunk,
                truncation=True,
                max_length=1024,  # Set a reasonable max length for the model
                return_tensors='pt'
            ).to(self.device)

            # Generate summary
            summary_ids = self.model.generate(
                input_tokenized,
                length_penalty=3.0,
                min_length=30,
                max_length=100,
                no_repeat_ngram_size=3,
                num_beams=4,
                early_stopping=True
            )

            # Decode the summary
            output = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in summary_ids]
            summaries.extend(output)

        return summaries

    def summarize_document(self, document: str) -> str:
        """Summarize the entire document by chunking and summarizing each part."""
        # Chunk the document
        nested_sentences = self.chunk_document(document)

        # Generate summaries for each chunk
        summaries = self.generate_summary(nested_sentences)

        # Combine all summaries into a final summary
        final_summary = ' '.join(summaries)
        return final_summary

    async def generate_summaries(
        self, documents_per_cluster: List[List[BaseNode]]
    ) -> List[str]:
        """
        Generate summaries for clusters of documents.

        Args:
            documents_per_cluster (List[List[BaseNode]]): List of document clusters.

        Returns:
            List[str]: Summaries for each cluster.
        """
        summaries = []

        for documents in documents_per_cluster:
            # Combine texts from all documents in the cluster
            combined_text = " ".join([doc.text for doc in documents])
            final_summary = self.summarize_document(combined_text)

            # Append the combined summary to summaries list
            summaries.append(final_summary)

        return summaries
    
summary_module = SummaryModule()