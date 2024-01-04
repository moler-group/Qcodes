import logging
import threading
from collections.abc import Callable, Sequence
from typing import Any, Generic, TypeVar

_LOG = logging.getLogger(__name__)

T = TypeVar("T")


class RespondingThread(threading.Thread, Generic[T]):
    """
    Thread subclass for parallelizing execution. Behaves like a
    regular thread but returns a value from target, and propagates
    exceptions back to the main thread when this value is collected.

    The `output` method joins the thread, then checks for errors and
    returns the output value.

    so, if you have a function `f` where `f(1, 2, a=3) == 4`, then:

    >>> thread = RespondingThread(target=f, args=(1, 2), kwargs={'a': 3})
    >>> thread.start()
    >>> # do other things while this is running
    >>> out = thread.output()  # out is 4
    """

    def __init__(
        self,
        target: Callable[..., T],
        args: Sequence[Any] = (),
        kwargs: dict[str, Any] | None = None,
        *args2: Any,
        **kwargs2: Any,
    ):
        if kwargs is None:
            kwargs = {}

        super().__init__(*args2, **kwargs2)

        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._exception: Exception | None = None
        self._output: T | None = None

    def run(self) -> None:
        _LOG.debug(f"Executing {self._target} on thread: {threading.get_ident()}")
        try:
            self._output = self._target(*self._args, **self._kwargs)
        except Exception as e:
            self._exception = e

    def output(self, timeout: float | None = None) -> T | None:
        self.join(timeout=timeout)

        if self._exception:
            e = self._exception
            self._exception = None
            raise e

        return self._output


def thread_map(
    callables: Sequence[Callable[..., T]],
    args: Sequence[Sequence[Any]] | None = None,
    kwargs: Sequence[dict[str, Any]] | None = None,
) -> list[T | None]:
    """
    Evaluate a sequence of callables in separate threads, returning
    a list of their return values.

    Args:
        callables: A sequence of callables.
        args (Optional): A sequence of sequences containing the positional
            arguments for each callable.
        kwargs (Optional): A sequence of dicts containing the keyword arguments
            for each callable.

    """
    if args is None:
        args = ((),) * len(callables)
    if kwargs is None:
        empty_dict: dict[str, Any] = {}
        kwargs = (empty_dict,) * len(callables)
    threads = [
        RespondingThread(target=c, args=a, kwargs=k)
        for c, a, k in zip(callables, args, kwargs)
    ]

    for t in threads:
        t.start()

    return [t.output() for t in threads]
