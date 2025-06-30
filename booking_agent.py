
import os
from typing import TypedDict, Annotated, List
from langchain.tools import Tool
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent
from calendar_utils import get_free_slots, create_event

# LLM Setup 
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.3,
    google_api_key=""
)

# Tool Wrappers 
def check_availability_tool(date: str, duration: int = 30):
    slots = get_free_slots(date, duration)
    return str(slots)

def book_event_tool(start: str, end: str, summary="Meeting", description="Booked by AGENT-Z"):
    event = create_event(summary, description, start, end)
    return f"Booked: {event.get('htmlLink')}"

# LangChain Tool Definition 
tools = [
    Tool.from_function(
        func=check_availability_tool,
        name="CheckCalendar",
        description="Check free time slots for a given date and duration"
    ),
    Tool.from_function(
        func=book_event_tool,
        name="BookCalendar",
        description="Book an event in the calendar with start and end datetime"
    )
]

#  AgentState for LangGraph 
class AgentState(TypedDict):
    input: str
    agent_scratchpad: Annotated[List[str], "Tool call history"]
    messages: Annotated[List[str], "Chat history"]
    

# Agent Creation 
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are AGENT-Z, a helpful calendar assistant."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


agent = create_tool_calling_agent(llm, tools, prompt=prompt)


def run_agent(state: AgentState):
    user_input = state["messages"][-1]  
    result = agent.invoke({
        "input": user_input,
        "agent_scratchpad": state.get("agent_scratchpad", []) 
    })

    return {
    "messages": state["messages"] + [result.get("output", "No output generated")],
    "agent_scratchpad": []
}




# Build LangGraph 
workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.set_entry_point("agent")
workflow.set_finish_point("agent")

agent_executor = workflow.compile()
