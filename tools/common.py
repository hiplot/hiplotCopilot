from langchain.prompts import PromptTemplate
from langchain.agents import Tool
from langchain.chains import LLMChain
from llm.chatOpenAI import chat_openai


def common():
    prompt = PromptTemplate(
        input_variables=["query"],
        template="{query}"
    )

    llm_chain = LLMChain(llm=chat_openai(), prompt=prompt)

    # initialize the LLM tool
    llm_tool = Tool(
        name='Common Tool',
        func=llm_chain.run,
        description='use this tool for general purpose queries and logic'
    )

    return llm_tool
