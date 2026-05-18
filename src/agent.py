"""
Core assembly of the single-agent orchestration workflow.
"""

import logging
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from src.tools.rag_tool import query_internal_financials
from src.tools.search_tool import live_web_search
from src.prompt_templates import get_agent_prompt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_agent_executor() -> AgentExecutor:
    """
    Assembles tools and initializes the deterministic LLM backbone.
    """
    logger.info("Initializing MarketMind Lite Agent Infrastructure...")
    
    # Define tools
    tools = [query_internal_financials, live_web_search]
    
    # Base LLM instantiation (Zero Temperature for strict financial extraction)
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    
    # Prompt Setup
    prompt = get_agent_prompt()
    
    # Use the modern, highly stable tool-calling agent factory
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Setup conversation memory
    memory = ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True,
        output_key="output"
    )
    
    # Compile runtime engine
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True
    )
    
    logger.info("AgentExecutor fully compiled.")
    return agent_executor