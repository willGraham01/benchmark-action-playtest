from random import choice
import string


def my_function() -> None:
    my_pointless_wrapper()
    print(my_nested_function())
    return


def my_nested_function(n_chars: int = 16) -> str:
    return "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(n_chars)
    )


def my_pointless_wrapper() -> None:
    for i in range(10):
        i += i
    return
