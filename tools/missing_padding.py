import uuid
import pandas
from langchain.tools import BaseTool


class MissingPadding(BaseTool):
    name: str = "Missing padding"
    description: str = (
        "Padding missing values"
    )

    def _run(self, file_path: str) -> str:
        # 读取文件
        try:
            data = pandas.read_excel(file_path)
        except FileNotFoundError:
            return ""
        return "data"


if __name__ == '__main__':
    dis = MissingPadding()
    data_file_path = "../data/thing.xlsx"
    # data_file_path = "../data/baby.xls"
    dis.run({
        "file_path": data_file_path,
    })
