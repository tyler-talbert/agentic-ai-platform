import logging
import structlog

def setup_logger():
    logging.basicConfig(format="%(message)s", stream=logging.StreamHandler())
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    return structlog.get_logger()
