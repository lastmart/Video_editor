from __future__ import unicode_literals, print_function
from tqdm import tqdm
import contextlib
import gevent
import gevent.monkey
import os
import shutil
import socket
import tempfile
from .utils import convert_date_to_seconds

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
def show_progress(total_duration):
    """Create a unix-domain socket to watch progress and render tqdm
    progress bar."""
    with tqdm(total=round(total_duration, 2)) as bar:
        def handler(key, value):
            if key == 'out_time':
                time = convert_date_to_seconds(value)
                bar.update(time - bar.n)
            elif key == 'progress' and value == 'end':
                bar.update(bar.total - bar.n)

        with _watch_progress(handler) as socket_filename:
            yield socket_filename


# if __name__ == '__main__':
#     total_duration = float(
#         ffmpeg.probe(
#             r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4")[
#             'format']['duration'])
#
#     with show_progress(total_duration * 2) as socket_filename:
#         # (ffmpeg
#         #  .input(r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4")
#         #  .output(r'/mnt/c/Users/egore/OneDrive/Документы/output.mp4')
#         #  .global_args('-progress', 'unix://{}'.format(socket_filename))
#         #  .overwrite_output()
#         #  .run(capture_stdout=True, capture_stderr=True)
#         #  )
#
#         set_video_speed_and_save(r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4",
#                                  0.5, r'/mnt/c/Users/egore/OneDrive/Документы/output.mp4', is_overwrite=True, socket_filename=socket_filename)
#
#         # input_video = ffmpeg.input(
#         #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4")
#         # output_path = r'/mnt/c/Users/egore/OneDrive/Документы/output.mp4'
#         # video = input_video.video.filter('setpts', f'{1 / 2:0.01}*PTS')
#         # audio = (input_video.audio
#         #          .filter('asetpts', f'{round(1 / 2, 1)}*PTS')
#         #          .filter("atempo", 2))
#         # a = ffmpeg.concat(video, audio, v=1, a=1).node
#         # out = (ffmpeg.output(a[0], a[1], output_path, format='mp4')
#         #        .global_args('-progress',
#         #                     'unix://{}'.format(socket_filename))
#         #        .overwrite_output()
#         #        .run(capture_stdout=True, capture_stderr=True)
#         #        )
