"""
La Archivista - Document Organization Agent

Specializes in document organization, intelligent filing, metadata extraction,
and intelligent search capabilities.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import hashlib

from .base_agent import BaseAgent, AgentCapability


class LaArchivista(BaseAgent):
    """
    Document Organization Agent

    La Archivista manages document storage, organization, metadata extraction,
    and provides intelligent search capabilities across all documents.
    """

    def __init__(self):
        """Initialize La Archivista with document management capabilities."""
        super().__init__("La Archivista")

        # Set agent capabilities
        self.set_capability(AgentCapability.DOCUMENT_ORGANIZATION, True)
        self.set_capability(AgentCapability.METADATA_EXTRACTION, True)
        self.set_capability(AgentCapability.INTELLIGENT_SEARCH, True)

        # Document index
        self.document_index: Dict[str, Dict] = {}

        # Taxonomy and classification rules
        self.document_taxonomy = self._initialize_taxonomy()

        # Tag system
        self.tag_library: Dict[str, List[str]] = {}

    def _initialize_taxonomy(self) -> Dict[str, List[str]]:
        """
        Initialize document classification taxonomy.

        Returns:
            Dictionary of document categories and keywords
        """
        return {
            "contracts": [
                "agreement", "contract", "terms", "conditions",
                "whereas", "parties", "executed"
            ],
            "correspondence": [
                "letter", "email", "memorandum", "communication",
                "dear", "sincerely"
            ],
            "court_documents": [
                "motion", "complaint", "answer", "brief",
                "plaintiff", "defendant", "court", "docket"
            ],
            "financial": [
                "invoice", "receipt", "statement", "payment",
                "billing", "account", "balance"
            ],
            "research": [
                "analysis", "research", "memo", "opinion",
                "findings", "conclusion"
            ],
            "client_documents": [
                "client", "matter", "case", "file"
            ]
        }

    async def process(self, event) -> Dict[str, Any]:
        """
        Process document-related events.

        Args:
            event: SystemEvent containing document data

        Returns:
            Dictionary with document processing results
        """
        event_type = event.type

        if event_type == "document_uploaded":
            return await self._process_document_upload(event)
        elif event_type == "search_query":
            return await self._process_search_query(event)
        elif event_type == "document_analyzed":
            return await self._process_document_analysis(event)
        else:
            return {
                "agent": self.agent_name,
                "status": "skipped",
                "reason": f"Event type '{event_type}' not handled by this agent"
            }

    async def _process_document_upload(self, event) -> Dict[str, Any]:
        """
        Process a newly uploaded document.

        Args:
            event: Document upload event

        Returns:
            Document processing results
        """
        doc_data = event.payload

        # Extract document metadata
        metadata = self._extract_metadata(doc_data)

        # Classify document
        classification = self._classify_document(metadata)

        # Generate suggested tags
        suggested_tags = self._generate_tags(metadata, classification)

        # Generate document hash for deduplication
        doc_hash = self._generate_document_hash(doc_data)

        # Check for duplicates
        is_duplicate = doc_hash in self.document_index

        # Create document record
        document_record = {
            "id": doc_data.get("id"),
            "hash": doc_hash,
            "filename": doc_data.get("filename", "untitled"),
            "upload_date": datetime.now().isoformat(),
            "metadata": metadata,
            "classification": classification,
            "suggested_tags": suggested_tags,
            "file_path": self._generate_file_path(classification, metadata)
        }

        # Add to index if not duplicate
        if not is_duplicate:
            self.document_index[doc_hash] = document_record

        result = {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "document_id": doc_data.get("id"),
            "filename": doc_data.get("filename"),
            "is_duplicate": is_duplicate,
            "classification": classification,
            "suggested_tags": suggested_tags,
            "suggested_file_path": document_record["file_path"],
            "metadata_extracted": len(metadata),
            "recommended_actions": self._generate_filing_actions(document_record)
        }

        return result

    async def _process_search_query(self, event) -> Dict[str, Any]:
        """
        Process a document search query.

        Args:
            event: Search query event

        Returns:
            Search results
        """
        query_data = event.payload
        query = query_data.get("query", "")
        filters = query_data.get("filters", {})

        # Perform intelligent search
        results = self._search_documents(query, filters)

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": len(results),
            "results": results[:50],  # Limit to top 50 results
            "search_suggestions": self._generate_search_suggestions(query)
        }

    async def _process_document_analysis(self, event) -> Dict[str, Any]:
        """
        Process AI-analyzed document results.

        Args:
            event: Document analysis event

        Returns:
            Analysis processing results
        """
        analysis_data = event.payload
        doc_id = analysis_data.get("document_id")

        # Update document index with analysis results
        for doc_hash, doc in self.document_index.items():
            if doc["id"] == doc_id:
                doc["ai_analysis"] = analysis_data.get("analysis")
                doc["extracted_entities"] = analysis_data.get("entities", [])
                break

        return {
            "agent": self.agent_name,
            "status": "processed",
            "timestamp": datetime.now().isoformat(),
            "document_id": doc_id,
            "analysis_integrated": True
        }

    def _extract_metadata(self, doc_data: Dict) -> Dict[str, Any]:
        """
        Extract metadata from document.

        Args:
            doc_data: Document data

        Returns:
            Extracted metadata
        """
        metadata = {
            "filename": doc_data.get("filename", ""),
            "file_type": self._detect_file_type(doc_data.get("filename", "")),
            "file_size": doc_data.get("size", 0),
            "upload_source": doc_data.get("source", "unknown"),
            "created_date": doc_data.get("created_date"),
            "modified_date": doc_data.get("modified_date"),
            "author": doc_data.get("author"),
            "title": doc_data.get("title"),
            "page_count": doc_data.get("page_count")
        }

        # Extract metadata from filename
        filename_metadata = self._parse_filename(doc_data.get("filename", ""))
        metadata.update(filename_metadata)

        return metadata

    def _detect_file_type(self, filename: str) -> str:
        """
        Detect file type from filename.

        Args:
            filename: Name of the file

        Returns:
            File type
        """
        extension = filename.split(".")[-1].lower() if "." in filename else "unknown"

        file_type_map = {
            "pdf": "PDF Document",
            "docx": "Word Document",
            "doc": "Word Document",
            "txt": "Text Document",
            "xlsx": "Excel Spreadsheet",
            "xls": "Excel Spreadsheet",
            "pptx": "PowerPoint Presentation",
            "jpg": "Image",
            "jpeg": "Image",
            "png": "Image",
            "msg": "Email Message",
            "eml": "Email Message"
        }

        return file_type_map.get(extension, f"Unknown ({extension})")

    def _parse_filename(self, filename: str) -> Dict[str, Any]:
        """
        Parse metadata from filename.

        Args:
            filename: Name of the file

        Returns:
            Parsed metadata
        """
        import re

        metadata = {}

        # Look for dates in filename (YYYY-MM-DD or YYYYMMDD)
        date_patterns = [
            r"(\d{4})-(\d{2})-(\d{2})",
            r"(\d{4})(\d{2})(\d{2})"
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                year, month, day = match.groups()
                metadata["filename_date"] = f"{year}-{month}-{day}"
                break

        # Look for matter/case numbers
        matter_pattern = r"(?:matter|case|file)[-_]?(\d+)"
        match = re.search(matter_pattern, filename, re.IGNORECASE)
        if match:
            metadata["matter_number"] = match.group(1)

        return metadata

    def _classify_document(self, metadata: Dict) -> Dict[str, Any]:
        """
        Classify document based on metadata and content.

        Args:
            metadata: Document metadata

        Returns:
            Classification results
        """
        filename = metadata.get("filename", "").lower()
        file_type = metadata.get("file_type", "")

        scores = {}

        # Score against each category
        for category, keywords in self.document_taxonomy.items():
            score = sum(1 for keyword in keywords if keyword in filename)
            if score > 0:
                scores[category] = score

        # Determine primary and secondary categories
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        primary_category = sorted_categories[0][0] if sorted_categories else "uncategorized"
        secondary_categories = [cat for cat, score in sorted_categories[1:3]]

        return {
            "primary": primary_category,
            "secondary": secondary_categories,
            "confidence": scores.get(primary_category, 0) / 10.0,
            "all_scores": scores
        }

    def _generate_tags(self, metadata: Dict, classification: Dict) -> List[str]:
        """
        Generate suggested tags for document.

        Args:
            metadata: Document metadata
            classification: Document classification

        Returns:
            List of suggested tags
        """
        tags = []

        # Add category as tag
        tags.append(classification["primary"])
        tags.extend(classification["secondary"])

        # Add file type tag
        file_type = metadata.get("file_type", "")
        if file_type:
            tags.append(file_type.lower().replace(" ", "_"))

        # Add date-based tags
        if "filename_date" in metadata:
            date = metadata["filename_date"]
            year = date.split("-")[0]
            tags.append(f"year_{year}")

        # Add matter number tag if present
        if "matter_number" in metadata:
            tags.append(f"matter_{metadata['matter_number']}")

        return list(set(tags))  # Remove duplicates

    def _generate_file_path(self, classification: Dict, metadata: Dict) -> str:
        """
        Generate suggested file path for document.

        Args:
            classification: Document classification
            metadata: Document metadata

        Returns:
            Suggested file path
        """
        category = classification["primary"]
        filename = metadata.get("filename", "document")

        # Get year for organization
        year = datetime.now().year
        if "filename_date" in metadata:
            year = metadata["filename_date"].split("-")[0]

        # Get matter number if available
        matter = metadata.get("matter_number", "general")

        return f"/documents/{year}/{category}/{matter}/{filename}"

    def _generate_document_hash(self, doc_data: Dict) -> str:
        """
        Generate unique hash for document.

        Args:
            doc_data: Document data

        Returns:
            Document hash
        """
        # Create hash from filename + size + creation date
        hash_input = (
            f"{doc_data.get('filename', '')}"
            f"{doc_data.get('size', 0)}"
            f"{doc_data.get('created_date', '')}"
        )

        return hashlib.md5(hash_input.encode()).hexdigest()

    def _generate_filing_actions(self, document_record: Dict) -> List[str]:
        """
        Generate recommended filing actions.

        Args:
            document_record: Document record

        Returns:
            List of recommended actions
        """
        actions = []

        actions.append(f"File in: {document_record['file_path']}")
        actions.append(f"Apply tags: {', '.join(document_record['suggested_tags'])}")

        if document_record["classification"]["confidence"] < 0.5:
            actions.append("Manual review recommended - low classification confidence")

        return actions

    def _search_documents(self, query: str, filters: Dict) -> List[Dict]:
        """
        Search documents in the index.

        Args:
            query: Search query
            filters: Search filters

        Returns:
            List of matching documents
        """
        results = []
        query_lower = query.lower()

        for doc_hash, doc in self.document_index.items():
            # Simple text matching (can be enhanced with full-text search)
            if (query_lower in doc["filename"].lower() or
                query_lower in doc["classification"]["primary"] or
                any(query_lower in tag for tag in doc["suggested_tags"])):

                # Apply filters
                if self._matches_filters(doc, filters):
                    results.append(doc)

        return results

    def _matches_filters(self, doc: Dict, filters: Dict) -> bool:
        """
        Check if document matches search filters.

        Args:
            doc: Document record
            filters: Filter criteria

        Returns:
            True if document matches filters
        """
        if "category" in filters:
            if doc["classification"]["primary"] != filters["category"]:
                return False

        if "date_from" in filters:
            # TODO: Implement date filtering
            pass

        return True

    def _generate_search_suggestions(self, query: str) -> List[str]:
        """
        Generate search suggestions based on query.

        Args:
            query: Original search query

        Returns:
            List of suggested searches
        """
        suggestions = []

        # Suggest category searches
        for category in self.document_taxonomy.keys():
            if query.lower() in category or category in query.lower():
                suggestions.append(f"category:{category}")

        return suggestions[:5]

    def train(self, training_data: Dict[str, Any]):
        """
        Train the agent with filing patterns and taxonomy.

        Args:
            training_data: Dictionary containing:
                - taxonomy: Custom document taxonomy
                - filing_patterns: Common filing patterns
        """
        if "taxonomy" in training_data:
            self.document_taxonomy.update(training_data["taxonomy"])
            print(f"✓ Updated taxonomy: {len(training_data['taxonomy'])} categories")

        if "filing_patterns" in training_data:
            # Update filing patterns
            print(f"✓ Updated filing patterns")

        self.training_data = training_data
        print(f"✓ {self.agent_name} training completed")
