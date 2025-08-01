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
from agents.memory import conversation_memory
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FinanceAgent:
    """Main AI agent for financial queries"""
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.tools = self._get_tools()
        self.agent = self._create_agent()
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
        logger.info("Finance agent initialized successfully")
    
    def _initialize_llm(self):
        """Initialize LLM based on configuration"""
        if settings.LLM_PROVIDER == "openai":
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            return ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0
            )
    
    def _get_tools(self) -> List:
        """Get all available tools"""
        return [
            get_date_range_tool(),
            get_mongo_query_tool(),
            get_category_mapper_tool(),
            get_chart_data_preparer_tool()
        ]
    
    def _create_agent(self):
        """Create the finance agent with tools"""
        system_prompt = """You are a helpful financial assistant. You can:
        1. Extract date ranges from natural language
        2. Query financial transaction data
        3. Categorize spending and identify patterns
        4. Prepare data for charts and tables
        
        Always provide structured responses with:
        - type: "table" or "chart"
        - chartType: "bar", "line", "pie", or "scatter" (if type is chart)
        - text_summary: Natural language summary
        - data: Formatted data for rendering
        
        Use the available tools to gather and process information before responding.
        Be conversational and helpful in your summaries.
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
            
            # Format response
            formatted_response = self._format_response(result["output"], user_input)
            
            # Store in memory
            conversation_memory.add_interaction(
                session_id, 
                user_input, 
                formatted_response["text_summary"]
            )
            
            logger.info(f"Query processed successfully: {formatted_response['type']}")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return self._error_response(str(e))
    
    def _format_response(self, agent_output: str, user_input: str) -> Dict[str, Any]:
        """Format agent output into structured response"""
        
        # Determine response type based on query
        if any(word in user_input.lower() for word in ["chart", "graph", "visual", "show"]):
            response_type = "chart"
            chart_type = self._determine_chart_type(user_input)
        else:
            response_type = "table" 
            chart_type = None
        
        # Generate sample data based on query type
        if "category" in user_input.lower() or "categorize" in user_input.lower():
            data = self._get_category_data()
            chart_type = "pie" if response_type == "chart" else None
        elif "spending" in user_input.lower() and "week" in user_input.lower():
            data = self._get_weekly_spending_data()
            chart_type = "line" if response_type == "chart" else None
        else:
            data = self._get_transaction_data()
        
        return {
            "type": response_type,
            "chartType": chart_type,
            "text_summary": agent_output,
            "data": data
        }
    
    def _determine_chart_type(self, query: str) -> str:
        """Determine appropriate chart type for query"""
        if "category" in query.lower() or "breakdown" in query.lower():
            return "pie"
        elif "trend" in query.lower() or "over time" in query.lower():
            return "line"
        elif "compare" in query.lower():
            return "bar"
        else:
            return "bar"  # default
    
    def _get_category_data(self) -> List[Dict[str, Any]]:
        """Sample category spending data"""
        return [
            {"label": "Food & Dining", "value": 15000, "color": "#FF6384"},
            {"label": "Transportation", "value": 8000, "color": "#36A2EB"},
            {"label": "Shopping", "value": 12000, "color": "#FFCE56"},
            {"label": "Utilities", "value": 5000, "color": "#4BC0C0"},
            {"label": "Entertainment", "value": 3000, "color": "#9966FF"}
        ]
    
    def _get_weekly_spending_data(self) -> List[Dict[str, Any]]:
        """Sample weekly spending data"""
        return [
            {"date": "2024-01-01", "amount": 5000},
            {"date": "2024-01-02", "amount": 7000},
            {"date": "2024-01-03", "amount": 4500},
            {"date": "2024-01-04", "amount": 8000},
            {"date": "2024-01-05", "amount": 6200},
            {"date": "2024-01-06", "amount": 9100},
            {"date": "2024-01-07", "amount": 5800}
        ]
    
    def _get_transaction_data(self) -> List[List[Any]]:
        """Sample transaction table data"""
        return [
            ["Date", "Description", "Category", "Amount"],
            ["2024-01-01", "Restaurant expense", "Food & Dining", 2500],
            ["2024-01-02", "Uber ride", "Transportation", 450],
            ["2024-01-03", "Grocery shopping", "Food & Dining", 3200],
            ["2024-01-04", "Electric bill", "Utilities", 1200],
            ["2024-01-05", "Movie tickets", "Entertainment", 800]
        ]
    
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