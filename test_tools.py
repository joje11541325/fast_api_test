#!/usr/bin/env python3
"""
Test script to demonstrate tool usage in the classification agent
"""

from email_agent import graph
from classes import Email


def test_price_inquiry():
    """Test the agent with a price inquiry that should trigger the price list tool"""
    print("=== Testing Price Inquiry ===")
    email = Email(
        subject="Fråga om pris",
        body="Hej, jag undrar vad det skulle kosta med ett nytt set med lösnaglar",
        email="test@example.com"
    )

    result = graph.invoke({"email": email})
    print(f"Tool results: {result.get('tool_results', [])}")
    print(f"Response subject: {result['email'].subject}")
    print(f"Response body: {result['email'].body}")
    print()


def test_booking_inquiry():
    """Test the agent with a booking inquiry that should trigger booking tools"""
    print("=== Testing Booking Inquiry ===")
    email = Email(
        subject="Boka tid",
        body="Hej, jag vill boka en tid för nagelförlängning nästa vecka",
        email="booking@example.com"
    )

    result = graph.invoke({"email": email})
    print(f"Tool results: {result.get('tool_results', [])}")
    print(f"Response subject: {result['email'].subject}")
    print(f"Response body: {result['email'].body}")
    print()


def test_opening_hours_inquiry():
    """Test the agent with an opening hours inquiry"""
    print("=== Testing Opening Hours Inquiry ===")
    email = Email(
        subject="Öppettider",
        body="Hej, när är ni öppna?",
        email="hours@example.com"
    )

    result = graph.invoke({"email": email})
    print(f"Tool results: {result.get('tool_results', [])}")
    print(f"Response subject: {result['email'].subject}")
    print(f"Response body: {result['email'].body}")
    print()


def test_general_inquiry():
    """Test the agent with a general inquiry that might not need tools"""
    print("=== Testing General Inquiry ===")
    email = Email(
        subject="Allmän fråga",
        body="Hej, hur mår ni?",
        email="general@example.com"
    )

    result = graph.invoke({"email": email})
    print(f"Tool results: {result.get('tool_results', [])}")
    print(f"Response subject: {result['email'].subject}")
    print(f"Response body: {result['email'].body}")
    print()


if __name__ == "__main__":
    print("Testing Classification Agent with Tools\n")

    test_price_inquiry()
    test_booking_inquiry()
    test_opening_hours_inquiry()
    test_general_inquiry()

    print("All tests completed!")
