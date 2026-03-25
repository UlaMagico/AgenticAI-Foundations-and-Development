import os
import re
from dotenv import load_dotenv
load_dotenv()

from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
def search_web(query):
    response = tavily_client.search(query, max_results=3)
    results = response['results']
    parts = []
    for result in results:
        parts.append(
            f"title: {result['title']}\n"
            f"url: {result['url']}\n"
            f"content: {result['content']}"
        )
    return '\n\n'.join(parts) if parts else "No results were found."

def calculate(expression: str) -> str:
    try:
        allowed = re.compile(r'^[\d\s\+\-\*\/\.\(\)\%\*\*]+$')
        if not allowed.match(expression):
            return {"error": "Invalid expression"}
        result = eval(expression, {"__builtins__": {}})   # noqa: S307
        return f"{expression} = {result}"
    except Exception as e:
        return {"error": e}
'''
def crawl_web(url, instructions):
    response = tavily_client.crawl(url, instructions=instructions)
    return response

def research_web(query):
    response = tavily_client.research(query)
    return response
'''

TOOLS: dict[str, callable] = {
    'search_web':   lambda inp: search_web(inp['query']),
    'calculate':    lambda inp: calculate(inp['expression']),
    #'crawl_web':    lambda inp: crawl_web(inp['url'], inp['query']),
    #'research_web': lambda inp: research_web(inp['query']),
}

if __name__ == '__main__':
    import json
    from contextlib import redirect_stdout
    def json_format(text):
        return json.dumps(text, indent=4, ensure_ascii=False)
    
    with open('.log', 'w', encoding='utf-8') as f:
        with redirect_stdout(f):
            # just some simple test
            print('='*10+'Search Web'+'='*10)
            print(TOOLS['search_web']({"query":"How to make cake?"}))
            #print(json_format(search_web("How to make cake?")))

            '''
            print('='*10+'Crawl Web'+'='*10)
            print(json_format(crawl_web("https://docs.tavily.com", instructions="Find all pages on the Python SDK")))

            print('='*10+'Reearch Web'+'='*10)
            print(json_format(research_web('What are the latest developments in AI?')))
            '''
