import string
import nanoid
import os
import json
import shutil
from common.hiTowhee import embedding_pipeline
from common.print_color import print_blue
from common.hiMilvus import hiplot_plugins_collection
from langchain import LLMChain
from llm.chatOpenAI import chat_openai
from plugin_copilot.rabbitmq import send_task


class Task:
    project_path = "//wsl.localhost/Ubuntu/home/lxs/code/ospp/plugins-open"
    destination_path = "//wsl.localhost/Ubuntu/home/lxs/code/ospp/user/input"

    def __init__(self, query: str):
        self.query = query
        self.tid = nanoid.generate(alphabet=string.digits + string.ascii_letters, size=10)
        self.image_description = ""
        self.data_filepath = ""
        self.title_description = ""
        self.module_name = ""
        self.plugin_name = ""
        self.plugin_path = ""
        self.hit_params_dict = {}
        self.input_json_required = ""

    def run(self):
        print_blue(f"用户输入:{self.query}")

        # 1. 提取出需要绘制的图像和参数路径
        self.extract_params_from_query()

        # 2.确定所属模块和插件名
        self.get_module_and_plugin_name()

        # 3.解析data.txt文件
        # 3.1读取并解释标题信息
        self.get_title_description()
        # 3.2解析得到必填参数项
        self.get_input_json_required()
        # 3.3选择合适的参数填充
        self.get_hit_params()

        # 4.构造新的data.json
        self.build_new_json()

        # 5.将文件迁移到指定位置
        self.move_file()

        # 6.将构造好的所有内容提交至rscheduler运行
        self.send()

    def send(self):
        send_task(task_id=self.tid, module_name=self.module_name, plugin_name=self.plugin_name)

    def get_module_and_plugin_name(self):
        # 2.根据图像描述确定插件名，并获取到模块名
        # 2.1 获取插件名
        from plugin_copilot.prompt import get_plugin_name
        embeddings = embedding_description(self.image_description)
        documents = get_description(embeddings)
        c = LLMChain(llm=chat_openai(), prompt=get_plugin_name)
        resp = c.run(image_description=self.image_description, documents=documents)
        hit_description = json.loads(resp)
        # 2.2 获取插件所属模块
        for name, _ in hit_description.items():
            self.plugin_name = name
            resp = hiplot_plugins_collection.query(f"name==\"{name}\"", ["module"])
            if len(resp) == 0:
                print("Record not found")
            self.module_name = resp[0]["module"]
            break
        print_blue(f"所属模块:{self.module_name}")
        print_blue(f"插件名:{self.plugin_name}")
        self.get_plugin_path()

    def extract_params_from_query(self):
        from plugin_copilot.prompt import extract_params
        c = LLMChain(llm=chat_openai(), prompt=extract_params)
        resp = c.run(self.query)
        params = json.loads(resp)
        i_description = params["image_description"]
        d_filepath = os.path.abspath(params["filepath"])
        print_blue(f"图像描述信息:{i_description}")
        print_blue(f"数据文件路径:{d_filepath}")
        self.image_description = i_description
        self.data_filepath = d_filepath

    def get_title_description(self):
        from plugin_copilot.prompt import explain_title
        from plugin_copilot.data_txt import get_data_top
        c = LLMChain(llm=chat_openai(), prompt=explain_title)
        resp = c({"json_data": get_data_top(self.data_filepath)})
        t_description = resp["text"]
        print_blue(f"标题解释:{t_description}")
        self.title_description = t_description

    def get_input_json_required(self):
        ui_json_file_path = os.path.join(self.plugin_path, "ui.json")
        with open(ui_json_file_path, "r", encoding="utf-8") as f:
            ui = json.load(f)
        from plugin_copilot.ui_json import get_table_required
        table_required = get_table_required(ui)
        self.input_json_required = json.dumps(table_required)
        print_blue(f"必填参数解析结果:{self.input_json_required}")

    def move_file(self):
        input_path = os.path.join(self.destination_path, self.tid)
        os.makedirs(input_path, exist_ok=True)
        new_data_path = shutil.copy("../data.txt", os.path.join(input_path, "data.txt"))
        new_config_path = shutil.copy("../data.json", os.path.join(input_path, "data.json"))
        # os.remove("../data.txt")
        # os.remove("../data.json")
        print_blue(f"用户提交的data.txt已迁移至{new_data_path}")
        print_blue(f"新构造的data.json已移动至{new_config_path}")

    def get_hit_params(self):
        from plugin_copilot.prompt import select_params
        llm_chain = LLMChain(llm=chat_openai(), prompt=select_params)
        select_params_res = llm_chain(
            {"description_json": self.title_description, "input_json": self.input_json_required})
        h_params = select_params_res["text"]
        self.hit_params_dict = json.loads(h_params)

    def build_new_json(self):
        with open(os.path.join(self.plugin_path, "data.json"), "r", encoding="utf-8") as f:
            data_json = json.load(f)
        for k, v in self.hit_params_dict.items():
            table_num, data_num = map(int, k.split("-"))
            key = f"{table_num}-data"
            data_json["params"]["config"]["dataArg"][key][data_num - 1]["value"] = v
        with open("../data.json", "w") as f:
            json.dump(data_json, f, indent=2)

    def get_plugin_path(self):
        self.plugin_path = os.path.join(self.project_path, self.module_name, self.plugin_name)


def embedding_description(desc: str):
    return embedding_pipeline(desc).get()


def get_description(embedding) -> str:
    search_params = {"metric_type": "L2", "offset": 0}
    result = hiplot_plugins_collection.search(
        data=embedding,
        anns_field="embeddings",
        param=search_params,
        limit=5,
        output_fields=["description", "name"]
    )
    docs = {}
    for hits in result:
        for hit in hits:
            description = hit.entity.get("description")
            description_decode = json.loads(description)
            hit_name = hit.entity.get("name")
            docs[hit_name] = description_decode
    return json.dumps(docs, ensure_ascii=False)


if __name__ == "__main__":
    query = "帮我给../data.txt文件画一幅区间区域图"
    t = Task(query)
    t.run()
