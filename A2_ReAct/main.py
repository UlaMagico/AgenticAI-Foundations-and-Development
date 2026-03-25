from agent import Agent

if __name__ == '__main__':
    agent = Agent()
    '''
    query_list = [
        #"What fraction of Japan's population is Taiwan's population as of 2025?",
        "Compare the main display specs of iPhone 15 and Samsung S24.",
        #"Who is the CEO of the startup 'Morphic' AI search?"
    ]

    for query in query_list:
        print('='*10 + f' {query} ' + '='*10)
        agent.execute(query)
        agent.clear_memory()
    '''

    print("Type 'QUIT' to quit the program.")
    while True:
        query = input('User: ')
        if query.lower() == 'quit':
            break
        agent.execute(query)
