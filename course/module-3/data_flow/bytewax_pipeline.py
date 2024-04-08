import bytewax.operators as op
from streaming_pipeline.db.qdrant import connection
from bytewax.dataflow import Dataflow
from streaming_pipeline.data_flow.stream_input import RabbitMQSource
from streaming_pipeline.data_flow.stream_output import QdrantOutput
from streaming_pipeline.data_logic.dispatchers import RawDispatcher, CleaningDispatcher, ChunkingDispatcher, EmbeddingDispatcher


flow = Dataflow("RAG Data Flow")
stream = op.input("input", flow, RabbitMQSource())
stream = op.map('raw dispatch', stream, RawDispatcher.handle_mq_message)
stream = op.map('clean dispatch', stream, CleaningDispatcher.dispatch_cleaner)
op.output('cleaned data insert to qdrant', stream, QdrantOutput(connection=connection, sink_type='clean'))
stream = op.flat_map('chunk dispatch', stream, ChunkingDispatcher.dispatch_chunker)
stream = op.map('embedded chunk dispatch', stream, EmbeddingDispatcher.dispatch_embedder)
op.output('embedded data insert to qdrant', stream, QdrantOutput(connection=connection, sink_type='vector'))
