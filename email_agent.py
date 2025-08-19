from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from typing import Optional
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from classes import Email
import requests
import os

load_dotenv()


class AgentState(TypedDict):
    email: Email
    category: Optional[str] = None
    actions_needed: Optional[str] = None
    reasoning: Optional[str] = None


llm = ChatOpenAI(model="gpt-4o", temperature=0)


class classification(BaseModel):
    category: str
    actions_needed: str
    reasoning: str


def classification_agent(state: AgentState):
    with open("company_info/email_response_guide.txt", "r") as file:
        email_guide = file.read()

    sys_msg = SystemMessage(f"""You are an email classification agent that classifies emails based on intent. Your objective is to read the incoming email, and think carefully about what the intent is. 
                Then you assign the emails category, actions needed to respond including potential tool calls, and in short your reasoning behind it.
                Here is the email response guide:
                {email_guide}
    
                Here is the email:
                Subject: {state["email"].subject}
                body: {state["email"].body}
                email address: {state["email"].email}""")
    result = llm.with_structured_output(classification).invoke([sys_msg])
    return {"category": result.category, "actions_needed": result.actions_needed, "reasoning": result.reasoning}


def send_email_agent(state: AgentState):
    """
    Send email via HTTP POST request to a webhook
    """
    try:
        url = "https://hook.eu2.make.com/2ni3fi07m5b6x4ebqj4vsfiz58z256eh"
        data = {
            "To": state["email"].email,
            "subject": state["category"],
            "body": state["actions_needed"]
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
builder.add_node("send_email", send_email_agent)
builder.add_edge(START, "classification")
builder.add_edge("classification", "send_email")
builder.add_edge("send_email", END)
graph = builder.compile()


def main():
    result = graph.invoke({"email": Email(subject="Fråga om pris",
                                          body="Hej, jag undrar vad det skulle kosta med ett nytt set med lösnaglar", email="jhedenrud02@gmail.com")})
    print(result)


if __name__ == "__main__":
    main()
