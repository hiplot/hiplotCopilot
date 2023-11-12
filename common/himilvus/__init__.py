from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection

# connect
connections.connect(alias="default", host="localhost", port="19530")
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
