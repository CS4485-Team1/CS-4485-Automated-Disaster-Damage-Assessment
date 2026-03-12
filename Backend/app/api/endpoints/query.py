from fastapi import APIRouter
from app.data.data import retrieve_test_queries
from app.services.query_parser import QueryParser
from colorama import Fore, Style, init
from pydantic import BaseModel
import time
import json

router = APIRouter()

@router.post("/parseQuery/")
async def parseQuery(req : str):
    print(f"Req: {req}")
    qp = QueryParser()
    return qp.parse(req)

def evaluate_parser(parser):
    TEST_CASES = retrieve_test_queries()
    total = len(TEST_CASES)
    correct_intent = 0
    correct_params = 0

    results = []
    start_time = time.time()

    for i, case in enumerate(TEST_CASES):

        result = parser.parse(case["query"])

        intent = result.get("intent")
        params = {k: v for k, v in result.items() if k != "intent"}

        expected_intent = case["expected_intent"]
        expected_fields = case["expected_fields"]

        intent_match = intent == expected_intent

        # checking only expected fields
        param_match = True
        for key, expected_value in expected_fields.items():
            predicted_value = params.get(key)

            if predicted_value != expected_value:
                param_match = False
                break

        case_result = {
            "test_case": i + 1,
            "query": case["query"],
            "expected_intent": expected_intent,
            "predicted_intent": intent,
            "expected_parameters": expected_fields,
            "predicted_parameters": params,
            "intent_correct": intent_match,
            "parameters_correct": param_match
        }

        results.append(case_result)

        print(Fore.YELLOW + f"Test Case {i + 1}")
        print(Fore.CYAN + f"Query: {case['query']}")

        print(Fore.GREEN + f"Expected Intent: {expected_intent}")
        print(Fore.GREEN + f"Predicted Intent: {intent}")

        print(Fore.GREEN + f"Expected Fields: {expected_fields}")
        print(Fore.GREEN + f"Predicted Fields: {params}")

        print(
            Fore.GREEN + "Intent Correct: Yes"
            if intent_match else Fore.RED + "Intent Correct: No"
        )

        print(
            Fore.GREEN + "Parameters Correct: Yes"
            if param_match else Fore.RED + "Parameters Correct: No"
        )

        print(Fore.WHITE + "-" * 50)

        if intent_match:
            correct_intent += 1

        if param_match:
            correct_params += 1

    end_time = time.time()

    intent_accuracy = correct_intent / total
    param_accuracy = correct_params / total
    duration = end_time - start_time

    print(Fore.YELLOW + "\n=========================")
    print(Fore.GREEN + f"Intent Accuracy: {correct_intent}/{total} = {intent_accuracy:.2%}")
    print(Fore.GREEN + f"Parameter Accuracy: {correct_params}/{total} = {param_accuracy:.2%}")
    print(Fore.YELLOW + "=========================")

    return {
        "intent_accuracy": f"{correct_intent}/{total} = {intent_accuracy:.2%}",
        "parameter_accuracy": f"{correct_params}/{total} = {param_accuracy:.2%}",
        "total_time_taken": f"{duration:.4f} seconds",
        "results": results
    }
    
# route to trigger the tests
@router.get("/run-tests/")
def run_tests():
    parser = QueryParser()
    test_results = evaluate_parser(parser)
    return test_results

class TestResultResponse(BaseModel):
    test_results: list
    summary: dict

@router.get("/test-results/", response_model=TestResultResponse)
def get_test_results():
    parser = QueryParser()
    test_results = evaluate_parser(parser)
    return test_results

@router.get("/showTest")
def showTest():
    return retrieve_test_queries()