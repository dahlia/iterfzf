from typing import AnyStr, Iterable, Optional

BUNDLED_EXECUTABLE: Optional[str]

def iterfzf(
    iterable: Iterable[AnyStr], *,
    # Search mode:
    extended: bool = ...,
    exact: bool = ...,
    case_sensitive: Optional[bool] = ...,
    no_sort: bool = ...,
    # Interface:
    multi: bool = ...,
    mouse: bool = ...,
    print_query: bool = ...,
    bind: Optional[str] = ...,
    # Layout:
    height: str = ...,
    prompt: str = ...,
    ansi: bool = ...,
    preview: Optional[str] = ...,
    # Display:
    ansi: bool = ...,
    # Misc:
    query: Optional[str] = ...,
    encoding: Optional[str] = ...,
    executable: str = ...,
) -> Iterable[AnyStr]: ...
