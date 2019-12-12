[![Gitter][gitter-image]][gitter-link]
[![Unix Build Status][travis-image]][travis-link]
[![Windows Build Status][appveyor-image]][appveyor-link]
[![Coverage][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
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

[github-ci-image]: https://github.com/facelessuser/bracex/workflows/build/badge.svg
[github-ci-link]: https://github.com/facelessuser/bracex/actions?workflow=build
[gitter-image]: https://img.shields.io/gitter/room/facelessuser/bracex.svg?logo=gitter&color=fuchsia&logoColor=cccccc
[gitter-link]: https://gitter.im/facelessuser/bracex
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/bracex/master.svg?logo=codecov&logoColor=cccccc
[codecov-link]: https://codecov.io/github/facelessuser/bracex
[appveyor-image]: https://img.shields.io/appveyor/ci/facelessuser/bracex/master.svg?label=appveyor&logo=appveyor&logoColor=cccccc
[appveyor-link]: https://ci.appveyor.com/project/facelessuser/bracex
[travis-image]: https://img.shields.io/travis/facelessuser/bracex/master.svg?label=travis&logo=travis%20ci&logoColor=cccccc
[travis-link]: https://travis-ci.org/facelessuser/bracex
[pypi-image]: https://img.shields.io/pypi/v/bracex.svg?logo=pypi&logoColor=cccccc
[pypi-link]: https://pypi.python.org/pypi/bracex
[python-image]: https://img.shields.io/pypi/pyversions/bracex?logo=python&logoColor=cccccc
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg
