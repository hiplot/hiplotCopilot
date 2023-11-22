import sys

from pymilvus import connections
from common.print_color import print_green, print_red
from common.hiMilvus.hiplot_doc import build_hiplot_doc
from common.hiMilvus.hiplot_plugins import build_hiplot_plugins

try:
    # connect
    print_green("Connecting milvus......")
    connections.connect(alias="default", host="localhost", port="19530")
    print_green("Milvus connect successful!")
    # build
    hiplot_doc_collection = build_hiplot_doc()
    hiplot_plugins_collection = build_hiplot_plugins()

except Exception as e:
    print_red(f"{e}")
    sys.exit()
