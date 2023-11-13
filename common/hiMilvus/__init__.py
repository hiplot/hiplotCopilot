import sys

from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection
from common.print_color import print_green, print_red

try:
    # connect
    print_green("Connecting milvus......")
    connections.connect(alias="default", host="localhost", port="19530")
    print_green("Milvus connect successful!")

    print_green("Building hiplot_doc collection and index......")
    # create collection
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=32, is_primary=True),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096)
    ]
    schema = CollectionSchema(fields, "Hiplot docs")
    hiplot_doc_collection = Collection("hiplot_doc", schema)
    # create index
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    hiplot_doc_collection.create_index("embeddings", index)
    print_green("Collection and index build successful!")
    hiplot_doc_collection.load()
except Exception as e:
    print_red(f"{e}")
    sys.exit()
