"""
Claude AI Integration Service

Provides integration with Anthropic's Claude API for intelligent document
analysis, metadata extraction, and natural language processing.
"""

import os
from typing import Any, Dict, List, Optional
import json

try:
    import anthropic
except ImportError:
    anthropic = None
    print("⚠ anthropic package not installed. Install with: pip install anthropic")


class ClaudeIntelligenceService:
    """
    Service for integrating Claude AI capabilities into AGENTTA.

    Provides methods for document analysis, metadata extraction,
    entity recognition, and intelligent text processing.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude Intelligence Service.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        if anthropic is None:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Model configurations
        self.default_model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 4096

    async def extract_document_metadata(
        self,
        document_text: str,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract structured metadata from a document.

        Args:
            document_text: The document text to analyze
            document_type: Optional document type hint (e.g., "contract", "email")

        Returns:
            Dictionary containing extracted metadata
        """
        system_prompt = """You are a legal document analysis expert. Extract structured metadata from documents.

Return a JSON object with the following fields:
- title: Document title or subject
- document_type: Type of document (contract, letter, memo, etc.)
- date: Any dates mentioned (ISO format)
- parties: List of parties involved
- key_terms: Important terms or concepts
- action_items: Any action items or deadlines
- summary: Brief summary (2-3 sentences)
- entities: List of named entities (people, organizations, places)
"""

        user_message = f"Analyze this document and extract metadata:\n\n{document_text[:10000]}"

        if document_type:
            user_message = f"Document type hint: {document_type}\n\n{user_message}"

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Parse the response
            content = response.content[0].text

            # Try to extract JSON from the response
            metadata = self._parse_json_response(content)

            return {
                "success": True,
                "metadata": metadata,
                "model": response.model,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def analyze_email_content(self, email_body: str, subject: str) -> Dict[str, Any]:
        """
        Analyze email content for intelligent triage.

        Args:
            email_body: Email body text
            subject: Email subject line

        Returns:
            Dictionary with email analysis
        """
        system_prompt = """You are an email triage assistant. Analyze emails and provide structured insights.

Return a JSON object with:
- priority: high, medium, or low
- sentiment: positive, neutral, or negative
- requires_response: boolean
- urgency: critical, high, medium, or low
- category: type of email (request, information, action, etc.)
- key_points: list of key points
- suggested_action: what should be done
"""

        user_message = f"Subject: {subject}\n\nBody:\n{email_body}"

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            content = response.content[0].text
            analysis = self._parse_json_response(content)

            return {
                "success": True,
                "analysis": analysis,
                "model": response.model
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract named entities from text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with extracted entities
        """
        system_prompt = """Extract named entities from the text. Return a JSON object with:
- people: List of person names
- organizations: List of organization names
- locations: List of places
- dates: List of dates
- money: List of monetary amounts
- case_numbers: List of case or matter numbers
"""

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": text[:5000]
                    }
                ]
            )

            content = response.content[0].text
            entities = self._parse_json_response(content)

            return {
                "success": True,
                "entities": entities
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def summarize_document(
        self,
        document_text: str,
        max_length: int = 200
    ) -> Dict[str, Any]:
        """
        Generate a summary of a document.

        Args:
            document_text: Text to summarize
            max_length: Maximum length of summary in words

        Returns:
            Dictionary with summary
        """
        system_prompt = f"""Summarize the following document in {max_length} words or less.
Focus on key points, main arguments, and important details."""

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": document_text[:15000]
                    }
                ]
            )

            summary = response.content[0].text

            return {
                "success": True,
                "summary": summary,
                "word_count": len(summary.split())
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def classify_document(self, document_text: str) -> Dict[str, Any]:
        """
        Classify a document into categories.

        Args:
            document_text: Text to classify

        Returns:
            Dictionary with classification results
        """
        system_prompt = """Classify this document. Return a JSON object with:
- primary_category: main category (contract, correspondence, court_filing, research, etc.)
- confidence: confidence score 0-1
- subcategories: list of relevant subcategories
- legal_domain: area of law if applicable
"""

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": document_text[:5000]
                    }
                ]
            )

            content = response.content[0].text
            classification = self._parse_json_response(content)

            return {
                "success": True,
                "classification": classification
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_response_draft(
        self,
        original_message: str,
        context: Optional[str] = None,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a draft response to a message.

        Args:
            original_message: The message to respond to
            context: Additional context for the response
            tone: Desired tone (professional, friendly, formal)

        Returns:
            Dictionary with generated response
        """
        system_prompt = f"""Generate a {tone} response to the following message.
Keep it clear, concise, and appropriate for professional legal correspondence."""

        user_message = f"Original message:\n{original_message}"

        if context:
            user_message += f"\n\nAdditional context:\n{context}"

        try:
            response = self.client.messages.create(
                model=self.default_model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            draft = response.content[0].text

            return {
                "success": True,
                "draft": draft
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from Claude's response.

        Args:
            response_text: Response text from Claude

        Returns:
            Parsed JSON object
        """
        try:
            # Try to parse the entire response as JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re

            json_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
            matches = re.findall(json_pattern, response_text, re.DOTALL)

            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass

            # If that fails, try to find any JSON object
            json_pattern = r"\{.*\}"
            matches = re.findall(json_pattern, response_text, re.DOTALL)

            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass

            # If all parsing fails, return the raw text
            return {"raw_response": response_text}

    async def batch_process_documents(
        self,
        documents: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Process multiple documents in batch.

        Args:
            documents: List of document dictionaries with 'text' and optional 'type'

        Returns:
            List of analysis results
        """
        results = []

        for doc in documents:
            result = await self.extract_document_metadata(
                document_text=doc.get("text", ""),
                document_type=doc.get("type")
            )

            results.append({
                "document_id": doc.get("id"),
                "result": result
            })

        return results

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model configuration.

        Returns:
            Model configuration details
        """
        return {
            "model": self.default_model,
            "max_tokens": self.max_tokens,
            "api_configured": bool(self.api_key)
        }
