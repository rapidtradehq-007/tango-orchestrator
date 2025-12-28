import sys
from src.pipeline.runner import PipelineStep, run_pipeline
from src.config.settings import CONFIG
from src.utils.metrics import start_metrics, stop_metrics


def main():
    if not CONFIG["EMAIL"] or not CONFIG["PASSWORD"]:
        raise RuntimeError("EMAIL or PASSWORD env vars not set")

    metrics_event, metrics_thread = start_metrics()

    try:
        steps = [
            PipelineStep("Customer Collector", [sys.executable, "-m", "src.workflows.collectors.customer_collector"], CONFIG["PIPELINE_DELAY_BETWEEN_STEPS_SECONDS"]),
            PipelineStep("Message Sender", [sys.executable, "-m", "src.workflows.senders.message_sender"]),
        ]
        run_pipeline(steps)

    finally:
        stop_metrics(metrics_event, metrics_thread)

if __name__ == "__main__":
    main()
