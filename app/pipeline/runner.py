import time, subprocess
import logging
from dataclasses import dataclass
from app.utils.logger import setup_logger

@dataclass
class PipelineStep:
    name: str
    command: list
    delay_after: int = 0

def run_pipeline(steps):
    setup_logger()
    for step in steps:
        logging.info(f"Running step: {step.name}")
        result = subprocess.run(step.command)
        if result.returncode != 0:
            logging.error(f"Step failed: {step.name} (exit code {result.returncode})")
            return result.returncode
        if step.delay_after:
            logging.info(f"Waiting {step.delay_after} seconds after step: {step.name}")
            time.sleep(step.delay_after)

    logging.info("Pipeline completed successfully")
    return 0
