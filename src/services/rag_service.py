import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import streamlit as st
from typing import List
import os
import hashlib

from src.config import Config

try:
    genai.configure(api_key=Config._GEMINI_API_KEY)
except Exception as e:
    st.error(f"Failed to configure Google API: {e}")
    st.stop()

CACHE_DIR = "vector_store_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

class RAGService:
    def __init__(self, document_text: str):
        self.vector_store = None
        
        document_id = hashlib.sha256(document_text.encode()).hexdigest()
        cache_folder_path = os.path.join(CACHE_DIR, document_id)
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model=Config.EMBEDDING_MODEL_NAME)
        
        if os.path.exists(cache_folder_path):
            print(f"DEBUG: Loading vector store from local cache: {cache_folder_path}")
            try:
                self.vector_store = FAISS.load_local(cache_folder_path, self.embeddings, allow_dangerous_deserialization=True)
                print("DEBUG: RAGService initialized successfully from cache.")
            except Exception as e:
                print(f"ERROR: Failed to load from cache: {e}. Rebuilding...")
                self.vector_store = self._build_and_save_vector_store(document_text, cache_folder_path)
        else:
            print("DEBUG: No cache found. Building new vector store...")
            self.vector_store = self._build_and_save_vector_store(document_text, cache_folder_path)
        
        if self.vector_store:
            self.retriever = self._initialize_reranker(self.vector_store)
        else:
            self.retriever = None

    def _build_and_save_vector_store(self, document_text, cache_path):
        text_chunks = self._get_semantic_chunks(document_text)
        if not text_chunks:
            print("WARNING: No text chunks generated.")
            return None
            
        try:
            print("DEBUG: Creating new FAISS vector store...")
            vector_store = FAISS.from_texts(text_chunks, self.embeddings)
            print("DEBUG: New vector store created. Saving to local cache.")
            vector_store.save_local(cache_path)
            return vector_store
        except Exception as e:
            error_msg = f"Failed to create and save vector store: {e}"
            print(f"ERROR: {error_msg}")
            st.warning("Could not create the document's searchable index. Q&A may be limited.")
            return None

    def _get_semantic_chunks(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        print("DEBUG: Performing semantic chunking...")
        text_splitter = SemanticChunker(self.embeddings)
        chunks = text_splitter.split_text(text)
        print(f"DEBUG: Text split into {len(chunks)} semantic chunks.")
        return chunks

    def _initialize_reranker(self, vector_store):
        print("DEBUG: Initializing CrossEncoder for reranking...")
        base_retriever = vector_store.as_retriever(search_kwargs={"k": 7})
        
        model = HuggingFaceCrossEncoder(model_name='cross-encoder/ms-marco-MiniLM-L-6-v2')
        
        compressor = CrossEncoderReranker(model=model, top_n=3)
        
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=base_retriever
        )
        print("DEBUG: Reranker initialized.")
        return compression_retriever

    def retrieve_relevant_chunks(self, query: str) -> str:
        if not self.retriever:
            print("DEBUG: Retriever not available. Cannot retrieve chunks.")
            return ""
            
        try:
            print(f"DEBUG: Performing compressed retrieval (reranking) for query: '{query}'")
            reranked_docs = self.retriever.get_relevant_documents(query)
            
            if not reranked_docs:
                print("DEBUG: Reranking returned 0 documents.")
                return ""

            context = "\n\n---\n\n".join([doc.page_content for doc in reranked_docs])
            print(f"DEBUG: Retrieved {len(reranked_docs)} reranked chunks.")
            return context
        except Exception as e:
            print(f"ERROR: Failed during compressed retrieval: {e}")
            return ""