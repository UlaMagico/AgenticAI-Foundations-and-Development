# Assignment 1: Build Your First Question Answering Agent (Raw Python & Function Calling)

## Objective: 
The goal of this assignment is to understand the fundamental mechanics of LLM Agents without relying on high-level frameworks like LangChain. You will implement a "Financial Assistant" that can answer questions about exchange rates and stock prices. You must implement best coding practices, including Function Maps for routing, Environment Variables for security, and handling Parallel Tool Calls.

## Task Description: 
You need to build a Command Line Interface (CLI) chatbot in Python.

**System Setup:**
* Connect to an LLM API using a model that supports Tool Use / Function Calling. The recommended option is OpenAI gpt-4o-mini, but any OpenAI-compatible API (e.g., Gemini, Groq, Azure OpenAI, or a local LLM) is also accepted, as long as it supports tool calls via the OpenAI Python SDK interface.
* Use **python-dotenv** to manage API keys. Do not upload keys to Git/Submission.

**Mock Data Functions (Standardized):** You must implement two functions. To ensure grading consistency, **you must use the exact data below.** Do not fetch real data from the web.

* **Function 1:** get_exchange_rate(currency_pair: str)
    * Data:
        * "USD_TWD" -> "32.0"
        * "JPY_TWD" -> "0.2"
        * "EUR_USD" -> "1.2"
    * Return: A JSON string, e.g., {"currency_pair": "USD_TWD", "rate": "32.5"}.

* **Function 2:** get_stock_price(symbol: str)
    * Data:
        * "AAPL" -> "260.00"
        * "TSLA" -> "430.00"
        * "NVDA" -> "190.00"
    * Return: A JSON string, e.g., {"symbol": "AAPL", "price": "260.00"}.

* Error Handling: If a symbol or pair is not in the list, return {"error": "Data not found"}.

**Tool Schema(Structured Outputs):**
* Define the JSON schemas using the tools parameter (standard OpenAI format).
* You must enable Structured Outputs by setting "strict": true in each function definition.
* Ensure all tool parameters include "additionalProperties": false to comply with strict mode requirements.

**Robust Agent Loop:**
* Function Map: Use a Python Dictionary to dispatch tool calls (e.g., available_functions = {"get_stock_price": get_stock_price}). Do not use long if-else chains.
* Parallel Tool Calls: The loop must handle cases where the LLM calls multiple tools in one turn (e.g., "Check AAPL and TSLA"). You must execute all pending tool calls and append all results to the history before calling the LLM again.
* Context Window: The agent must remember previous turns (e.g., "What is its price?" after mentioning AAPL).

## My Review
Prompt is important, the system prompt I set in the begining is:
```
SYSTEM_PROMPT = """"
You are a "Financial Assistant" that can answer questions about exchange rates and stock prices.
Use tools when you need.
"""
```
It truns out that the program crashed and gave me the error message below:
```
groq.BadRequestError: Error code: 400 - {'error': {'message': "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '<function=get_stock_price{"symbol": "GOOG"}</function>'}}
```
then, I set another system prompt:
```
SYSTEM_PROMPT = """"
You are a "Financial Assistant" that can answer questions about exchange rates and stock prices.
Use tools to get the needed data.
If the data is not found, then tell the user the data is not found.
"""
```
It didn't crash and answered correctly. I think it's because the system prompt I set before is too ambiguous, leads to some kind of error.

## Reference
* [OpenAI Developers](https://developers.openai.com/api/docs/guides/function-calling/)
* [iThome, 透過 tool use (function calling) API 提升模型輸出穩定性](https://ithelp.ithome.com.tw/m/articles/10355329)