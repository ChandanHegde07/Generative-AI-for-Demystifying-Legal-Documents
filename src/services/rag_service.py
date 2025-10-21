import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import streamlit as st
from typing import List

from src.config import Config

try:
    genai.configure(api_key=Config._GEMINI_API_KEY)
except Exception as e:
    st.error(f"Failed to configure Google API: {e}")
    st.stop()


class RAGService:
    def __init__(self, document_text: str):
        """
        Initializes the RAG service by processing the document text.
        
        Args:
            document_text: The combined text from the uploaded document(s).
        """
        print("DEBUG: Initializing RAGService...")
        self.text_chunks = self._get_text_chunks(document_text)
        if self.text_chunks:
            self.vector_store = self._get_vector_store(self.text_chunks)
            if self.vector_store:
                print("DEBUG: RAGService initialized successfully. Vector store created.")
        else:
            self.vector_store = None
            print("WARNING: RAGService initialized, but no text chunks were generated to create a vector store.")

    def _get_text_chunks(self, text: str) -> List[str]:
        """Splits the text into smaller chunks."""
        if not text or not text.strip():
            print("DEBUG: Input text for chunking is empty.")
            return []
            
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        print(f"DEBUG: Text split into {len(chunks)} chunks.")
        return chunks

    def _get_vector_store(self, text_chunks: List[str]):
        """Creates embeddings and stores them in a FAISS vector store."""
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model=Config.EMBEDDING_MODEL_NAME)
            
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
            return vector_store
        except Exception as e:
            error_msg = f"Failed to create the document's searchable index (vector store). The Q&A feature may not work. Error: {e}"
            print(f"ERROR: {error_msg}")
            st.warning(error_msg) 
            return None

    def retrieve_relevant_chunks(self, query: str) -> str:
        """
        Retrieves the most relevant text chunks from the vector store based on the user's query.
        
        Args:
            query: The user's question.
            
        Returns:
            A string containing the concatenated relevant context.
        """
        if not self.vector_store:
            print("DEBUG: Vector store not available. Cannot retrieve chunks.")
            return ""
            
        try:
            docs = self.vector_store.similarity_search(query, k=3)
            
            context = "\n\n---\n\n".join([doc.page_content for doc in docs])
            print(f"DEBUG: Retrieved {len(docs)} relevant chunks for the query.")
            return context
        except Exception as e:
            print(f"ERROR: Failed during similarity search: {e}")
            return ""