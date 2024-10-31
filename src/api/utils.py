import socket
from contextlib import closing


def find_free_port() -> int:
    """Helper function to find an available port on the machine (to locally launch the API).

    This will likely assign a random port.

    !!! To be used only for debug/dev purposed - Don't run it on production !!!
    Credit to https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("localhost", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
