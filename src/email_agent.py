import email
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from classes import Email, AgentState, classification_output
from tools import get_price_and_service_list, book_appointment, reschedule_appointment, tool_node, create_quote, get_general_info, cancel_appointment
import requests


load_dotenv()


llm = ChatOpenAI(model="gpt-4o", temperature=0)


def classification_agent(state: AgentState):
    print("=== CLASSIFICATION AGENT ===")
    print(f"Processing email from: {state['email'].email}")
    print(f"Subject: {state['email'].subject}")
    print(f"Body: {state['email'].body}")
    
    analysis_sys_msg = SystemMessage(f"""You are an email categorizing agent for a Swedish auto repair shop. You are exceptional at understanding customer intent and your job is to classify the email as one of these 3 categories.
    1. Booking questions - these are all questions that regard a booking or where the customers intent is to make a booking, remove a booking, or change an existing booking.
    2. Price and service questions and quotes - any questions about the services the auto shop provides, the prices for services. Any questions regarding quotes for services or products, and any other product or service related question.
    3. General/other inquiries - any email that does not fall in to the first two categories, such as general FAQ questions, opening times, logistics questions, and other.
    
    Think carefully about what the customers intent is, if the email can fit into multiple categories, e.g a question about price and intent to book a service. Output both categories.
    Output the category/categories for the email, as well as short reasoning for the categoriation""")
    email_message = HumanMessage(
    f"""Email to categorize:
    Subject: {state["email"].subject}
    Body: {state["email"].body}
    Email address: {state["email"].email}""")
    # Get the agent's analysis and tool usage decision
    category_result = llm.with_structured_output(classification_output).invoke([analysis_sys_msg, email_message])
    
    print(f"Classification result: {category_result.category}")
    print(f"Reasoning: {category_result.reasoning}")
    print("=== END CLASSIFICATION AGENT ===\n")

    return {"category": category_result}

def category_condition(state: AgentState):
    if state["category"].category == "Booking inquiries":
        return "booking_agent"
    elif state["category"].category == "Price or service inquiries":
        return "service_agent"
    else:
        return "general_agent"
    
booking_tools = [book_appointment, reschedule_appointment, cancel_appointment]
booking_llm = llm.bind_tools(booking_tools)

def booking_agent(state: AgentState):
    print("=== BOOKING AGENT ===")
    print(f"Processing email from: {state['email'].email}")
    print(f"Subject: {state['email'].subject}")
    print(f"Body: {state['email'].body}")
    booking_sys_msg = SystemMessage(f"""You are an email agent for a Swedish auto repair shop that specialises in emails that regard bookings. 
    You are exceptional at understanding customer intent and your job is to use one of your tools to book an appointment, rebook an appointment or cancel an appointment depending on the customers intent.
    You will be given an email with a customer's email regarding a booking.
    You must decide id the user wants to book, rebook or cancel.
    You must then see if the email contains all necesary information to use the specific booking tool for this inquiry.
    If the email does not contain all necesary information, you must ask the user for the missing information.
    If the email contains all necesary information, you must use the specific booking tool to book an appointment, rebook an appointment or cancel an appointment.
    You must then respond back to the email to the user with the result of the booking tool.""")
    
    # If we have existing messages, use them as conversation history
    if state.get("messages"):
        # Use existing conversation history
        messages = [booking_sys_msg] + state["messages"]
        booking_result = booking_llm.invoke(messages)
    else:
        # First time processing - create new conversation
        booking_email = HumanMessage(f"""Email to process:
        Subject: {state["email"].subject}
        Body: {state["email"].body}
        Email address: {state["email"].email}""")
        booking_result = booking_llm.invoke([booking_sys_msg, booking_email])
    
    print("booking_result", booking_result)
    print("=== END BOOKING AGENT ===\n")
    
    # Update messages with the new result
    if state.get("messages"):
        updated_messages = state["messages"] + [booking_result]
    else:
        updated_messages = [booking_sys_msg, booking_email, booking_result]
    
    return {"messages": updated_messages, "email_response": booking_result.content}

quote_tool = [create_quote]
service_llm = llm.bind_tools(quote_tool)

def service_agent(state: AgentState):
    print("=== SERVICE AGENT ===")
    print(f"Processing email from: {state['email'].email}")
    print(f"Subject: {state['email'].subject}")
    print(f"Body: {state['email'].body}")
    service_sys_msg = SystemMessage(f"""You are an email agent for a Swedish auto repair shop that specialises in emails that regard questions about services, products and prices.
    Your job is to use the provided price and service list to answer the customers question, and respond to the customers question.
    If the customers requests price information about a service that is not specifically in the service list, you must use the quote tool.
    You must then respond to the email with either information from the service list, or from the quote tool.
    Here is the service list with prices:
    {get_price_and_service_list()}
    """)
    
    # If we have existing messages, use them as conversation history
    if state.get("messages"):
        # Use existing conversation history
        messages = [service_sys_msg] + state["messages"]
        service_result = service_llm.invoke(messages)
    else:
        # First time processing - create new conversation
        customer_email = HumanMessage(f"""Email to process:
        Subject: {state["email"].subject}
        Body: {state["email"].body}
        Email address: {state["email"].email}""")
        service_result = service_llm.invoke([service_sys_msg, customer_email])
    
    print("=== END SERVICE AGENT ===\n")
    
    # Update messages with the new result
    if state.get("messages"):
        updated_messages = state["messages"] + [service_result]
    else:
        updated_messages = [service_sys_msg, customer_email, service_result]
    
    return {"messages": updated_messages, "email_response": service_result.content}


