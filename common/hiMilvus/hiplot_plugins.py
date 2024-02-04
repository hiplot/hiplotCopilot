from pymilvus import FieldSchema, DataType, CollectionSchema, Collection

from common.print_color import print_green


def build_hiplot_plugins() -> Collection:
    print_green("Building hiplot_plugins collection and index......")

    # create collection
    fields = [
        FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=32, is_primary=True),
        FieldSchema(name="module", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=8192),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384)
    ]
    schema = CollectionSchema(fields, "Hiplot plugins")
    hiplot_plugins_collection = Collection("hiplot_plugins", schema)

    # create index
    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    hiplot_plugins_collection.create_index("embeddings", index)
    print_green("Collection and index build successful!")
    hiplot_plugins_collection.load()
    return hiplot_plugins_collection
