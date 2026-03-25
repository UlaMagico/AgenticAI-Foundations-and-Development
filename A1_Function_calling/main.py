'''
"Financial Assistant" that can answer questions about exchange rates and stock prices.
You must implement best coding practices, including:
Function Maps for routing
Environment Variables for security
Parallel Tool Calls

references:
OpenAI Developers: https://developers.openai.com/api/docs/guides/function-calling/
groq supported models: https://console.groq.com/docs/models
iThome, 透過 tool use (function calling) API 提升模型輸出穩定性: https://ithelp.ithome.com.tw/m/articles/10355329
'''

import os
import json
from groq import Groq
from AvailableFunction import get_exchange_rate, get_stock_price
from dotenv import load_dotenv

# Environment Variables for security
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """"
You are a "Financial Assistant" that can answer questions about exchange rates and stock prices.
Use tools when you need.
"""
MODEL_NAME = 'llama-3.1-8b-instant'

# Function Maps for routing (tools definition)
function_map: dict[str, callable] = {
    "get_exchange_rate": get_exchange_rate,
    "get_stock_price": get_stock_price
}
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "strict": True,
            "description": "Get current exchange rate from USD to a target currency (e.g., 'USD to TWD').",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_pair": {
                        "type": "string",
                        "description": "Target currency code, e.g., 'USD_TWD'."
                    }
                },
                "required": ["currency_pair"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "strict": True,
            "description": "Get current stock price for a symbol (e.g., 'AAPL').",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., 'AAPL')."
                    }
                },
                "required": ["symbol"],
                "additionalProperties": False
            }
        }
    }
]

def run_agent():
    messages = [{'role':"system", 'content': SYSTEM_PROMPT}]
    print("Agent Started. Type 'QUIT' to quit.")
    while True:
        user_input = input("User: ")
        if user_input.upper()=="QUIT": break

        messages.append({
            "role": 'user',
            "content": user_input
        })

        # First API Call
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls
        
        if tool_calls:
            # IMPORTANT: Add the assistant's "thought" (tool call request) to history
            thoughts = [response_msg]

            # Handle Parallel Tool Calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Dynamic Dispatch using Function Map
                function_to_call = function_map.get(function_name)
                
                # ps: tool_result must be a string
                if function_to_call:
                    try:
                        tool_result = json.dumps(function_to_call(**function_args))
                    except Exception as e:
                        tool_result = json.dumps({"error": str(e)})
                else:
                    tool_result = json.dumps({"error": "Function not found"})

                # Append RESULT to history
                thoughts.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result,
                })
                
            print('-'*5+' Log '+'-'*5)
            print("Thinking:")
            print(thoughts)
            print('-'*10)

            messages += thoughts

            # Final answer
            final_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
            )
            final_content = final_response.choices[0].message.content
            print(f'Agent: {final_content}')
            messages.append({"role": "assistant", "content": final_content})
        else:
            # No tool needed
            print(f"Agent: {response_msg.content}")
            messages.append({"role": "assistant", "content": response_msg.content})

if __name__ == '__main__':
    run_agent()