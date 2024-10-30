import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

F = TypeVar("F", bound=Callable[..., Any])


def timeit(func: F) -> F:
    """Time function execution time."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa:ANN401
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = f"{end_time - start_time:.2f}"
        logger.info("Analyzing image took %s seconds", elapsed_time)
        return result

    return cast(F, wrapper)
