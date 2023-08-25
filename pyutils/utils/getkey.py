try:
    import msvcrt

    def getkey():
        """Wait for keypress and return a single character string."""
        return msvcrt.getch()

except ImportError:

    import sys
    import tty
    import termios

    def getkey():
        """OS-independent method to retrieve a keyboard keypress and return it as a single character string."""
        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCADRAIN, original_attributes)
        return ch

    # If either of the Unix-specific tty or termios are not found, we allow the ImportError
    # to propogate from here.
