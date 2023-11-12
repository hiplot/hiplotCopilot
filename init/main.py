import logging
import os
import shutil
import subprocess
import hashlib
import time

from towhee import AutoPipes
from tqdm import tqdm
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain.text_splitter import TokenTextSplitter

from common.himilvus import hiplot_doc_collection

git_url = "https://github.com/hiplot/docs.git"
docs_directory = "docs"
print("Loading embedding model......")
embedding_pipeline = AutoPipes.pipeline("sentence_embedding")
print("Loading embedding model success!")
splitter = TokenTextSplitter(chunk_size=300, chunk_overlap=50)


def docsExists() -> bool:
    current_directory = os.getcwd()
    docs_folder = os.path.join(current_directory, docs_directory)
    return os.path.exists(docs_folder) and os.path.isdir(docs_folder)


def git_clone():
    try:
        subprocess.run(["git", "clone", git_url], check=True)
        print("Git clone successful")
    except subprocess.CalledProcessError as e:
        print(f"Git clone failed: {e}")


def delete_dir():
    for root, dirs, files in os.walk(docs_directory):
        for file in files:
            path = os.path.join(root, file)
            os.chmod(path, 0o777)
    shutil.rmtree(docs_directory)
    print(f"Remove {docs_directory} success")


def get_all_md_filepath() -> list:
    os.chdir(docs_directory)
    current_directory = os.getcwd()

    markdown_filepath = []
    for root, dirs, files in os.walk(current_directory):
        for file in files:
            if file.endswith(".md"):
                markdown_filepath.append(os.path.join(root, file))
    return markdown_filepath


def split_and_store_md(filepath: str):
    # load
    doc_md = UnstructuredMarkdownLoader(filepath).load()
    # split
    doc_md_split = splitter.split_documents(doc_md)
    # store
    for i in tqdm(range(len(doc_md_split))):
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
    print("Loading document into milvus......")
    for i in range(len(fps)):
        print(f"Total document: {i + 1}/{len(fps)}")
        split_and_store_md(fps[i])
    # load
    hiplot_doc_collection.load()


if __name__ == "__main__":
    if docsExists():
        print("Document path <docs> exists, continue clone? (y/n)")
        if "y" == input():
            delete_dir()
            git_clone()
    else:
        git_clone()
    start_time = time.time()
    store_documents()
    end_time = time.time()
    use_time = end_time - start_time
    print(f"Use time: {int(use_time)}s")
    print("Milvus init success!")
