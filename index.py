import tantivy

# Declaring our schema.
schema_builder = tantivy.SchemaBuilder()
schema_builder.add_text_field("invoice_id", stored=True)
schema_builder.add_text_field("sub_invoice_id", stored=True)
schema_builder.add_text_field("content", stored=True)
schema_builder.add_text_field("money", stored=True)
schema_builder.add_text_field("organization", stored=True)
schema_builder.add_text_field("bill_code", stored=True)
schema_builder.add_text_field("NDKT_code", stored=True)
schema_builder.add_text_field("economic_code", stored=True)
schema_builder.add_text_field("NSNN_code", stored=True)
schema_builder.add_text_field("organization_received", stored=True)
schema_builder.add_text_field("chapter_code", stored=True)
schema = schema_builder.build()

# Creating our index (in memory, but filesystem is available too)
index = tantivy.Index(schema, path='./docstore')

