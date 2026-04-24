"""
Context Service for managing conversation history.
Provides context-aware assistance by maintaining and retrieving message history.
"""
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from src.config import Settings
from src.models import ChatMessage, ContextMessage, ContextSummary, MessageRole
from src.utils import get_logger

logger = get_logger(__name__)


class ContextService:
    """
    Service for managing conversation context.
    Stores message history per session and provides intelligent context retrieval.
    """

    def __init__(self, settings: Settings):
        """
        Initialize context service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.max_messages = settings.max_context_messages

        # In-memory storage: session_id -> List[ContextMessage]
        # For production, consider using Redis for persistence
        self.contexts: Dict[str, List[ContextMessage]] = defaultdict(list)

        logger.info(
            "Context service initialized",
            max_messages=self.max_messages,
        )

    async def add_message(
        self,
        session_id: str,
        role,  # Can be MessageRole enum or str
        content: str,
        metadata: Optional[Dict] = None,
    ):
        """
        Add a message to session context.

        Args:
            session_id: Session ID
            role: Message role (user/assistant/system) - enum or string
            content: Message content
            metadata: Optional metadata
        """
        # Handle both enum and string role inputs
        if isinstance(role, str):
            # Convert string to enum
            role = MessageRole(role)

        message = ContextMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )

        self.contexts[session_id].append(message)

        # Trim to max messages if exceeded
        if len(self.contexts[session_id]) > self.max_messages:
            # Keep system message (if first) + recent messages
            messages = self.contexts[session_id]
            if messages[0].role == MessageRole.SYSTEM:
                self.contexts[session_id] = [messages[0]] + messages[-(self.max_messages - 1):]
            else:
                self.contexts[session_id] = messages[-self.max_messages:]

        logger.debug(
            "Message added to context",
            session_id=session_id,
            role=role,
            content_length=len(content),
            total_messages=len(self.contexts[session_id]),
        )

    async def get_context(
        self,
        session_id: str,
        max_tokens: Optional[int] = None,
    ) -> List[ChatMessage]:
        """
        Get conversation context for a session.

        Args:
            session_id: Session ID
            max_tokens: Optional token limit (approximate)

        Returns:
            List of ChatMessage objects

        Note:
            If max_tokens is provided, messages are trimmed from oldest to newest
            while keeping system message and ensuring we don't exceed token limit.
        """
        messages = self.contexts.get(session_id, [])

        if not messages:
            return []

        # Convert to ChatMessage format
        chat_messages = [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in messages
        ]

        # Simple token approximation: ~4 chars per token
        if max_tokens:
            total_chars = sum(len(msg.content) for msg in chat_messages)
            estimated_tokens = total_chars // 4

            if estimated_tokens > max_tokens:
                # Keep system message if present, trim others
                first_role = chat_messages[0].role
                # Handle both enum and string forms
                is_system = (first_role == MessageRole.SYSTEM or
                           first_role == "system" or
                           (hasattr(first_role, "value") and first_role.value == "system"))

                if is_system:
                    system_msg = chat_messages[0]
                    other_msgs = chat_messages[1:]

                    # Trim from beginning
                    while other_msgs and estimated_tokens > max_tokens:
                        removed = other_msgs.pop(0)
                        total_chars -= len(removed.content)
                        estimated_tokens = total_chars // 4

                    chat_messages = [system_msg] + other_msgs
                else:
                    # Trim from beginning
                    while chat_messages and estimated_tokens > max_tokens:
                        removed = chat_messages.pop(0)
                        total_chars -= len(removed.content)
                        estimated_tokens = total_chars // 4

        logger.info(
            "Context retrieved",
            session_id=session_id,
            message_count=len(chat_messages),
        )

        return chat_messages

    async def get_summary(self, session_id: str) -> ContextSummary:
        """
        Get a summary of session context.

        Args:
            session_id: Session ID

        Returns:
            ContextSummary with statistics
        """
        messages = self.contexts.get(session_id, [])

        total_chars = sum(len(msg.content) for msg in messages)
        estimated_tokens = total_chars // 4

        # Extract key topics from messages (simple keyword extraction)
        key_topics = self._extract_key_topics(messages)

        return ContextSummary(
            session_id=session_id,
            message_count=len(messages),
            token_count=estimated_tokens,
            key_topics=key_topics,
        )

    def _extract_key_topics(self, messages: List[ContextMessage]) -> List[str]:
        """
        Extract key topics from messages (simple keyword extraction).

        Args:
            messages: List of context messages

        Returns:
            List of key topic keywords
        """
        # Common coding interview topics
        topics_keywords = {
            "arrays": ["array", "list", "vector"],
            "hash-maps": ["hash", "map", "dict", "hashmap", "dictionary"],
            "trees": ["tree", "binary tree", "bst", "node"],
            "graphs": ["graph", "dfs", "bfs", "adjacency"],
            "sorting": ["sort", "quicksort", "mergesort", "heapsort"],
            "dynamic-programming": ["dp", "dynamic programming", "memoization"],
            "recursion": ["recursive", "recursion", "backtrack"],
            "strings": ["string", "substring", "character"],
            "linked-lists": ["linked list", "linkedlist", "node"],
            "system-design": ["system design", "scalability", "distributed"],
        }

        found_topics = set()
        content_lower = " ".join(msg.content.lower() for msg in messages)

        for topic, keywords in topics_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                found_topics.add(topic)

        return list(found_topics)[:5]  # Return top 5 topics

    async def clear_context(self, session_id: str):
        """
        Clear all context for a session.

        Args:
            session_id: Session ID
        """
        if session_id in self.contexts:
            message_count = len(self.contexts[session_id])
            del self.contexts[session_id]

            logger.info(
                "Context cleared",
                session_id=session_id,
                messages_removed=message_count,
            )

    async def get_last_n_messages(
        self,
        session_id: str,
        n: int = 5,
    ) -> List[ChatMessage]:
        """
        Get last N messages from context.

        Args:
            session_id: Session ID
            n: Number of messages to retrieve

        Returns:
            List of last N ChatMessage objects
        """
        messages = self.contexts.get(session_id, [])
        recent_messages = messages[-n:] if len(messages) > n else messages

        return [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in recent_messages
        ]

    async def health_check(self) -> bool:
        """
        Check if context service is healthy.

        Returns:
            True if healthy
        """
        return True
