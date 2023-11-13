import logging
import os
import shutil
import subprocess
import hashlib
import sys
import time

from tqdm import tqdm
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain.text_splitter import TokenTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.hiMilvus import hiplot_doc_collection
from common.hiEmbedding import embedding_pipeline
from common.print_color import print_green, print_yellow

git_url = "https://github.com/hiplot/docs.git"
docs_directory = "docs"
splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=50)


def docsExists() -> bool:
    current_directory = os.getcwd()
    docs_folder = os.path.join(current_directory, docs_directory)
    return os.path.exists(docs_folder) and os.path.isdir(docs_folder)


def git_clone():
    try:
        subprocess.run(["git", "clone", git_url], check=True)
        print_green("Git clone successful")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git clone failed: {e}")


def delete_doc_dir():
    for root, dirs, files in os.walk(docs_directory):
        for file in files:
            path = os.path.join(root, file)
            os.chmod(path, 0o777)
    shutil.rmtree(docs_directory)
    print_green(f"Clean {docs_directory} successful.")


def get_all_md_filepath() -> list:
    os.chdir(docs_directory)
    current_directory = os.getcwd()

    markdown_filepath = []
    for root, dirs, files in os.walk(current_directory):
        for file in files:
            if file.endswith(".md"):
                markdown_filepath.append(os.path.join(root, file))
    os.chdir("..")
    return markdown_filepath


def split_and_store_md(filepath: str):
    # load
    doc_md = UnstructuredMarkdownLoader(filepath).load()
    # split
    doc_md_split = splitter.split_documents(doc_md)
    # store
    for i in tqdm(range(len(doc_md_split)), ncols=50):
        doc = doc_md_split[i]
        store_md(doc.page_content)


def store_md(content: str):
    content_byte = content.encode("utf-8")
    hash_value = hashlib.md5(content_byte).hexdigest()
    res = hiplot_doc_collection.query(f"id == \"{hash_value}\"")
    if len(res) != 0:
        return
    embedding = embedding_pipeline(content).get()
    entity = [
        [hash_value],
        [embedding[0]],
        [content]
    ]
    hiplot_doc_collection.insert(entity)


def show_file_content(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            print(content)
    except FileNotFoundError as e:
        logging.error(e)


def store_documents():
    fps = get_all_md_filepath()
    print_green("Loading document into milvus......")
    for i in range(len(fps)):
        print_green(f"Total document: {i + 1}/{len(fps)}")
        split_and_store_md(fps[i])
    # load
    hiplot_doc_collection.load()


if __name__ == "__main__":
    if docsExists():
        print_yellow("Document path <docs> exists, continue clone? (y/n/q)")
        c = input().lower()
        if c == "y":
            delete_doc_dir()
            git_clone()
        elif c == "q":
            sys.exit()
    else:
        git_clone()
    start_time = time.time()
    store_documents()
    end_time = time.time()
    use_time = end_time - start_time
    print_green(f"Use time: {int(use_time)}s")
    delete_doc_dir()
    print_green("Milvus init successful!")
