from agent_service.app import run_agent

# Local testing script for validating agent behavior in isolation.
if __name__ == "__main__":
    task = {"input": "Explain what Kafka is in 2 sentences."}
    output = run_agent(task)
    print("Agent response:", output)
