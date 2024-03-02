from bq_agent.agent import agent_executor

if __name__ == "__main__":
    question = "how many unique users are there?"
    print(agent_executor.invoke({"input": question}))
