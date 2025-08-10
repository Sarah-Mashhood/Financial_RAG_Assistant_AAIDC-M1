import sys
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from query import query_financials

test_cases = {
    "basic_revenue": "What was the company's revenue in 2024?",
    "formatted_metrics": "List key financial ratios like ROE, ROA, and profit margin.",
    "unavailable_info": "What is the CEO's birthday?",
    "multiple_metrics": "Compare revenue and net profit year-over-year.",
    "efficiency_ratio": "What was the efficiency ratio in the last quarter?",
    "improper_question": "How does the company's logo look?",
    "ambiguous_question": "Tell me about the company.",
    "empty_input": "",
    "non_financial_query": "What is the weather today?",
    "large_number_format": "Report the total assets if available."
}

def run_tests():
    all_passed = True
    for test_name, query in test_cases.items():
        print(f"\n=== Running Test: {test_name} ===")
        result = query_financials(query)

        print("Response Preview:\n", result[:300], "..." if len(result) > 300 else "")

        # Automated assertions per test case:
        try:
            if test_name == "unavailable_info":
                assert "Information not available" in result, "Expected 'Information not available.'"
            elif test_name == "basic_revenue":
                assert "PKR" in result and any(char.isdigit() for char in result), "Expected numeric revenue with currency."
            elif test_name == "formatted_metrics":
                for metric in ["ROE", "ROA", "profit margin"]:
                    assert metric in result or "not available" in result.lower(), f"Expected mention of {metric} or not available"
            elif test_name == "multiple_metrics":
                assert "revenue" in result.lower() and "net profit" in result.lower(), "Expected comparison of revenue and net profit"
            elif test_name == "efficiency_ratio":
                assert "efficiency ratio" in result.lower(), "Expected efficiency ratio info"
            elif test_name == "improper_question":
                assert "Information not available" in result or len(result.strip()) > 0, "Expected polite fallback or response"
            elif test_name == "ambiguous_question":
                assert len(result.strip()) > 0, "Expected some descriptive answer"
            elif test_name == "empty_input":
                assert len(result.strip()) > 0, "Expected response to empty input"
            elif test_name == "non_financial_query":
                assert "Information not available" in result or "cannot provide" in result.lower(), "Expected fallback for non-financial query"
            elif test_name == "large_number_format":
                assert "PKR" in result and any(char.isdigit() for char in result), "Expected total assets with currency and numbers"
            print(f"Test '{test_name}' PASSED.")
        except AssertionError as e:
            print(f"Test '{test_name}' FAILED: {e}")
            all_passed = False

    if all_passed:
        print("\nAll tests PASSED.")
    else:
        print("\nSome tests FAILED. Please review the outputs.")

if __name__ == "__main__":
    run_tests()
