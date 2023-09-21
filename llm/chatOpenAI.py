from langchain.chat_models import ChatOpenAI


def chat_openai():
    return ChatOpenAI(temperature=0)