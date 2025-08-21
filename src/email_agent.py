from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel
from typing import Optional
from typing import TypedDict
from langgraph.graph import StateGraph, START, END, MessagesState
from dotenv import load_dotenv
from classes import Email
from tools import get_price_list, get_services_list, get_opening_hours, check_availability, book_appointment, reschedule_appointment
import requests
import os

load_dotenv()


class AgentState(MessagesState):
    email: Email
    category: Optional[str] = None
    actions_needed: Optional[str] = None
    reasoning: Optional[str] = None
    tool_results: Optional[list] = None


class classification(BaseModel):
    category: str
    actions_needed: str
    reasoning: str


llm = ChatOpenAI(model="gpt-4o", temperature=0)
# Import all tools from tools.py
tools = [get_price_list, get_services_list, get_opening_hours,
         check_availability, book_appointment, reschedule_appointment]
tool_llm = llm.bind_tools(tools)


def classification_agent(state: AgentState):
    with open("company_info/email_response_guide.txt", "r") as file:
        email_guide = file.read()

    # First, let the agent analyze the email and decide if tools are needed
    analysis_sys_msg = SystemMessage(f"""You are an email agent for a Swedish nail salon that answers inquiries and questions and books and changes appointments. 
    
    Your first task is to analyze the incoming email and determine:
    1. What the customer is asking for
    2. Whether you need to use any tools to get information before responding
    3. What tools would be most helpful
    
    Available tools:
    - get_price_list: Use when customers ask about prices or costs
    - get_services_list: Use when customers ask about available services
    - get_opening_hours: Use when customers ask about when you're open
    - check_availability: Use when customers want to check if a time slot is available
    - book_appointment: Use when customers want to schedule an appointment
    - reschedule_appointment: Use when customers want to change an existing appointment
    
    Email response guide:
    {email_guide}
    
    Email to analyze:
    Subject: {state["email"].subject}
    Body: {state["email"].body}
    Email address: {state["email"].email}
    
    Think step by step about what the customer needs and which tools would help you provide the best response.""")

    # Get the agent's analysis and tool usage decision
    analysis_result = tool_llm.invoke([analysis_sys_msg])

    return {"messages": [analysis_result]}


def tool_node(state: AgentState):
    if state["messages"][-1].tool_calls:
        for tool_call in state["messages"][-1].tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_result = tools[tool_name](**tool_args)
            state["tool_results"].append(tool_result)
    return {"messages": [state["messages"][-1]]}


def write_email_agent(state: AgentState):
    if state["tool_results"]:
        state["email"].body = state["tool_results"]
    return {"messages": [state["messages"][-1]]}


def send_email_agent(state: AgentState):
    """
    Send email via HTTP POST request to a webhook
    """
    try:
        url = "https://hook.eu2.make.com/2ni3fi07m5b6x4ebqj4vsfiz58z256eh"
        data = {
            "To": state["email"].email,
            "subject": state["email"].subject,
            "body": state["email"].body
        }
        print(f"data for email: {data}")
        response = requests.post(url, json=data, timeout=30)

        if response.status_code == 200:
            print("Success: Email sent via webhook")
            # Try to parse JSON response, but don't fail if it's not JSON
            try:
                response_data = response.json()
                print("Response data:", response_data)
            except requests.exceptions.JSONDecodeError:
                print("Response text:", response.text)

            return {
                "email_sent": True,
                "status_code": response.status_code,
                "message": "Email sent successfully via webhook"
            }
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return {
                "email_sent": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except requests.exceptions.RequestException as e:
        print(f"Network error while sending email: {e}")
        return {
            "email_sent": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        print(f"Unexpected error while sending email: {e}")
        return {
            "email_sent": False,
            "error": f"Unexpected error: {str(e)}"
        }


builder = StateGraph(AgentState)
builder.add_node("classification", classification_agent)
builder.add_node("tool", tool_node)
builder.add_node("send_email", send_email_agent)
builder.add_edge(START, "classification")
builder.add_edge("classification", "tool")
builder.add_edge("tool", "send_email")
builder.add_edge("send_email", END)
graph = builder.compile()


def main():
    result = graph.invoke({"email": Email(subject="Fråga om pris",
                                          body="Hej, jag undrar vad det skulle kosta med ett nytt set med lösnaglar", email="jhedenrud02@gmail.com")})
    print(result)


if __name__ == "__main__":
    main()
