from .getkey import getkey


def cprint(ch, end=''):
    """
    Prints a string to the console without including a newline.

    Args:
        ch : The character string to print to the console.
        end : Optional character that will be added to the end of the string.
    """
    print(ch, end=end, flush=True)

#------------------------------------------------------------------------------

def getstr() -> str:
    """
    Retrieves a string of characters from the keyboard until the return key is pressed.

    Returns: String of UTF-8 text.
    """
    text = ''
    while True:
        ch = getkey().decode("utf-8")
        if ch == '\r': break
        text += ch
        cprint(ch)

    print()
    return text

#------------------------------------------------------------------------------

def str_to_bytes(input:str) -> bytes:
    """
    Converts a character string into a string of bytes.

    Args:
        input : character string to convert

    Returns:
        A byte encoded string.
    """

    if isinstance(input, str):
        return str.encode(input)
    return input

#------------------------------------------------------------------------------

if __name__ == "__main__":
    cprint("Enter a string of text: ")
    text = getstr()
    print(f"The text you entered was : \"{text}\"")
