# Development work flow

## 1. Model Selection (Ollama)

For a 12GB VRAM setup, you want models that balance reasoning depth with memory efficiency.
    - The Planner (Thinking LLM): DeepSeek-R1 (Distilled Llama-70B or Qwen-32B).
        Why: DeepSeek-R1 is the gold standard for open-source reasoning. It uses a "Chain of Thought" (CoT) process to break down complex tasks into manageable steps before writing a single line of code.
        - ollama run deepseek-r1:32b (search for a cloud option if results are not good)
    - The Executor (Coding LLM): Qwen3-Coder (14B or 32B).
        Why: Qwen3-Coder models are currently outperforming almost everything in the open-weight space for pure syntax accuracy and repository-level understanding.
        - ollama run qwen3-coder:30b
        - ollama run qwen3-coder:480b-cloud
    - The Tester (Utility LLM): Llama-3.3-8B.
        Why: You need a fast, lightweight model to generate the random test data and the unit test templates. Using a massive model here is overkill and slows down the loop.
        - ollama run phi4-mini (precision)
        - ollama run gemma3:4b (speed)
        - ollama run gemma3:27b-cloud

## 2. Recommended Frameworks

While you've used CrewAI, for this specific "Loop" logic, a state-machine approach is often more reliable:
    LangGraph (Local): Better than standard CrewAI for "retry loops" because it allows you to define explicit nodes and edges with cycles (loops).
    PydanticAI: Excellent if you want strict "Structured Outputs" (ensuring the LLM always returns valid JSON or specific code blocks).
    Pytest + Hypothesis: For the testing phase. Hypothesis is a Python library specifically designed for "Property-Based Testing" (generating random data to find edge cases).

## 3. Designing the Development Flow

The Logic Steps:
    1. Planning Phase: DeepSeek-R1 receives the prompt. It outputs a PLAN.md detailing the logic, edge cases, and required functions.
    2. Implementation Phase: Qwen3-Coder reads the PLAN.md and the original prompt. It outputs the source code.
    3. Test Generation: Llama-8B generates a test suite. It analyzes the code to identify input types (e.g., "this function takes an integer between 1 and 100").
    4. Verification (The Loop): The code is run against the tests.
        - Success: Implementation accepted.
        - Failure: The error logs are sent back to the Executor (not the Planner) to fix the code.

## 4. How many test runs are enough?

To be confident without wasting local compute time, we look at the Law of Diminishing Returns in software testing.
    Runs,Confidence Level,Goal
    5–10,Low,"Catching basic syntax and ""happy path"" errors."
    30–50,High (Recommended),"This is the ""sweet spot."" It usually catches most boundary conditions and edge cases with random data."
    100+,Very High,Necessary only for critical financial or security logic.

Recommendation: Set your flow to 40 runs with random data. If it passes 40 different random inputs, your confidence that the logic is sound is statistically very high (>95%).

## 5. Implementing the Retry Limit

To prevent an infinite loop (and your GPU melting), implement a "Max Retries" counter.
    - Max Retries: 3 to 5.
    - The Escalation Rule: If the Executor fails twice at the same fix, the flow should go back one step further to the Planner to see if the original plan was flawed.

Code:

max_retries = 3
current_retry = 0

while current_retry < max_retries:
    result = run_tests(code, test_data)
    if result.passed:
        save_code(code)
        break
    else:
        current_retry += 1
        # Pass the error logs back to the LLM
        code = executor_agent.fix_code(code, result.logs)

### One final tip for your RTX 4070 Super

Since you only have 12GB of VRAM, use Ollama's model concurrency. You don't need all three models in memory at once. Ollama will swap them out automatically, but to speed this up, ensure you aren't using the maximum context window (32k) for the simple Tester model, which saves VRAM for the Planner.
