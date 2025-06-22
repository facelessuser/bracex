# Changes

## 2.6

-   **NEW**: Drop support for Python 3.8.
-   **NEW**: Add support for Python 3.14.

## 2.5.post1

-   **FIX**: Fix PyPI landing page.

## 2.5

-   **NEW** Add Python 3.13 support.

## 2.4

-   **NEW**: Formally declare support for Python 3.11 and 3.12.
-   **NEW**: Drop Python 3.7 support.

## 2.3.post1

-   **CHORE**: Fix issue where tar ball did not include all required files for running tests.

## 2.3

-   **NEW**: Drop Python 3.6 support.
-   **NEW**: Switch to Hatch build backend instead of Setuptools.

## 2.2.1

-   **FIX**: Remove excessive generator wrappers.
-   **FIX**: Use `AnyStr` for string static types instead of custom alias.

## 2.2

-   **NEW**: Support Python 3.10
-   **NEW**: Command line interface using `python3 -m bracex`
-   **NEW**: Add static types to API.

## 2.1.1

-   **FIX**: Expansion limit evaluated much too late and hanging can still occur with large expansions. Calculate
    expansion count and assert limit while parsing strings to reduce chance of hanging.

## 2.1

-   **NEW**: Drop support for Python 3.5.
-   **FIX**: Fix potential corner case in looping logic.

## 2.0.1

-   **FIX**: Officially support Python 3.9.

## 2.0

-   **NEW**: An expansion limit of `1000` is enforced by default. This can be controlled, or even removed, via the
    `limit` option.

## 1.4

-   **NEW**: Remove `version` and `version_info` and the associated deprecation code.

## 1.3

-   **NEW**: Drop Python 3.4 support.

## 1.2

-   **NEW**: Officially support Python 3.8.

## 1.1.1

-   **FIX**: Vendor `pep562` in order to reduce dependencies.

## 1.1

-   **NEW**: Deprecate `version` and `version_info` in favor of the more standard `__version__` and `__version_info__`.
-   **FIX**: Proper iteration when using `iexpand`.

## 1.0.2

-   **FIX**: Officially support Python 3.7.

## 1.0.1

-   **FIX**: Allow zero increments in sequence ranges: `{1..10..0}`. Zero will be treated as one just like Bash does.

## 1.0

-   **NEW**: Initial release.
