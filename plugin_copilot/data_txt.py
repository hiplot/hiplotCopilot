import json


class InputData:
    def __init__(self, title: list, data: list):
        self.title = title
        self.data = data

    def json_format(self) -> str:
        return json.dumps(self.__dict__)


def get_data_top(path: str, line_num: int = 6):
    with open(path, "r") as file:
        input_data = InputData([], [])
        for i in range(line_num):
            line = file.readline().split()
            if i == 0:
                input_data.title = line
                continue
            input_data.data.append(line)
    return input_data.json_format()
