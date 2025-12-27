"""Tkinter-asyncio integration via thread-safe queue."""

import asyncio
import threading
import queue
from typing import Callable, Any, Optional
from dataclasses import dataclass


@dataclass
class AsyncTask:
    """Represents an async task to be executed."""

    coro_func: Callable[..., Any]
    args: tuple = ()
    kwargs: dict = None
    callback: Optional[Callable[[Any], None]] = None
    error_callback: Optional[Callable[[Exception], None]] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class AsyncBridge:
    """Bridge between Tkinter main thread and asyncio event loop."""

    def __init__(self):
        self._task_queue: queue.Queue = queue.Queue()
        self._result_queue: queue.Queue = queue.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self):
        """Start the async event loop in a background thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the async event loop."""
        self._running = False
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)

    def _run_loop(self):
        """Run the asyncio event loop in background thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        while self._running:
            # Process pending tasks
            try:
                task = self._task_queue.get_nowait()
                self._loop.run_until_complete(self._execute_task(task))
            except queue.Empty:
                # Run loop briefly to allow other async operations
                self._loop.run_until_complete(asyncio.sleep(0.01))

        self._loop.close()

    async def _execute_task(self, task: AsyncTask):
        """Execute an async task and queue the result."""
        try:
            result = await task.coro_func(*task.args, **task.kwargs)
            self._result_queue.put(("success", task, result))
        except Exception as e:
            self._result_queue.put(("error", task, e))

    def submit(
        self,
        coro_func: Callable[..., Any],
        *args,
        callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        **kwargs,
    ):
        """Submit an async task from Tkinter thread."""
        task = AsyncTask(
            coro_func=coro_func,
            args=args,
            kwargs=kwargs,
            callback=callback,
            error_callback=error_callback,
        )
        self._task_queue.put(task)

    def process_results(self, root):
        """Process results from the result queue (call from Tkinter mainloop)."""
        try:
            while True:
                status, task, result = self._result_queue.get_nowait()
                if status == "success" and task.callback:
                    task.callback(result)
                elif status == "error" and task.error_callback:
                    task.error_callback(result)
        except queue.Empty:
            pass

        # Schedule next check
        if self._running:
            root.after(50, lambda: self.process_results(root))
