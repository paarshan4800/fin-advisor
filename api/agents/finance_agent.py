from langchain.agents import create_openai_functions_agent, AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from typing import Dict, Any, List
from config.settings import settings
from tools.date_extractor import get_date_range_tool
from tools.mongo_query_tool import get_mongo_query_tool  
from tools.category_mapper import get_category_mapper_tool
from tools.chart_data_preparer import get_chart_data_preparer_tool
from tools.query_filter_extractor import get_query_filter_extractor_tool
from tools.mongo_projection_tool import get_mongo_projection_tool
from agents.memory import conversation_memory
from utils.logger import setup_logger
from agents.llm import llm
from utils.json_formatter import _finalize_json
from utils.helper import enhance_response
from agents.prompt import FINANCE_AGENT_SYSTEM_PROMPT

logger = setup_logger(__name__)

class FinanceAgent:
    """Main AI agent for financial queries"""
    
    def __init__(self):
        self.llm = llm
        self.tools = self._get_tools()
        self.agent = self._create_agent()
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
        logger.info("Finance agent initialized successfully")
    
    def _get_tools(self) -> List:
        """Get all available tools"""
        return [
            get_date_range_tool(),
            get_mongo_query_tool(),
            get_category_mapper_tool(),
            get_chart_data_preparer_tool(),
            get_query_filter_extractor_tool(),
            get_mongo_projection_tool()
        ]
    
    def _create_agent(self):
        """Create the finance agent with tools"""
        system_prompt = FINANCE_AGENT_SYSTEM_PROMPT
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
        ])

        if settings.LLM_PROVIDER == "openai":
            return create_openai_functions_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )
        else:
            return create_tool_calling_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=prompt
            )

    
    def process_query(self, user_input: str, session_id: str = "default") -> Dict[str, Any]:
        """Process user financial query"""
        logger.info(f"Processing query: {user_input}")
        
        try:
            # Get conversation context
            context = conversation_memory.get_context(session_id)
            
            # Process with agent
            result = self.executor.invoke({
                "input": user_input,
                "chat_history": context
            })

            resp = enhance_response(result)

            # raw_output = result.get("output")
            # resp = _finalize_json(raw_output)

            # Store in memory
            if isinstance(resp, dict) and "visualization" in resp and "text_summary" in resp["visualization"]:
                conversation_memory.add_interaction(session_id, user_input, resp["visualization"]["text_summary"])            

            # logger.info(f"Query processed successfully: {resp["visualization"]['type']}")
            logger.info(f"Query processed successfully")
            return resp
            
        except Exception as e:
            logger.exception(f"Error processing query: {e}")
            return self._error_response(str(e), user_input)
    
    def _error_response(self, error_message: str, user_input: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            "visualization": {
                "type": "table",
                "chartType": None,
                "text_summary": f"I encountered an error processing your request: {error_message}",
                "data": [],
            },
            "analysis": [],
            "query": user_input,
            "error": True
        }

# Global agent instance
finance_agent = FinanceAgent()