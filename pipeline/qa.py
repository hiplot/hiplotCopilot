from typing import List

from towhee import pipe
from langchain.schema.document import Document
from langchain.chains.question_answering import load_qa_chain

from common.hiTowhee import embedding_pipeline
from common.hiMilvus import hiplot_doc_collection
from llm.chatOpenAI import chat_openai


def get_documents(embedding) -> List[Document]:
    search_params = {"metric_type": "L2", "offset": 0}
    result = hiplot_doc_collection.search(
        data=embedding,
        anns_field="embeddings",
        param=search_params,
        limit=10,
        output_fields=["content"]
    )
    documents = []
    for hits in result:
        for hit in hits:
            content = hit.entity.get("content")
            doc = Document(page_content=content)
            documents.append(doc)
    return documents


def get_gpt_result(documents: List[Document], query: str) -> str:
    llm = chat_openai(0.5)
    chain = load_qa_chain(llm, chain_type="stuff")
    return chain.run(input_documents=documents, question=query)


hiplot_doc_qa_pipeline = (
    pipe.input("query")
    .map("query", "embedding", lambda query: embedding_pipeline(query).get())
    .map("embedding", "documents", get_documents)
    .map(("documents", "query"), "result", get_gpt_result)
    .output("result")
)

if __name__ == "__main__":
    print(hiplot_doc_qa_pipeline("Hello world!").get()[0])
