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

and as a command:

```shell-session
$ python3 -m bracex -0 "base/{a,b}/{1..2}" | xargs -0 mkdir -p
$ tree base/
base/
├── a
│   ├── 1
│   └── 2
└── b
    ├── 1
    └── 2
```

-   **Why Bracex over other solutions?**

    Bracex actually follows pretty closely to how Bash processes braces. It is not a 1:1 implementation of how Bash
    handles braces, but generally, it follows very closely. Almost all of the test cases are run through Bash first,
    then our implementation is compared against the results Bash gives. There are a few cases where we have purposely
    deviated. For instance, we are not handling Bash's command line inputs, so we are not giving special meaning to back
    ticks and quotes at this time.

    On the command line Bracex can handle more expansions than Bash itself.

More Examples:

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
def expand(string, keep_escapes=False, limit=1000):
```

`expand` accepts a string and returns a list of expanded strings. It will always return at least a single empty string
`[""]`. By default, escapes will be resolved and the backslashes reduced accordingly, but `keep_escapes` will process
the escapes without stripping them out.

By default, brace expansion growth is limited to `1000`. This limit can be configured via the `limit` option. If you
would like to remove the limit option, you simply set `limit` to `0`.

### `iexpand()`

```py3
def iexpand(string, keep_escapes=False, limit=1000):
```

`iexpand` is just like `expand` except it returns a generator.

## Command line interface

```shell-session
$ python3 -m bracex --help
usage: python -mbracex [-h] [--terminator STR | -0] [--version] expression

Expands a bash-style brace expression, and outputs each expansion.

positional arguments:
  expression            Brace expression to expand

optional arguments:
  -h, --help            show this help message and exit
  --terminator STR, -t STR
                        Terminate each expansion with string STR (default: \n)
  -0                    Terminate each expansion with a NUL character
  --version             show program's version number and exit
```
