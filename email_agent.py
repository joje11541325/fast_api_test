from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from pydantic import BaseModel
from typing import Optional
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from classes import Email

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
    print(sys_msg)
    result = llm.with_structured_output(classification).invoke([sys_msg])
    return {"category": result.category, "actions_needed": result.actions_needed, "reasoning": result.reasoning}


builder = StateGraph(AgentState)
builder.add_node("classification", classification_agent)
builder.add_edge(START, "classification")
builder.add_edge("classification", END)
graph = builder.compile()


def main():
    result = graph.invoke({"email": Email(subject="Fråga om pris",
                                          body="Hej, jag undrar vad det skulle kosta med ett nytt set med lösnaglar", email="john@example.com")})
    print(result)


if __name__ == "__main__":
    main()
