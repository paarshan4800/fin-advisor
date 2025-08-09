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
from agents.memory import conversation_memory
from utils.logger import setup_logger
from agents.llm import llm
from utils.json_formatter import _finalize_json

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
            get_query_filter_extractor_tool()
        ]
    
    def _create_agent(self):
        """Create the finance agent with tools"""
        system_prompt = """You are a helpful financial assistant. You can:
        1. Extract date ranges from natural language
        2. Query financial transaction data
        3. Categorize spending and identify patterns
        4. Prepare data for charts and tables

        CRITICAL: When you need data or filters, CALL TOOLS instead of writing JSON yourself.

        FINAL ANSWER FORMAT (respond ONLY in valid JSON for the final turn):
        - type: "table" or "chart"
        - chartType: "bar", "line", "pie", or "scatter" (if type is chart)
        - text_summary: Natural language summary
        - data: Formatted data for rendering

        Tool usage order (adapt as needed):
        - If the user asks anything about spending/transactions/money sent or otherwise needs data:
        1. Call `query_filter_extractor` to get filters.
        2. Call `mongo_query_tool` with those filters to fetch transactions.
        3. If the user's request implies categorization (e.g., breakdown by category, patterns, recs), call `category_mapper`.
        4. Call `chart_data_preparer` to produce the FINAL JSON.

        When calling `chart_data_preparer`, you MUST pass:
        {{
        "raw_data": <LIST of transaction records from mongo_query_tool>,
        "preferred_chart": <optional>,
        "objective": reason for aggregating data,
        "category_result": <optional; the entire output from category_mapper must be passed if it was used>
        }}

        Important rules:
        - Do NOT fabricate data—use tools to get it.
        - If `mongo_query_tool` returns no rows, return a minimal table with an explanatory text_summary.
        - Keep summaries conversational but concise.
        - Do not include any JSON in regular chat/tool-call turns; ONLY the final assistant turn should be JSON.
        """

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

            raw_output = result.get("output")
            resp = _finalize_json(raw_output)

            print(type(resp))
            print("resp", resp)

            # Store in memory
            if isinstance(resp, dict) and "text_summary" in resp:
                conversation_memory.add_interaction(session_id, user_input, resp["text_summary"])
            
            logger.info(f"Query processed successfully: {resp['type']}")
            return resp
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._error_response(str(e))
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            "type": "table",
            "chartType": None,
            "text_summary": f"I encountered an error processing your request: {error_message}",
            "data": [],
            "error": True
        }

# Global agent instance
finance_agent = FinanceAgent()