import bytewax.operators as op
from bytewax.dataflow import Dataflow

from data_flow.stream_input import RabbitMQSource
from data_flow.stream_output import SuperlinkedOutputSink
from data_logic.dispatchers import (
    CleaningDispatcher,
    RawDispatcher,
)
from superlinked_client import SuperlinkedClient


flow = Dataflow("Streaming RAG feature pipeline")
stream = op.input("input", flow, RabbitMQSource())
stream = op.map("raw", stream, RawDispatcher.handle_mq_message)
stream = op.map("clean", stream, CleaningDispatcher.dispatch_cleaner)
op.output(
    "superlinked_output",
    stream,
    SuperlinkedOutputSink(client=SuperlinkedClient()),
)
