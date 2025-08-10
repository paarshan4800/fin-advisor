from typing import List, Dict, Any
from utils.logger import setup_logger
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime

logger = setup_logger(__name__)

class ConversationMemory:
    """Simple in-memory conversation storage"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_interaction(self, session_id: str, user_input: str, assistant_response: str) -> None:
        """Add user-assistant interaction to memory"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        interaction = {
            "user_input": user_input,
            "assistant_response": assistant_response,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[session_id].append(interaction)
        
        # Keep only last N interactions
        if len(self.conversations[session_id]) > self.max_history:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history:]
        
        logger.info(f"Added interaction to memory for session {session_id}")
    
    def get_context(self, session_id: str) -> List:
        """Get conversation context for session"""
        if session_id not in self.conversations:
            return []
        
        messages = []
        for interaction in self.conversations[session_id]:
            messages.append(HumanMessage(content=interaction["user_input"]))
            messages.append(AIMessage(content=interaction["assistant_response"]))
        
        return messages

# Global memory instance
conversation_memory = ConversationMemory()