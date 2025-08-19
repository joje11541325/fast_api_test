#!/usr/bin/env python3
"""
Test script for email sending functionality
"""

import os
from dotenv import load_dotenv
from email_agent import send_email_generic, Email, AgentState

load_dotenv()


def test_email_sending():
    """Test the email sending functionality"""

    # Create a test email
    test_email = Email(
        subject="Test Email from FastAPI",
        body="This is a test email sent via HTTP POST request.",
        email="recipient@example.com"
    )

    # Create agent state
    state = AgentState(email=test_email)

    print("Testing email sending functionality...")
    print(f"To: {test_email.email}")
    print(f"Subject: {test_email.subject}")
    print(f"Body: {test_email.body}")
    print("-" * 50)

    # Test with different email services
    services = ["sendgrid", "mailgun", "custom"]

    for service in services:
        print(f"\nTesting {service.upper()} service:")
        try:
            result = send_email_generic(state, service_type=service)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error testing {service}: {e}")

    print("\n" + "=" * 50)
    print("Note: Make sure to set up your environment variables in .env file")
    print("See email_config_example.txt for configuration details")


if __name__ == "__main__":
    test_email_sending()
