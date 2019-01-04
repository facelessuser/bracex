[![Unix Build Status][travis-image]][travis-link]
[![Windows Build Status][appveyor-image]][appveyor-link]
[![Coverage][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
![License][license-image-mit]
# Bracex

Bracex is a brace expanding library (à la Bash) for Python. Brace expanding is used to generate arbitrary strings.


```console
$ echo {{a,b},c}d
ad bd cd
```

Bracex adds this ability to Python:

```python
>>> bracex.expand(r'file-{{a,b},c}d.txt')
['file-ad.txt', 'file-bd.txt', 'file-cd.txt']
```

## Install

```console
$ pip install bracex
```

## Documentation

Documentation is found here: http://facelessuser.github.io/bracex/.

## License

MIT License

Copyright (c) 2018 - 2019 Isaac Muse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/bracex/master.svg
[codecov-link]: https://codecov.io/github/facelessuser/bracex
[travis-image]: https://img.shields.io/travis/facelessuser/bracex/master.svg?label=Unix%20Build
[travis-link]: https://travis-ci.org/facelessuser/bracex
[appveyor-image]: https://img.shields.io/appveyor/ci/facelessuser/bracex/master.svg?label=Windows%20Build&logo=appveyor
[appveyor-link]: https://ci.appveyor.com/project/facelessuser/bracex
[pypi-image]: https://img.shields.io/pypi/v/bracex.svg
[pypi-link]: https://pypi.python.org/pypi/bracex
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg
