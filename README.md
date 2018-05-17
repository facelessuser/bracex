[![Unix Build Status][travis-image]][travis-link]
[![Coverage][codecov-image]][codecov-link]
[![pypi-version][pypi-image]][pypi-link]
![License][license-image-mit]
# Bracex

Bracex is a brace expanding library (à la Bash) for Python. Brace expanding is used to generate arbitrary strings.


```console
> echo {{a,b},c}d
ad bd cd
```

Bracex adds this ability to Python:

```python
>>> bracex.expand(r'file-{1,2,3}.txt')
['file-1.txt', 'file-2.txt', 'file-3.txt']
```

```python
>>> bracex.expand(r'file-{1,2,3}.txt')
['file-1.txt', 'file-2.txt', 'file-3.txt']
```

```python
>>> bracex.expand(r'-v{,,}')
['-v', '-v', '-v']
```

Nested braces:

```python
>>> bracex.expand(r'file-{{a,b},c}d.txt')
['file-ad.txt', 'file-bd.txt', 'file-cd.txt']
```

Numerical sequences:

```python
>>> bracex.expand(r'file{0..3}.txt')
['file0.txt', 'file1.txt', 'file2.txt', 'file3.txt']
```

```python
>>> bracex.expand(r'file{0..6..2}.txt')
['file0.txt', 'file2.txt', 'file4.txt', 'file6.txt']
```

```python
>>> bracex.expand(r'file{00..10..5}.jpg')
['file00.jpg', 'file05.jpg', 'file10.jpg']
```

Alphabetic sequences:

```python
>>> bracex.expand(r'file{A..D}.txt')
['fileA.txt', 'fileB.txt', 'fileC.txt', 'fileD.txt']
```

```python
>>> bracex.expand(r'file{A..G..2}.txt')
['fileA.txt', 'fileC.txt', 'fileE.txt', 'fileG.txt']
```

Allows escaping:

```python
>>> bracex.expand(r'file\{00..10..5}.jpg')
['file{00..10..5}.jpg']
```

```python
>>> bracex.expand(r'file\{00..10..5}.jpg', keep_escapes=True)
['file\\{00..10..5}.jpg']
```

Bracex will **not** expand braces in the form of `${...}`:

```python
>>> bracex.expand(r'file${a,b,c}.jpg')
['file${a,b,c}.jpg']
```

## Install

```console
> pip install bracex
```

## API


### expand

```python
def expand(string, keep_escapes=False):
```

`expand` accepts a string and returns a list of expanded strings. It will always return at least a single empty string `[""]`. By default, escapes will be resolved and the backslashes reduced accordingly, but `keep_escapes` will process the escapes without stripping them out.

### iexpand

```python
def iexpand(string, keep_escapes=False):
```

`iexpand` is just like `expand` except it returns a generator.

## License

MIT License

Copyright (c) 2018 Isaac Muse

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
[pypi-image]: https://img.shields.io/pypi/v/bracex.svg
[pypi-link]: https://pypi.python.org/pypi/bracex
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg
