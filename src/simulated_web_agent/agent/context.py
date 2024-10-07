import pathlib
from contextvars import ContextVar

# api_call_manager: "agent.LogApiCall" = None
# run_path: pathlib.Path = None

run_path = ContextVar("run_path", default=None)
api_call_manager = ContextVar("api_call_manager", default=None)
browser_context = ContextVar("browser_context", default=None)
