from langchain_core.tools import tool
from typing import Optional
import datetime
import requests
from classes import AgentState, tool_calls


def get_price_and_service_list() -> str:
    """
    Returns a very detailed list of the auto repair shops services including prices.
    Use this when customers ask about prices, costs, or  information about services.
    """
    try:
        with open("company_info/prislista.txt", "r", encoding="utf-8") as file:
            price_list = file.read()
        return f"Here is our current price list:\n\n{price_list}"
    except FileNotFoundError:
        return "Price list not available at the moment. Please contact us directly for pricing information."





def get_general_info() -> str:
    """
    Returns the general information for the auto repair shop.
    Use this when customers ask about general information, such as opening hours, location, contact information, etc.
    """
    try:
        with open("company_info/general_info.txt", "r", encoding="utf-8") as file:
            general_info = file.read()
        return general_info
    except FileNotFoundError:
        return "General information not available at the moment. Please contact us directly for information."   

@tool
def check_availability(from_date: str, to_date: str) -> str:
    """
    Check availability for a specific date and time.
    Use this when customers want to book an appointment.

    Args:
        from_date: The start date in format YYYY-MM-DD HH:MM
        to_date: The end date in format YYYY-MM-DD HH:MM
    """
    # This is a placeholder - in a real implementation, you'd check against a booking system
    from_date = str(from_date)
    to_date = str(to_date)
    try:
        url = "https://hook.eu2.make.com/1g5yvvf6j38zha7ncnm9jafsv05lq9iu"
        data = {
            "from_date": from_date,
            "to_date": to_date
        }
        print(f"data for availability check: {data}")
        response = requests.post(url, json=data, timeout=30)
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 200:
            # Check if response has content before trying to parse JSON
            if response.text.strip():
                try:
                    return response.json()
                except ValueError as json_error:
                    return f"Availability check completed but received invalid response: {response.text}"
            else:
                return "Availability check completed successfully (no data returned)"
        else:
            return f"Availability check failed with status code: {response.status_code}"
    except Exception as e:
        return f"Availability check failed: {e}"


@tool
def book_appointment(customer_name: str, service: str, date: str, time: str, email: str) -> str:
    """
    Book an appointment for a customer.
    Use this when customers want to schedule an appointment.

    Args:
        customer_name: The name of the customer
        service: The service they want to book
        date: The date in format YYYY-MM-DD
        time: The time in format HH:MM (24-hour format)
        email: The customer's email address
    """
    # This is a placeholder - in a real implementation, you'd integrate with a booking system
    return f"Appointment booked for {customer_name} on {date} at {time} for {service}. A confirmation email has been sent to {email}."


@tool
def reschedule_appointment(original_date: str, original_time: str, new_date: str, new_time: str, email: str) -> str:
    """
    Reschedule an existing appointment.
    Use this when customers want to change their appointment time.

    Args:
        original_date: The original date in format YYYY-MM-DD
        original_time: The original time in format HH:MM
        new_date: The new date in format YYYY-MM-DD
        new_time: The new time in format HH:MM
        email: The customer's email address
    """
    # This is a placeholder - in a real implementation, you'd update the booking system
    return f"Appointment rescheduled from {original_date} at {original_time} to {new_date} at {new_time}. A confirmation email has been sent to {email}."

@tool
def cancel_appointment(date: str, time: str, email: str) -> str:
    """
    Cancel an existing appointment.
    Use this when customers want to cancel an appointment.
    """
    return f"Appointment cancelled for {date} at {time}. A confirmation email has been sent to {email}."

@tool
def create_quote(car_brand : str, registration_number : str, service : str) -> str:
    """
    Creates a custom quote for a service.
    Use this when customers want to get a quote for a service.
    """
    return f"Quote created for {car_brand} {registration_number} for {service}. Time to complete the service is 1 hour. Cost of the service is 10000 SEK."

tools = [get_price_and_service_list, get_general_info, check_availability, book_appointment, reschedule_appointment, cancel_appointment, create_quote]


def tool_node(state: AgentState):
    if state["messages"][-1].tool_calls:
        for tool_call in state["messages"][-1].tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_result = tools[tool_name](**tool_args)
            state["tool_calls"].append(tool_calls(name=tool_name, args=tool_args, result=tool_result))
            return {"messages": }
    return {"messages": [state["messages"][-1]]}

if __name__ == "__main__":
    print(check_availability("2025-08-10", "2025-08-21"))
