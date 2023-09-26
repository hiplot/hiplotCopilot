# 加载.env中的变量 包含OPENAI_API_KEY和OPENAI_API_BASE
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())