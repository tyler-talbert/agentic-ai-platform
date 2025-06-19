"""Service app package.

This package exposes orchestrator modules under the ``app.orchestrator``
namespace when running tests so import paths match across services.
"""

import importlib
import sys

try:
    orch_pkg = importlib.import_module(
        "agent_orchestrator.app.orchestrator"
    )
    sys.modules.setdefault("app.orchestrator", orch_pkg)
    kafka_prod = importlib.import_module(
        "agent_orchestrator.app.kafka_client.producer"
    )
    sys.modules.setdefault("app.kafka_client.producer", kafka_prod)
    kafka_cons = importlib.import_module(
        "agent_orchestrator.app.kafka_client.consumer"
    )
    sys.modules.setdefault("app.kafka_client.consumer", kafka_cons)
    grpc_mod = importlib.import_module(
        "agent_orchestrator.app.grpc_client"
    )
    sys.modules.setdefault("app.grpc_client", grpc_mod)
    sys.modules.setdefault(
        "app.orchestrator.orchestrator_engine",
        importlib.import_module(
            "agent_orchestrator.app.orchestrator.orchestrator_engine"
        ),
    )
except Exception:
    pass