def general_agent(state: AgentState):
    print("=== GENERAL AGENT ===")
    print(f"Processing email from: {state['email'].email}")
    print(f"Subject: {state['email'].subject}")
    print(f"Body: {state['email'].body}")
    general_sys_msg = SystemMessage(f"""You are an email agent for a Swedish auto repair shop that specialises in emails that regard general inquiries.
    Your job is to use the provided general information to answer the customers question, and respond to the customers question
    If the customers requests information that is not specifically in the general information, you must simply repond "human review needed".
    
    Here is the general information:
    {get_general_info()}
    """)
    
    # If we have existing messages, use them as conversation history
    if state.get("messages"):
        # Use existing conversation history
        messages = [general_sys_msg] + state["messages"]
        general_result = llm.invoke(messages)
    else:
        # First time processing - create new conversation
        customer_email = HumanMessage(f"""Email to process:
        Subject: {state["email"].subject}
        Body: {state["email"].body}
        Email address: {state["email"].email}""")
        general_result = llm.invoke([general_sys_msg, customer_email])
    
    print("=== END GENERAL AGENT ===\n")
    
    # Update messages with the new result
    if state.get("messages"):
        updated_messages = state["messages"] + [general_result]
    else:
        updated_messages = [general_sys_msg, customer_email, general_result]
    
    return {"messages": updated_messages, "email_response": general_result.content}

def tool_conditional(state: AgentState):
    print("=== TOOL CONDITIONAL ===")
    print(f"Checking if last message has tool calls...")
    
    # Check if any message in the history has tool calls
    has_tool_calls = False
    if state["messages"]:
        # Look for ToolMessages in last message
        if isinstance(state["messages"][-1], ToolMessage):
            has_tool_calls = True
    
    if has_tool_calls:
        print("Tool calls detected - routing back to appropriate agent")
        # Route back to the agent based on the original classification
        if state["category"].category == "Booking inquiries":
            print("Routing back to booking_agent")
            print("=== END TOOL CONDITIONAL ===\n")
            return "booking_agent"
        elif state["category"].category == "Price or service inquiries":
            print("Routing back to service_agent")
            print("=== END TOOL CONDITIONAL ===\n")
            return "service_agent"
        else:
            print("Routing back to general_agent")
            print("=== END TOOL CONDITIONAL ===\n")
            return "general_agent"
    else:
        print("No tool calls - routing to send_email")
        print("=== END TOOL CONDITIONAL ===\n")
        return "send_email"  # If no tool calls, still send the email response

def send_email_step(state: AgentState):
    print("=== SEND EMAIL STEP ===")
    print(f"Preparing to send email to: {state['email'].email}")
    print(f"Subject: RE: {state['email'].subject}")
    print(f"Response content: {state['email_response']}")

    """
    Send email via HTTP POST request to a webhook
    """
    try:
        url = "https://hook.eu2.make.com/2ni3fi07m5b6x4ebqj4vsfiz58z256eh"
        data = {
            "To": state["email"].email,
            "subject": f"RE: {state["email"].subject}",
            "body": state["email_response"]
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

            print("=== END SEND EMAIL STEP ===\n")
            return {
                "email_sent": True,
                "status_code": response.status_code,
                "message": "Email sent successfully via webhook"
            }
        else:
            print(f"Error: {response.status_code}, {response.text}")
            print("=== END SEND EMAIL STEP ===\n")
            return {
                "email_sent": False,
                "status_code": response.status_code,
                "error": response.text
            }

    except requests.exceptions.RequestException as e:
        print(f"Network error while sending email: {e}")
        print("=== END SEND EMAIL STEP ===\n")
        return {
            "email_sent": False,
            "error": f"Network error: {str(e)}"
        }
    except Exception as e:
        print(f"Unexpected error while sending email: {e}")
        print("=== END SEND EMAIL STEP ===\n")
        return {
            "email_sent": False,
            "error": f"Unexpected error: {str(e)}"
        }

#nodes
builder = StateGraph(AgentState)
builder.add_node("classification", classification_agent)
builder.add_node("tool", tool_node)
builder.add_node("booking_agent", booking_agent)
builder.add_node("service_agent", service_agent)
builder.add_node("general_agent", general_agent)
builder.add_node("send_email", send_email_step)

#edges
builder.add_edge(START, "classification")
builder.add_conditional_edges("classification", category_condition, {"booking_agent": "booking_agent", "service_agent": "service_agent", "general_agent": "general_agent"})
builder.add_edge("booking_agent", "tool")
builder.add_edge("service_agent", "tool")
builder.add_edge("general_agent", "tool")
builder.add_conditional_edges("tool", tool_conditional, {"booking_agent": "booking_agent", "service_agent": "service_agent", "general_agent": "general_agent", "send_email": "send_email"})
builder.add_edge("send_email", END)



graph = builder.compile()


def main():
    result = graph.invoke({"email": Email(subject="Boka tid för besiktning",
    body="Hej jag skulle vilja boka en tid för besiktning den 21a augusti kl 15, finns det en ledig tid? Mvh Jonathan", email="jhedenrud02@gmail.com")})
    print(result)
    
    try:
        mermaid_png = graph.get_graph(xray=True).draw_mermaid_png()
        with open("graph_visualization.png", "wb") as f:
            f.write(mermaid_png)
        print("Graph visualization saved as graph_visualization.png")
    except Exception as e:
        print(f"Could not save Mermaid graph: {e}")
    print("=== END MAIN ===")


if __name__ == "__main__":
    main()
