from langchain_core.tools import tool
from typing import Optional
import datetime
import requests


@tool
def get_price_list() -> str:
    """
    Returns a very detailed price list for the company's services.
    Use this when customers ask about prices, costs, or pricing information.
    """
    try:
        with open("company_info/prislista.txt", "r", encoding="utf-8") as file:
            price_list = file.read()
        return f"Here is our current price list:\n\n{price_list}"
    except FileNotFoundError:
        return "Price list not available at the moment. Please contact us directly for pricing information."


@tool
def get_services_list() -> str:
    """
    Returns a detailed list of services offered by the company.
    Use this when customers ask about available services or what you offer.
    """
    try:
        with open("company_info/prislista.txt", "r", encoding="utf-8") as file:
            services = file.read()
        return f"Here are our available services:\n\n{services}"
    except FileNotFoundError:
        return "Services list not available at the moment. Please contact us directly for information about our services."


@tool
def get_opening_hours() -> str:
    """
    Returns the opening hours for the nail salon.
    Use this when customers ask about when you're open or available hours.
    """
    # You can either read from a file or hardcode this information
    opening_hours = """
    Our opening hours:
    Monday - Friday: 9:00 AM - 7:00 PM
    Saturday: 9:00 AM - 5:00 PM
    Sunday: Closed
    
    We recommend booking appointments in advance to ensure availability.
    """
    return opening_hours


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
    return f"Appointment booked for {customer_name} on {date} at {time} for {service}. A confirmation email has been sent to {email}. Please arrive 10 minutes before your appointment time."


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


if __name__ == "__main__":
    print(check_availability("2025-08-10", "2025-08-21"))
