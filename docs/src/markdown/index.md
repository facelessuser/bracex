# Bracex

## Overview

Bracex is a brace expanding library (à la Bash) for Python. Brace expanding is used to generate arbitrary strings.


```shell-session
$ echo {{a,b},c}d
ad bd cd
```

Bracex adds this ability to Python:

```pycon3
>>> bracex.expand(r'file-{1,2,3}.txt')
['file-1.txt', 'file-2.txt', 'file-3.txt']
```

```pycon3
>>> bracex.expand(r'file-{1,2,3}.txt')
['file-1.txt', 'file-2.txt', 'file-3.txt']
```

```pycon3
>>> bracex.expand(r'-v{,,}')
['-v', '-v', '-v']
```

Nested braces:

```pycon3
>>> bracex.expand(r'file-{{a,b},c}d.txt')
['file-ad.txt', 'file-bd.txt', 'file-cd.txt']
```

Numerical sequences:

```pycon3
>>> bracex.expand(r'file{0..3}.txt')
['file0.txt', 'file1.txt', 'file2.txt', 'file3.txt']
```

```pycon3
>>> bracex.expand(r'file{0..6..2}.txt')
['file0.txt', 'file2.txt', 'file4.txt', 'file6.txt']
```

```pycon3
>>> bracex.expand(r'file{00..10..5}.jpg')
['file00.jpg', 'file05.jpg', 'file10.jpg']
```

Alphabetic sequences:

```pycon3
>>> bracex.expand(r'file{A..D}.txt')
['fileA.txt', 'fileB.txt', 'fileC.txt', 'fileD.txt']
```

```pycon3
>>> bracex.expand(r'file{A..G..2}.txt')
['fileA.txt', 'fileC.txt', 'fileE.txt', 'fileG.txt']
```

Allows escaping:

```pycon3
>>> bracex.expand(r'file\{00..10..5}.jpg')
['file{00..10..5}.jpg']
```

```pycon3
>>> bracex.expand(r'file\{00..10..5}.jpg', keep_escapes=True)
['file\\{00..10..5}.jpg']
```

Bracex will **not** expand braces in the form of `${...}`:

```pycon3
>>> bracex.expand(r'file${a,b,c}.jpg')
['file${a,b,c}.jpg']
```

## Install

```shell-session
$ pip install bracex
```

## API

### `expand()`

```py3
def expand(string, keep_escapes=False):
```

`expand` accepts a string and returns a list of expanded strings. It will always return at least a single empty string `[""]`. By default, escapes will be resolved and the backslashes reduced accordingly, but `keep_escapes` will process the escapes without stripping them out.

### `iexpand()`

```py3
def iexpand(string, keep_escapes=False):
```

`iexpand` is just like `expand` except it returns a generator.
