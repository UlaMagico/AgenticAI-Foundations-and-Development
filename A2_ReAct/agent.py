'''
Thought -> Action -> Observation loop.
'''
import os
import re
import json
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from tools import TOOLS

MODEL_NAME = 'llama-3.1-8b-instant'
#MODEL_NAME = "openai/gpt-oss-20b"
MAX_STEPS = 6
MAX_TOKENS = 1024

SYSTEM_PROMPT = '''
You are a helpful assistant who can do reasoning and acting to give the user a reasonable answer.
You are allowed to use the tools to help you get the sufficient information to answer the query.
You must give your thought and action following the format below and only one thought and action per every step, the user will help you count the step:
user: [step n]
Thought: <Breaking the query and thinking of what to do and how to do.>
Action: [{"name": "tool_name", "args": {"arg1":"arg1", "arg2": "arg2", ...}},...] (The tool you want to use, json format. Can use multiple tools if you need.)>

Then you will get the informations:
Observation: <the information> (Don't generate observations yourself!)
If you get enough informations, then generate the answer to the query:
Thought: I've gotten enough information to answer.
Action: [{"name": "answer", "args": {"answer":"final answer"}}]

For example:
user query: "How to make cake?"
user: [step 1]
Thought: I need to search "How to make cake?" on the web to answer the query.
Action: [{"name": "search_web", "args": {"query": "How to make cake?"}}]
Observation:
search_web "How to make cake?"
How to make cake? First, You need to prepare...

user: [step 2]
Thought: I've gotten enough information to answer.
Action: [{"name": "answer", "args": {"answer":"To make cake, you need to prepare..."}}]
________________________________
The tools you can use, the tool name and the arg name must be same as the description:
1. answer: stop ReAct and answer the query
    args: {"answer": "the final answer"}

2. search_web: Gives the query that you want to search on the web. Return json list of the search results.
    args: {"query": "The query that you want to search on the web"}

3. calculate: Do math calculation
    args: {"expression": "math expression, e.g.: (3 + 5) * 2"}
________________________________
Don't respond without enough information.
Don't use the tool that isn't on the tool list.
'''

class Agent:
    def __init__(self, system_prompt=SYSTEM_PROMPT, error_allowed=True):
        self.system = system_prompt
        self.messages = [{'role':"system", 'content': system_prompt}]
        self.error_allowed = error_allowed

        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.MODEL_NAME = MODEL_NAME

    def _call_llm(self):
        response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=self.messages,
            max_tokens=MAX_TOKENS,
            stop=["Observation:"],   # prevent llm generate observation by itself
            tool_choice = "none"
        )
        return response.choices[0].message.content
    
    def _log_error(self, error_msg):
        error_msg = f"ERROR: {error_msg}"
        print(error_msg)
        self.messages.append({"role": "user", "content": error_msg})
        self.error_flag = True

    def _parse_llm_output(self, text: str) -> dict:
        """
        parse ReAct format output
        return:
        (
            "thought": "llm thougt"
            "actions": [
                {
                    "name": "tool_1",
                    "args": {
                        "arg1": "arg1",
                        "arg2": "arg2",
                        ...
                    }
                },
                ...
            ]
        )
        or 
        {"error": "error msg"}
        """
        thought_match = re.search(r"Thought:\s*(.+?)(?=Action:|$)", text, re.DOTALL)
        actions_match  = re.search(r"Action:\s*(.+)", text, re.DOTALL)

        error = None
        if actions_match and thought_match:
            thought = thought_match.group(1).strip()
            try:
                actions = json.loads(actions_match.group(1).strip().split("\n")[0])
            except json.JSONDecodeError:
                # try to fix the json format
                fixed = actions_match.group(1).replace("'", '"')
                try:
                    actions = json.loads(fixed.strip().split("\n")[0])
                except Exception:
                    error = {"error": f"Invalid action format: {actions_match.group(1)}"}
        else:
            error = {"error":f"Invalid llm output format: {text}"}

        if error:
            return error

        return {
            "thought": thought,
            "actions": actions
        }

    def execute(self, query):
        # The ReAct Loop
        iteration = 0
        self.error_flag = False
        self.messages.append({"role": "user", "content": query}) # save
        while iteration < MAX_STEPS:
            print("\n" + "="*10 + f" Step {iteration+1} " + "="*10)
            self.messages.append({"role": "user", "content": f"[step {iteration+1}]"}) # help llm count steps
            # Call LLM -----------------
            try:
                llm_response = self._call_llm()
            except Exception as e:
                error_msg = f"Fail to call llm:\n{e}"
                print(f"ERROR: {error_msg}")
                return
            print(llm_response)
            self.messages.append({"role": "assistant", "content": llm_response}) # save
            
            # Parse Action -----------------
            parsed = self._parse_llm_output(llm_response)
            if "error" in parsed:
                error_msg = parsed['error']
                self._log_error(error_msg)
            else:
                if(parsed['actions'][0]['name']=='answer'):
                    print("Answer:")
                    print(parsed['actions'][0]['args']['answer'])
                    break

                # Call Tool -----------------
                observation_parts = ["Observation:"]
                for action in parsed['actions']:
                    tool_name = action['name']
                    args = action["args"]
                    if tool_name not in TOOLS:
                        error_msg = f"Tool '{tool_name}' not found."
                        self._log_error(error_msg)
                        break
                    tool_result = TOOLS[tool_name](args)
                    if 'error' in tool_result:
                        error_msg = f"Fail to call tool: {action}\n{tool_result['error']}"
                        self._log_error(error_msg)
                        break
                    try:
                        observation_parts.append(f"{tool_name}({','.join([str(v) for v in args.values()])})")
                        observation_parts.append(str(tool_result))
                    except Exception as e:
                        error_msg = f"Fail to call tool: {action}\n{e}"
                        self._log_error(error_msg)
                        break
                observation_text = '\n'.join(observation_parts)
                print('-'*20)
                print(observation_text)
                print('-'*20)

            if self.error_flag:
                if not self.error_allowed:
                    # stop execute when error occurred
                    print("Error occurred! Stop executing agent.")
                    return
                else: 
                    iteration += 1
                    continue
            else:
                self.messages.append({"role": "assistant", "content": observation_text}) # feed back the observation text
                iteration += 1
        if iteration >= MAX_STEPS:
            print(f"Exceed max step {MAX_STEPS}, stop execute agent.")
            print("Answer:")
            print("Failed to get answer within step limit.")
                
    def clear_memory(self):
        self.messages = [{'role':"system", 'content': self.system}]
        print("="*10 + ' Clear Memory ' + "="*10)

    def demo(self):
        query_list = [
            #"What fraction of Japan's population is Taiwan's population as of 2025?",
            "Compare the main display specs of iPhone 15 and Samsung S24.",
            #"Who is the CEO of the startup 'Morphic' AI search?"
        ]
        for i,query in enumerate(query_list):
            print('='*10 + f" Query {i+1}: {query} " + '='*10)
            self.execute(query)
            self.clear_memory()

if __name__ == '__main__':
    agent = Agent(error_allowed=True)
    agent.demo()

    '''
    from datetime import datetime
    from contextlib import redirect_stdout

    log_dir = './A2_ReAct/log'
    
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
    log_path = os.path.join(log_dir, filename)
    with open(f"{log_path}", 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            agent.demo()
    '''