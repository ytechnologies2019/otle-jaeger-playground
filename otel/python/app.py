from flask import Flask, request, Response
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
import time
import requests as rq

resource = Resource(attributes={
    "service.name": "flask_otel_POC"
})

# Set up the Tracer Provider
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
# Set up the OTLP exporter to send data to the OpenTelemetry Collector via gRPC
otlp_exporter = OTLPSpanExporter(
    endpoint="grpc://20.185.47.228:4317",  # Replace with your OTLP receiver endpoint
    insecure=True  # Set to True if not using TLS
)
# Set up a BatchSpanProcessor for exporting spans
span_processor = BatchSpanProcessor(otlp_exporter)
trace_provider = trace.get_tracer_provider()
trace_provider.add_span_processor(span_processor)
# Create and configure the Flask app
app = Flask(__name__)
# Instrument Flask to automatically create spans for requests
FlaskInstrumentor().instrument_app(app)
# Optionally, instrument the requests library to trace outbound HTTP calls
# Define a simple route
@app.route("/")
def main():
    with tracer.start_as_current_span("main"):
        return "Hello, OpenTelemetry!"
@app.route("/get_seg_offer",methods=['POST'])
def get_ppy_offer():
    with tracer.start_as_current_span("get_seg_offer") as route_span:
        request_data=request.get_json()
        msisdn=request_data.get('msisdn')
        response=None
        with tracer.start_as_current_span("fetch API") as fetch_span:
             response=rq.get('http://google.com/')
        actual_response=Response()
        actual_response.content_type='application/json'
        actual_response.data=response.content
        return actual_response
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)