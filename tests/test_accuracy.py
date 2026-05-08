import pytest
import json
from src.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def load_golden_set():
    with open("tests/goldenset.json", "r") as f:
        return json.load(f)

@pytest.mark.parametrize("test_case", load_golden_set())
def test_ai_accuracy(test_case):
    """Verify AI finds correct IDs and math totals."""
    response = client.post("/ask", json={"query": test_case["query"]})
    analysis = response.json()["analysis"]
    
    # 1. Verification: Groundedness
    # Does the AI mention the specific Transaction IDs required?
    for tid in test_case["expected_ids"]:
        assert tid in analysis, f"AI missed transaction {tid} for query '{test_case['query']}'"
    
    # 2. Verification: Math
    # Check if the total dollar amount is present in the text
    total_str = f"{test_case['expected_total']:,}" # Format with commas if needed
    assert str(test_case['expected_total']) in analysis.replace(",", ""), \
        f"AI math incorrect. Expected {test_case['expected_total']} in output."