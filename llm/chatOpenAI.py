from langchain.chat_models import ChatOpenAI


def chat_openai(temperature=0):
    return ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo-0613")