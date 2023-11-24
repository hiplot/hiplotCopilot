class TableArg:
    en_description: str = "This field represents {} and requires selecting the appropriate field from the data table as its value"
    zh_description: str = "这个字段表示{}，需要从数据表中选择合适的字段作为其值"

    def __init__(self, arg: dict):
        self.arg = arg

    def get_prompt(self) -> str:
        label = self.arg["label"]
        if "en" in label:
            return self.en_description.format(label["en"])
        elif "zh_cn" in label:
            return self.zh_description.format(label["zh_cn"])
        return "language type not found"

    def is_required(self) -> bool:
        return "required" in self.arg and self.arg["required"]


class ExtraArg:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data

    def get_prompt(self) -> str:
        return self.name

    def is_required(self) -> bool:
        # return "required" in self.data and self.data["required"]
        # TODO 尚未完善相关内容
        return False


def get_table_required(ui_json) -> dict:
    data_arg = ui_json["dataArg"]
    cur_table = 0
    table_required = {}
    while True:
        cur_table += 1
        table_name = f"{cur_table}-data"
        if table_name not in data_arg:
            break

        arg_num = 0
        for arg in data_arg[table_name]:
            arg_num += 1

            table_arg = TableArg(arg)
            if not table_arg.is_required():
                continue
            key = f"{cur_table}-{arg_num}"
            table_required[key] = table_arg.get_prompt()
    return table_required


def get_extra_required(ui_json) -> dict:
    extra = ui_json["extra"]
    extra_required = {}
    for k, v in extra.items():
        extra_arg = ExtraArg(k, v)
        if not extra_arg.is_required():
            continue
        if "required" not in v or not v["required"]:
            continue
        extra_required[k] = extra_arg.get_prompt()
    return extra_required
