import tantivy

# Declaring our schema.
schema_builder = tantivy.SchemaBuilder()
schema_builder.add_text_field("invoice_id", stored=True)
schema_builder.add_text_field("content", stored=True)
schema = schema_builder.build()

# Creating our index (in memory, but filesystem is available too)
index = tantivy.Index(schema, path='./docstore')