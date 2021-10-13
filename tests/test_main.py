"""Test command module and argument handling."""
import pytest
from bracex.__main__ import main
from bracex import __version__


def test_expand_with_default_terminator(capsys):
    """Test that by default one expansion is printed per line."""
    with pytest.raises(SystemExit) as exinfo:
        main(['{a..c}'])
    capture = capsys.readouterr()
    assert capture.out == "a\nb\nc\n"
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_expand_with_spaces(capsys):
    """Test that expansions can be space terminated."""
    with pytest.raises(SystemExit) as exinfo:
        main(['-t', ' ', '{a..c}'])
    capture = capsys.readouterr()
    assert capture.out == "a b c "
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_expand_with_empty_terminators(capsys):
    """Test that expansions can be terminated by an empty string."""
    with pytest.raises(SystemExit) as exinfo:
        main(['-t', '', '{a..c}'])
    capture = capsys.readouterr()
    assert capture.out == "abc"
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_expand_with_nul_terminators(capsys):
    """Test that expansions can be terminated by a NUL character."""
    with pytest.raises(SystemExit) as exinfo:
        main(['-0', '{a..c}'])
    capture = capsys.readouterr()
    assert capture.out == "a\x00b\x00c\x00"
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_terminator_arguments_are_mutually_exclusive(capsys):
    """Test that contradicting terminators raise an error."""
    with pytest.raises(SystemExit) as exinfo:
        main(['-0', '--terminator', ' ', '{a..c}'])

    capture = capsys.readouterr()
    assert capture.out == ""
    assert capture.err.find("error: argument --terminator/-t: not allowed with argument -0") > 0
    assert exinfo.value.code > 0


def test_help(capsys):
    """Test that help is available."""
    with pytest.raises(SystemExit) as exinfo:
        main(['--help'])
    capture = capsys.readouterr()
    assert capture.out.startswith("usage:")
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_version(capsys):
    """Test that the version is available."""
    with pytest.raises(SystemExit) as exinfo:
        main(['--version'])
    capture = capsys.readouterr()
    assert capture.out == f"{__version__}\n"
    assert capture.err == ""
    assert exinfo.value.code == 0


def test_no_args_is_considered_an_error(capsys):
    """Test that an error is reported when no expression is provided."""
    with pytest.raises(SystemExit) as exinfo:
        main([])
    capture = capsys.readouterr()
    assert capture.out == ""
    assert capture.err.endswith("error: the following arguments are required: expression\n")
    assert exinfo.value.code > 0


def test_excess_args_is_considered_an_error(capsys):
    """Test that an error is reported when too many arguments are provided."""
    with pytest.raises(SystemExit) as exinfo:
        main(['{a,b,c}', '{1..3}'])
    capture = capsys.readouterr()
    assert capture.out == ""
    assert capture.err.find("error: unrecognized arguments") > 0
    assert exinfo.value.code > 0
