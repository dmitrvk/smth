import contextlib
import io


def capture_stderr(function, *args, **kwargs):
    stream = io.StringIO()
    with contextlib.redirect_stderr(stream):
        function(*args, **kwargs)
    output = stream.getvalue()
    stream.close()
    return output


def capture_stdout(function, *args, **kwargs):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        function(*args, **kwargs)
    output = stream.getvalue()
    stream.close()
    return output
