from langchain.tools import PythonAstREPLTool
from tools.common import common
from tools.discrete_mapping import DiscreteMapping


def get_all_tools():
    return [
        PythonAstREPLTool(),
        DiscreteMapping(),
        # common(), # 通用工具
    ]
