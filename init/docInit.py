import os
import hashlib
import sys
import time

from tqdm import tqdm
from langchain.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain.text_splitter import TokenTextSplitter

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from common.hiMilvus import hiplot_doc_collection
from common.hiTowhee import embedding_pipeline
from common.print_color import print_green
from common.tools import delete_dir, git_clone_path

git_url_doc = "https://github.com/hiplot/docs.git"
docs_directory = "docs"
splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=100)


def get_all_md_filepath() -> list:
    path = os.path.join(os.getcwd(), docs_directory)
    markdown_filepath = []
    for root, dirs, files in os.walk(path):
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


def store_documents():
    fps = get_all_md_filepath()
    print_green("Loading document into milvus......")
    for i in range(len(fps)):
        print_green(f"Total document: {i + 1}/{len(fps)}")
        split_and_store_md(fps[i])
    # load
    hiplot_doc_collection.load()


if __name__ == "__main__":
    git_clone_path(git_url_doc, docs_directory)

    start_time = time.time()
    store_documents()
    end_time = time.time()
    use_time = end_time - start_time
    print_green(f"Use time: {int(use_time)}s")
    # delete_dir(docs_directory)
    print_green("hiplot_doc init docs successful!")
