import os, glob, traceback, hashlib
import re
import numpy as np
import pandas as pd
from typing import Union, Sequence, Dict, Any, List

from langchain_cohere import CohereRerank
from langchain_community.document_loaders import UnstructuredMarkdownLoader, PyMuPDFLoader, \
    UnstructuredWordDocumentLoader, TextLoader
from langchain_postgres.v2.indexes import HNSWIndex, DistanceStrategy

from langchain_core.documents import Document
from langchain_postgres import PGEngine
from langchain_postgres.v2.async_vectorstore import AsyncPGVectorStore
from langchain_openai import OpenAIEmbeddings

from .kbase_service import KBaseService, VectorStoreConfig


class CategoryConfig:
    """Configuration for category inference with keywords"""
    CATEGORY_KEYWORDS = {
        # Add your category-specific keywords here
        # These will be populated automatically from your documents
    }


class VectorService(KBaseService):
    store: AsyncPGVectorStore = None
    config: VectorStoreConfig
    documents: list[Document]
    categories: list[str]
    _category_embeddings: Dict[str, List[float]] = {}
    _embeddings: OpenAIEmbeddings | None = None

    def __init__(self, config: VectorStoreConfig) -> None:
        self.config = config
        self.documents, self.categories = self.load_documents()
        self._compressor = CohereRerank(
            top_n=self.config['topN'],
            model=self.config['reRankModel']
        )
        # Get unique categories
        self.unique_categories = list(set(self.categories))
        # Initialize embeddings for category inference
        self._embeddings = OpenAIEmbeddings(model=self.config['embedModel'])
        self._category_embeddings = {}

    def load_documents(self) -> tuple[list[Document], list[str]]:
        loaded: list[Document] = []
        base = self.config['location']
        categories: list[str] = []

        for path in glob.glob(os.path.join(base, "**", "*"), recursive=True):
            if os.path.isdir(path) or os.path.basename(path).startswith("."):
                continue
            ext = os.path.splitext(path)[1].lower()

            relative_path = os.path.relpath(path, base)
            category = relative_path.split(os.sep)[0] if os.sep in relative_path else "general"

            try:
                loaded_docs = []
                if ext == ".md":
                    for d in UnstructuredMarkdownLoader(path).load():
                        loaded_docs.append(d)
                elif ext == ".pdf":
                    for d in PyMuPDFLoader(path).load():
                        loaded_docs.append(d)
                elif ext == ".docx":
                    for d in UnstructuredWordDocumentLoader(path).load():
                        loaded_docs.append(d)
                elif ext == ".txt":
                    for d in TextLoader(path).load():
                        loaded_docs.append(d)
                elif ext == '.csv':
                    df = pd.read_csv(path)
                    df = df.replace({np.nan: None})

                    filename = os.path.basename(path)

                    for row_num, (_, row) in enumerate(df.iterrows()):
                        row_dict = row.to_dict()

                        row_text = f"Record from {filename}:\n"
                        row_text += "\n".join([
                            f"{col}: {val}" for col, val in row_dict.items()
                            if val is not None
                        ])

                        doc = Document(
                            page_content=row_text,
                            metadata={
                                "source": path,
                                "row_number": row_num,  # This is a proper int
                                "csv_data": row_dict
                            }
                        )
                        loaded_docs.append(doc)

                for d in loaded_docs:
                    d.metadata["category"] = category
                    d.metadata['file_type'] = ext
                    loaded.append(d)
                    categories.append(category)
            except Exception:
                print(f"INGEST ERROR: failed to load {path}")
                traceback.print_exc()

        return loaded, categories

    async def get_vector_store(self) -> AsyncPGVectorStore | None:
        if self.store:
            return self.store

        engine = PGEngine.from_connection_string(self.config['connectionStr'])
        embeddings = OpenAIEmbeddings(model=self.config['embedModel'])

        self.store = await AsyncPGVectorStore.create(
            engine=engine,
            embedding_service=embeddings,
            table_name=self.config['tableName'],
            metadata_json_column=self.config['metadataJsonColumn'],
            metadata_columns=self.config['metadataColumns'],
        )

        await self.add_docs_to_store()
        await self._create_index()

        return self.store

    async def _create_index(self):
        index = HNSWIndex(
            name="hnsw_idx",
            distance_strategy=DistanceStrategy.COSINE_DISTANCE,
            m=16,
            ef_construction=64
        )
        try:
            await self.store.aapply_vector_index(index, concurrently=True)
            print("Index created successfully")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg:
                print("Index already exists, skipping creation")
            else:
                print(f"Error creating index: {e}")
                traceback.print_exc()
                raise

    async def add_docs_to_store(self) -> list[str]:
        store = await self.get_vector_store()
        document_id_key = 'document_id'

        new_documents = []
        added_ids = []

        for doc in self.documents:
            # Check if document has an ID in metadata
            doc_id = doc.metadata.get(document_id_key)

            if not doc_id:
                # Generate ID from content hash if not provided
                doc_id = self._generate_doc_id(doc.page_content)
                doc.metadata[document_id_key] = doc_id

            # Check if document exists
            if not await self.document_exists(doc_id):
                new_documents.append(doc)
                added_ids.append(doc_id)

        self.documents = []

        # Add only new documents
        if new_documents:
            await store.aadd_documents(new_documents)
            print(f"Added {len(new_documents)} new documents to vector store")
        else:
            print("All documents already exist in vector store")

        return added_ids

    def _generate_doc_id(self, content: str) -> str:
        """Generate a unique ID based on content hash"""
        return hashlib.md5(content.encode()).hexdigest()

    async def _retrieve_and_rerank(
            self,
            query: str,
            k: int = 5,
            category: str | None = None
    ) -> Union[list[Document], Sequence[Document]]:
        """
        Retrieve documents and rerank them using Cohere.
        Mimics the behavior of ContextualCompressionRetriever with CohereRerank.
        """
        store = await self.get_vector_store()
        if not store:
            return []

        # Build search kwargs
        search_kwargs = {"k": k}
        if category:
            search_kwargs["filter"] = {"category": category}

        # Initial retrieval from vector store
        initial_docs = await store.asimilarity_search(query, **search_kwargs)

        if not initial_docs:
            return []

        # Apply reranking
        if self._compressor:
            # CohereRerank expects documents in a specific format
            compressed_docs = await self._compressor.acompress_documents(
                documents=initial_docs,
                query=query
            )
            return compressed_docs

        return initial_docs

    async def document_exists(self, document_id: str) -> bool:
        """Check if a document with given ID already exists"""
        store = await self.get_vector_store()

        # Search by metadata
        results = await store.asimilarity_search(
            query="",  # Empty query to just filter by metadata
            k=1,
            filter={"document_id": document_id}  # Fixed: was "document_id_key"
        )

        return len(results) > 0

    # ========== Category Inference Methods ==========

    async def _initialize_category_embeddings(self):
        """Pre-compute embeddings for categories"""
        if self._category_embeddings or not self._embeddings:
            return

        for category in self.unique_categories:
            # Create a representative description for each category
            # You can customize this based on your needs
            description = f"Documents and content related to {category}"
            embedding = await self._embeddings.aembed_query(description)
            self._category_embeddings[category] = embedding

    def _normalize_text(self, text: str) -> str:
        """Normalize text for keyword matching"""
        return re.sub(r'[^\w\s]', '', text.lower())

    def _infer_category_keyword(self, query: str, min_score: float = 0.3) -> Dict[str, Any]:
        """
        Keyword-based category inference.
        Matches query against category names.
        """
        if not self.unique_categories:
            return {"category": None, "confidence": 0.0, "method": "keyword"}

        query_normalized = self._normalize_text(query)
        query_words = set(query_normalized.split())

        scores = {}
        for category in self.unique_categories:
            category_normalized = self._normalize_text(category)
            category_words = set(category_normalized.split())

            # Check for exact category name match
            if category_normalized in query_normalized:
                scores[category] = 1.0
                continue

            # Check for word overlap
            matches = len(query_words & category_words)
            if matches > 0:
                # Score based on percentage of category words matched
                scores[category] = matches / max(len(category_words), 1)
            else:
                scores[category] = 0.0

        if not scores or max(scores.values()) < min_score:
            return {"category": None, "confidence": 0.0, "method": "keyword"}

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        return {
            "category": best_category,
            "confidence": best_score,
            "method": "keyword",
            "all_scores": scores
        }

    async def _infer_category_embedding(self, query: str, min_similarity: float = 0.65) -> Dict[str, Any]:
        """
        Embedding-based category inference using cosine similarity.
        Compares query embedding to category embeddings.
        """
        if not self._embeddings or not self.unique_categories:
            return {"category": None, "confidence": 0.0, "method": "embedding"}

        # Initialize category embeddings if not done
        await self._initialize_category_embeddings()

        if not self._category_embeddings:
            return {"category": None, "confidence": 0.0, "method": "embedding"}

        # Get query embedding
        query_embedding = await self._embeddings.aembed_query(query)

        # Calculate cosine similarity with each category
        similarities = {}
        for cat_name, cat_embedding in self._category_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, cat_embedding)
            similarities[cat_name] = similarity

        if not similarities:
            return {"category": None, "confidence": 0.0, "method": "embedding"}

        best_category = max(similarities, key=similarities.get)
        best_similarity = similarities[best_category]

        if best_similarity < min_similarity:
            return {"category": None, "confidence": best_similarity, "method": "embedding"}

        return {
            "category": best_category,
            "confidence": best_similarity,
            "method": "embedding",
            "all_scores": similarities
        }

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    async def _infer_category_hybrid(
            self,
            query: str,
            keyword_weight: float = 0.4,
            embedding_weight: float = 0.6,
            min_confidence: float = 0.4
    ) -> Dict[str, Any]:
        """
        Hybrid approach: combines keyword and embedding methods.
        Uses weighted average of both scores.
        """
        # Get results from both methods
        keyword_result = self._infer_category_keyword(query, min_score=0.0)
        embedding_result = await self._infer_category_embedding(query, min_similarity=0.0)

        # If either method failed, fall back to the other
        if keyword_result['category'] is None and embedding_result['category'] is None:
            return {"category": None, "confidence": 0.0, "method": "hybrid"}

        if keyword_result['category'] is None:
            return {**embedding_result, "method": "hybrid-embedding-only"}

        if embedding_result['category'] is None:
            return {**keyword_result, "method": "hybrid-keyword-only"}

        # Combine scores from both methods
        combined_scores = {}
        all_categories = set(keyword_result.get('all_scores', {}).keys()) | \
                         set(embedding_result.get('all_scores', {}).keys())

        for category in all_categories:
            keyword_score = keyword_result.get('all_scores', {}).get(category, 0.0)
            embedding_score = embedding_result.get('all_scores', {}).get(category, 0.0)

            combined_scores[category] = (
                    keyword_weight * keyword_score +
                    embedding_weight * embedding_score
            )

        if not combined_scores:
            return {"category": None, "confidence": 0.0, "method": "hybrid"}

        best_category = max(combined_scores, key=combined_scores.get)
        best_score = combined_scores[best_category]

        if best_score < min_confidence:
            return {"category": None, "confidence": best_score, "method": "hybrid"}

        return {
            "category": best_category,
            "confidence": best_score,
            "method": "hybrid",
            "keyword_result": keyword_result,
            "embedding_result": embedding_result,
            "all_scores": combined_scores
        }

    async def _infer_category(
            self,
            query: str,
            method: str = "hybrid"  # Options: "keyword", "embedding", "hybrid"
    ) -> str | None:
        """
        Main category inference method.

        Args:
            query: The search query
            method: Inference method to use ("keyword", "embedding", or "hybrid")

        Returns:
            The inferred category name or None if no category matches
        """
        if not self.unique_categories:
            return None

        try:
            if method == "keyword":
                result = self._infer_category_keyword(query)
            elif method == "embedding":
                result = await self._infer_category_embedding(query)
            elif method == "hybrid":
                result = await self._infer_category_hybrid(query)
            else:
                print(f"Unknown inference method: {method}, falling back to hybrid")
                result = await self._infer_category_hybrid(query)

            category = result.get("category")
            confidence = result.get("confidence", 0.0)

            # Log the inference for debugging
            if category:
                print(f"Category inferred: {category} (confidence: {confidence:.2f}, method: {result.get('method')})")
            else:
                print(f"No category inferred (confidence too low: {confidence:.2f})")

            return category

        except Exception as e:
            print(f"Error inferring category: {e}")
            traceback.print_exc()
            return None

    async def load_context(self, query: str, k: int = 5, infer_category: bool = True) -> str:
        """
        Retrieve relevant context from vector store

        Args:
            query: The search query
            k: Number of documents to retrieve
            infer_category: Whether to infer and use category filtering
        """
        category = None
        if infer_category:
            category = await self._infer_category(query)

        if k is None:
            k = int(os.getenv("RETRIEVAL_K", "5"))

        # Retrieve and rerank documents
        relevant_docs = await self._retrieve_and_rerank(
            query=query,
            k=k,
            category=category
        )

        if not relevant_docs:
            return "\n\n[No relevant context found in knowledge base]"

        # Format context
        context = "\n\n---\n\n".join([
            f"[Document {i + 1}]\n{doc.page_content}"
            for i, doc in enumerate(relevant_docs)
        ])

        category_info = f" (filtered by category: {category})" if category else ""
        return f"\n\nRelevant Knowledge Base Context{category_info}:\n{context}"
