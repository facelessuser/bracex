# Changes

## 1.2.0

- **NEW**: Officially support Python 3.8.

## 1.1.1

- **FIX**: Vendor `pep562` in order to reduce dependencies.

## 1.1.0

- **NEW**: Deprecate `version` and `version_info` in favor of the more standard `__version__` and `__version_info__`.
- **FIX**: Proper iteration when using `iexpand`.

## 1.0.2

- **FIX**: Officially support Python 3.7.

## 1.0.1

- **FIX**: Allow zero increments in sequence ranges: `{1..10..0}`. Zero will be treated as one just like Bash does.

## 1.0.1

- **NEW**: Initial release.
