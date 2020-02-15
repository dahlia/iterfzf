from typing import AnyStr, Iterable, Optional, Union

BUNDLED_EXECUTABLE: Optional[str]

def iterfzf(
    iterable: Iterable[AnyStr], *,
    # Search mode:
    extended: bool = ...,
    exact: bool = ...,
    case_sensitive: Optional[bool] = ...,
    # Interface:
    multi: Optional[Union[bool,int]] = ...,
    mouse: bool = ...,
    print_query: bool = ...,
    # Layout:
    prompt: str = ...,
    preview: Optional[str] = ...,
    # Misc:
    query: str = ...,
    encoding: Optional[str] = ...,
    executable: str = ...,
) -> Iterable[AnyStr]: ...
