from towhee import AutoPipes

from common.print_color import print_green

print_green("Loading embedding model......")
embedding_pipeline = AutoPipes.pipeline("sentence_embedding")
print_green("Loading embedding model successful!")
