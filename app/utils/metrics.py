import psutil
import logging
import time
import threading

_metrics_lock = threading.Lock()

def start_metrics():
    metrics_event = threading.Event()
    metrics_thread = threading.Thread(
        target=metrics_loop,
        args=(metrics_event,),
        daemon=True
    )
    metrics_thread.start()
    return metrics_event, metrics_thread

def stop_metrics(metrics_event, metrics_thread):
    metrics_event.set()
    metrics_thread.join(timeout=2)

def metrics_loop(stop_event, interval=60):
    while not stop_event.is_set():
        log_infra_metrics()
        time.sleep(interval)

def log_infra_metrics():
    with _metrics_lock:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

    logging.info(
        "SYSTEM METRICS | CPU=%5.1f%% | MEM=%5.1f%% | DISK=%5.1f%%",
        cpu, mem, disk
    )
