from uv_boilerplate.main import hello_world


def test_hello_world() -> None:
    """
    Test the basic hello world functionality.
    """
    if hello_world() != "Hello World":
        raise ValueError('Expected value to be "Hello World"')
    assert True
