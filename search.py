from tantivy import Index, SchemaBuilder, Document
import tantivy

# Declaring our schema.
schema_builder = tantivy.SchemaBuilder()
schema_builder.add_text_field("invoice_id", stored=True)
schema_builder.add_text_field("content", stored=True)
schema = schema_builder.build()

# Creating our index (in memory, but filesystem is available too)
index = tantivy.Index(schema)


# Adding one document.
writer = index.writer()
writer.add_document(tantivy.Document(
    invoice_id=["The Old Man and the Sea"],
    content=["He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish."],
))
writer.add_document(tantivy.Document(
    invoice_id=["first document"],
    content=["this is the first document"],
))
writer.add_document(tantivy.Document(
    invoice_id=["second document"],
    content=["this is the second document"],
))
writer.commit()

# writer.add_document({"title": "First document", "body": "This is the first document."})
# writer.add_document({"title": "Second document", "body": "This is the second document."})
# writer.commit()


# Reload the index to ensure it points to the last commit.
index.reload()
searcher = index.searcher()
query = index.parse_query("first this", ["content"])

search_results = searcher.search(query, 10)
for score, doc_address in search_results.hits:
    # Retrieve the document
    document = searcher.doc(doc_address)
    content = document.get_first("content")
    print(content)