from __future__ import unicode_literals, print_function
from .utils import convert_time_to_seconds
import PySimpleGUI as sg
from tqdm import tqdm
from math import ceil
import contextlib
import tempfile
import gevent
import gevent.monkey
import shutil
import socket
import os

gevent.monkey.patch_all(thread=False)


@contextlib.contextmanager
def _tmpdir_scope():
    tmpdir = tempfile.mkdtemp()
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir)


def _do_watch_progress(sock, handler):
    """Function to run in a separate gevent greenlet to read progress
    events from a unix-domain socket."""
    connection, client_address = sock.accept()
    data = b''
    try:
        while True:
            more_data = connection.recv(16)
            if not more_data:
                break
            data += more_data
            lines = data.split(b'\n')
            for line in lines[:-1]:
                line = line.decode()
                parts = line.split('=')
                key = parts[0] if len(parts) > 0 else None
                value = parts[1] if len(parts) > 1 else None
                handler(key, value)
            data = lines[-1]
    finally:
        connection.close()


@contextlib.contextmanager
def _watch_progress(handler):
    """Context manager for creating a unix-domain socket and listen for
    ffmpeg progress events.

    The socket filename is yielded from the context manager and the
    socket is closed when the context manager is exited.

    Args:
        handler: a function to be called when progress events are
            received; receives a ``key`` argument and ``value``
            argument. (The example ``show_progress`` below uses tqdm)

    Yields:
        socket_filename: the name of the socket file.
    """
    with _tmpdir_scope() as tmpdir:
        socket_filename = os.path.join(tmpdir, 'sock')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        with contextlib.closing(sock):
            sock.bind(socket_filename)
            sock.listen(1)
            try:
                child = gevent.spawn(_do_watch_progress, sock, handler)
                yield socket_filename
            except:
                gevent.kill(child)
                raise


@contextlib.contextmanager
def show_progress_in_console(total_duration: float) -> None:
    """Create a unix-domain socket to watch progress and render tqdm
    progress bar."""
    with tqdm(total=total_duration) as bar:
        def console_handler(key: str, value: str) -> None:
            if key == 'out_time':
                time = convert_time_to_seconds(value)
                bar.update(time - bar.n)
            elif key == 'progress' and value == 'end':
                bar.update(bar.total - bar.n)

        with _watch_progress(console_handler) as socket_filename:
            yield socket_filename


@contextlib.contextmanager
def show_progress_in_gui(total_duration: float) -> None:
    """Create a unix-domain socket to watch progress and render PuSimpleGUI
        progress bar."""
    total_duration = ceil(total_duration)

    def gui_handler(key: str, value: str) -> None:
        if key == 'out_time':
            time = convert_time_to_seconds(value)
            sg.one_line_progress_meter('Progress bar', time, total_duration)
        elif key == 'progress' and value == 'end':
            sg.one_line_progress_meter('Progress bar', total_duration, total_duration)

    with _watch_progress(gui_handler) as socket_filename:
        yield socket_filename
