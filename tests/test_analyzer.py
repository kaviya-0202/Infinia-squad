import pytest
from analyzer import analyze_ticket

# Test 1: High urgency ticket returns correct signals
def test_high_urgency_ticket():
    ticket = "I have been waiting 3 days and no one responded. Cancelling my subscription today."
    result = analyze_ticket(ticket)
    assert "Negative" in result
    assert "High" in result

# Test 2: Positive ticket returns positive sentiment
def test_positive_ticket():
    ticket = "Love the product! Everything is working perfectly. Thank you!"
    result = analyze_ticket(ticket)
    assert "Positive" in result

# Test 3: Output always contains required fields
def test_output_format():
    ticket = "My payment failed but I was still charged."
    result = analyze_ticket(ticket)
    assert "Sentiment:" in result
    assert "Urgency:" in result
    assert "Churn Risk:" in result

# Test 4: Empty ticket input is handled
def test_empty_ticket():
    ticket = ""
    result = analyze_ticket(ticket)
    assert result is not None  # Should return something, not crash

# Test 5: Low urgency ticket
def test_low_urgency_ticket():
    ticket = "Just checking if there are any new features coming. Love the service!"
    result = analyze_ticket(ticket)
    assert "Low" in result or "Positive" in result