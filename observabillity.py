# observabillity.py
import os
import sys
import logging
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

def setup_observability():
    """
    Auto-instruments all LangGraph agents, LLM calls, and tool operations
    using OpenInference & OpenTelemetry standards silently.
    """
    os.makedirs("./logs", exist_ok=True)
    log_file_path = os.path.abspath("./logs/telemetry.log")

    print("\n" + "="*60)
    print("  AGENTIC OBSERVABILITY ENABLED (OpenInference / OpenTelemetry)")
    print("="*60)

    try:
        # Initialize Tracer Provider
        tracer_provider = TracerProvider()
        
        # Log OpenTelemetry traces silently to file instead of flooding stdout/stderr terminal
        log_file = open(log_file_path, "a", encoding="utf-8")
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter(out=log_file)))
        trace.set_tracer_provider(tracer_provider)

        # Enable OpenInference instrumentation for LangChain & LangGraph
        LangChainInstrumentor().instrument()

        print(f"[Observability] Telemetry active. Traces logged silently to: {log_file_path}\n")
    except Exception as e:
        print(f"[Observability Warning] Could not start telemetry exporter: {e}")

if __name__ == "__main__":
    setup_observability()
    print("[Observability] Test runner completed.")
