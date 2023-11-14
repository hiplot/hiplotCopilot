from towhee import pipe

from llm.chatOpenAI import chat_openai
from langchain.agents import initialize_agent, agent_types
from tookits import data_processing

llm = chat_openai()
toolkit = data_processing.DataProcessingToolKit()
agentType = agent_types.AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION

agent = initialize_agent(
    llm=llm,
    agent=agentType,
    tools=toolkit.get_tools(),
    verbose=False  # output logs
)

hiplot_preprocess_pipeline = (
    pipe.input("query")
    .map("query", "result", lambda query: agent.run(query))
    .output("result")
)

if __name__ == "__main__":
    print(hiplot_preprocess_pipeline("Hello world!").get()[0])
