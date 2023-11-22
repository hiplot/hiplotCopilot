import hashlib
import json
import os
import re
import sys
import time

from tqdm import tqdm

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.print_color import print_green, print_yellow
from common.tools import git_clone_path, delete_dir
from common.hiMilvus import hiplot_plugins_collection
from common.hiTowhee import embedding_pipeline

git_url = "https://github.com/hiplot/plugins-open.git"
plugins_directory = "plugins-open"
support_modules = {"./basic"}


def get_description_str(description_filepath: dict, limit: int = 4096) -> str:
    # 优先提取meta中的描述
    meta_json_filepath = description_filepath["meta"]
    readme_md_filepath = description_filepath["readme"]
    description = ""
    if meta_json_filepath != "":
        with open(meta_json_filepath, "r", encoding="utf-8") as f:
            meta_json = json.load(f)
            new_json_dict = {
                "name": meta_json["name"],
                "alias": meta_json["alias"],
                "intro": meta_json["intro"]
            }
    description += json.dumps(new_json_dict, ensure_ascii=False)
    if readme_md_filepath != "":
        with open(readme_md_filepath, "r", encoding="utf-8") as f:
            # 后续如遇到prompt过长问题可考虑压缩readme内容
            readme_str = f.read()
            description += readme_str
    if len(description) > limit:
        print_yellow(
            f"description length exceeding max length, get:{len(description)}, limit:{limit}, filepath:{description_filepath}")
    return description[:limit]


def get_plugins_description_filepath() -> dict[str, dict[str, dict[str, str]]]:
    path = os.path.join(os.getcwd(), plugins_directory)
    absolute_support_modules = {os.path.normpath(os.path.join(path, module)) for module in support_modules}
    pattern = re.compile('|'.join(re.escape(module) for module in absolute_support_modules))
    filepath = {}
    for root, dirs, files in os.walk(path):
        # 目前仅支持basic模块
        if not re.match(pattern, root):
            continue
        # 开源版本仅支持调用开源插件
        if "plot.R" not in files:
            continue

        module_name = os.path.basename(os.path.dirname(root))
        if module_name not in filepath:
            filepath[module_name] = {}

        meta_json = ""
        readme_md = ""
        for file in files:
            if file.lower() == "meta.json":
                meta_json = os.path.join(root, file)
            elif file.lower() == "readme.md":
                readme_md = os.path.join(root, file)

        if readme_md == "":
            for file in files:
                if file.lower() == "readme-zh_cn.md":
                    readme_md = os.path.join(root, file)

        module_path = filepath[module_name]
        basename = os.path.basename(root)
        module_path[basename] = {}
        module_path[basename]["meta"] = meta_json
        module_path[basename]["readme"] = readme_md
    return filepath


def store_description(module_name: str, name: str, description: str):
    description_byte = description.encode("utf-8")
    hash_value = hashlib.md5(description_byte).hexdigest()
    res = hiplot_plugins_collection.query(f"id==\"{hash_value}\"")
    if len(res) != 0:
        return
    embedding = embedding_pipeline(description).get()
    entity = [
        [hash_value],
        [module_name],
        [name],
        [description],
        [embedding[0]]
    ]
    hiplot_plugins_collection.insert(entity)


def store_info():
    filepaths = get_plugins_description_filepath()
    num = 0
    for module_name, module_paths in filepaths.items():
        num += 1
        print_green(f"Module {num}/{len(filepaths)}")
        for basename, description_filepath in tqdm(module_paths.items(), total=len(module_paths), ncols=50):
            description_str = get_description_str(description_filepath)
            store_description(module_name, basename, description_str)
    hiplot_plugins_collection.load()


if __name__ == "__main__":
    git_clone_path(git_url, plugins_directory)
    # delete_dir(plugins_directory)
    start_time = time.time()
    store_info()
    end_time = time.time()
    use_time = end_time - start_time
    print_green(f"Use time: {int(use_time)}s")
    print_green("hiplot_plugins init plugins successful!")
