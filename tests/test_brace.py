"""
Test braces.

Looking for brace test cases, I stumbled on https://github.com/juliangruber/brace-expansion.
The project contained great tests that mirror Bash 4.3's behavior.  And while this library
was written independently, we used their test sweet to bring this up to Bash 4.3 standard.
"""
import unittest
import pytest
import bracex
import ast
import re

RE_REMOVE = re.compile(r'^\[|\]$')
BRE_REMOVE = re.compile(br'^\[|\]$')


def get_bash_cases():
    """Setup module."""

    re_split = re.compile(r'><><><><')

    with open('tests/brace-results.txt', 'r') as r:
        # Split by test cases
        results = re_split.split(r.read())
        results.pop()
        # Split by line within test case
        wanted = [x.split('\n') for x in results]

    with open('tests/brace-cases.txt', 'r') as r:
        # Split by line ignoring commented lines.
        # We may have blank lines that get included,
        # But the test will compare those too, so it
        # isn't a problem.
        cases = [x.strip() for x in r.read().split('\n') if not x.startswith('#')]
        cases.pop()

    bash_cases = []
    while cases:
        bash_cases.append((cases.pop(0), wanted.pop(0)))
    return bash_cases


class TestBraces:
    """Test globbing."""

    dollar_cases = [
        ['${1..3}', ['${1..3}']],
        ['${a,b}${c,d}', ['${a,b}${c,d}']],
        ['x${a,b}x${c,d}x', ['x${a,b}x${c,d}x']]
    ]

    empty_cases = [
        ['-v{,,,,}', ['-v', '-v', '-v', '-v', '-v']],
        ['{,,}', ['']],
        ['', ['']]
    ]

    negative_incr_cases = [
        ['{3..1}', ['3', '2', '1']],
        ['{10..8}', ['10', '9', '8']],
        ['{10..08}', ['10', '09', '08']],
        ['{c..a}', ['c', 'b', 'a']],
        ['{4..0..2}', ['4', '2', '0']],
        ['{4..0..-2}', ['4', '2', '0']],
        ['{e..a..2}', ['e', 'c', 'a']]
    ]

    nested_cases = [
        ['{a,b{1..3},c}', ['a', 'b1', 'b2', 'b3', 'c']],
        ['{{A..Z},{a..z}}', list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')],
        ['ppp{,config,oe{,conf}}', ['ppp', 'pppconfig', 'pppoe', 'pppoeconf']]
    ]

    order_cases = [
        ['a{d,c,b}e', ['ade', 'ace', 'abe']]
    ]

    pad_cases = [
        ['{09..11}', ['09', '10', '11']],
        ['{9..11}', ['9', '10', '11']]
    ]

    sequence_cases = [
        ['a{1..2}b{2..3}c', ['a1b2c', 'a1b3c', 'a2b2c', 'a2b3c']],
        ['{1..2}{2..3}', ['12', '13', '22', '23']],
        ['{0..8..2}', ['0', '2', '4', '6', '8']],
        ['{1..8..2}', ['1', '3', '5', '7']],
        ['{3..-2}', ['3', '2', '1', '0', '-1', '-2']],
        ['1{a..b}2{b..c}3', ['1a2b3', '1a2c3', '1b2b3', '1b2c3']],
        ['{a..b}{b..c}', ['ab', 'ac', 'bb', 'bc']],
        ['{a..k..2}', ['a', 'c', 'e', 'g', 'i', 'k']],
        ['{b..k..2}', ['b', 'd', 'f', 'h', 'j']]
    ]

    error_cases = [
        # This would fail in bash, but we won't fail because we aren't Bash
        ['{a,b,c}\\', ['a', 'b', 'c']]
    ]

    @staticmethod
    def eval_str_esc(string):
        r"""Evaluate buffer as a string buffer counting things like \\ as \."""

        return ast.literal_eval('"%s"' % string.strip().replace('"', '\\"'))

    @staticmethod
    def assert_equal(a, b):
        """Assert equal."""

        assert a == b, "Comparison between objects yielded False."

    @classmethod
    def eval_brace_cases(cls, case):
        """Evaluate the brace cases."""

        print("PATTERN: ", case[0])
        expanded_pattern = []
        try:
            expanded_pattern.extend(
                list(bracex.iexpand(case[0]))
            )
        except Exception:
            expanded_pattern.append(case[0])
        result = expanded_pattern
        goal = case[1]
        print('TEST: ', result, '<=^=>', goal, '\n')
        cls.assert_equal(result, goal)

    @pytest.mark.parametrize("case", error_cases)
    def test_internal_errors(self, case):
        """Test trailing escape."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", dollar_cases)
    def test_dollar_expand(self, case):
        """Test that dollar expansions don't expand."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", empty_cases)
    def test_empty_expand(self, case):
        """Test empty expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", negative_incr_cases)
    def test_negative_incr_expand(self, case):
        """Test negative increment expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", nested_cases)
    def test_nested_expand(self, case):
        """Test nested expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", order_cases)
    def test_order_expand(self, case):
        """Test ordered expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", pad_cases)
    def test_pad_expand(self, case):
        """Test padded expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", sequence_cases)
    def test_sequence_expand(self, case):
        """Test sequence expansion."""

        self.eval_brace_cases(case)

    @pytest.mark.parametrize("case", get_bash_cases())
    def test_bash_cases(self, case):
        """Test bash cases."""

        test_case = self.eval_str_esc(case[0])
        entry = case[1]

        print('TEST: ', test_case)
        self.assert_equal(test_case, entry[0])
        expansions = bracex.expand(test_case)
        if not (len(expansions) == 1 and not expansions[0]):
            index = 1
            for a in expansions:
                b = RE_REMOVE.sub('', entry[index])
                print('    ', a, '<==>', b)
                self.assert_equal(a, b)
                index += 1

        # Bytes
        test_case = test_case.encode('utf-8')
        self.assert_equal(test_case, entry[0].encode('utf-8'))
        expansions = bracex.expand(test_case)
        if not (len(expansions) == 1 and not expansions[0]):
            index = 1
            for a in expansions:
                b = BRE_REMOVE.sub(b'', entry[index].encode('utf-8'))
                print('    ', a, '<==>', b)
                self.assert_equal(a, b)
                index += 1


class TestExpansionLimit(unittest.TestCase):
    """Test brace expansion limit."""

    def test_expansion_limit_expand(self):
        """Test expansion limit."""

        self.assertEqual(len(bracex.expand('text{1,2}text{{3,4,{5,6}text{7,8}},{9}}', limit=14)), 14)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('text{1,2}text{{3,4,{5,6}text{7,8}},{9}}', limit=13)

    def test_expansion_no_limit_expand(self):
        """Test expansion no limit."""

        self.assertEqual(len(bracex.expand('text{1,2}text{{3,4,{5,6}text{7,8}},{9}}', limit=0)), 14)

    def test_expansion_char_limt_expand(self):
        """Test expansion character limit with `expand`."""

        self.assertEqual(len(bracex.expand('{a..k}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k}', limit=10)

    def test_expansion_char_reverse_limt_expand(self):
        """Test expansion character reversed limit with `expand`."""

        self.assertEqual(len(bracex.expand('{k..a}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a}', limit=10)

    def test_expansion_char_limt_expand_step2(self):
        """Test expansion character limit with `expand` step 2."""

        self.assertEqual(len(bracex.expand('{a..k..2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..2}', limit=5)

    def test_expansion_char_limt_expand_step3(self):
        """Test expansion character limit with `expand` step 3."""

        self.assertEqual(len(bracex.expand('{a..k..3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..3}', limit=3)

    def test_expansion_char_limt_expand_step5(self):
        """Test expansion character limit with `expand` step 5."""

        self.assertEqual(len(bracex.expand('{a..k..5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..5}', limit=2)

    def test_expansion_char_reverse_limt_expand_step2(self):
        """Test expansion character reversed limit with `expand` step 2."""

        self.assertEqual(len(bracex.expand('{k..a..2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..2}', limit=5)

    def test_expansion_char_reverse_limt_expand_step3(self):
        """Test expansion character reversed limit with `expand` step 3."""

        self.assertEqual(len(bracex.expand('{k..a..3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..3}', limit=3)

    def test_expansion_char_reverse_limt_expand_step5(self):
        """Test expansion character reversed limit with `expand` step 5."""

        self.assertEqual(len(bracex.expand('{k..a..5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..5}', limit=2)

    def test_expansion_char_limt_expand_step2_neg(self):
        """Test expansion character limit with `expand` step -2."""

        self.assertEqual(len(bracex.expand('{a..k..-2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..-2}', limit=5)

    def test_expansion_char_limt_expand_step3_neg(self):
        """Test expansion character limit with `expand` step -3."""

        self.assertEqual(len(bracex.expand('{a..k..-3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..-3}', limit=3)

    def test_expansion_char_limt_expand_step5_neg(self):
        """Test expansion character limit with `expand` step -5."""

        self.assertEqual(len(bracex.expand('{a..k..-5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{a..k..-5}', limit=2)

    def test_expansion_char_reverse_limt_expand_step2_neg(self):
        """Test expansion character reversed limit with `expand` step -2."""

        self.assertEqual(len(bracex.expand('{k..a..-2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..-2}', limit=5)

    def test_expansion_char_reverse_limt_expand_step3_neg(self):
        """Test expansion character reversed limit with `expand` step -3."""

        self.assertEqual(len(bracex.expand('{k..a..-3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..-3}', limit=3)

    def test_expansion_char_reverse_limt_expand_step5_neg(self):
        """Test expansion character reversed limit with `expand` step -5."""

        self.assertEqual(len(bracex.expand('{k..a..-5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{k..a..-5}', limit=2)

    def test_expansion_num_limt_expand(self):
        """Test expansion numeric limit with `expand`."""

        self.assertEqual(len(bracex.expand('{1..11}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{1..11}', limit=10)

    def test_expansion_num_reverse_limt_expand(self):
        """Test expansion numeric reversed limit with `expand`."""

        self.assertEqual(len(bracex.expand('{11..1}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{11..1}', limit=10)

    def test_expansion_num_negative_limt_expand(self):
        """Test expansion numeric negative limit with `expand`."""

        self.assertEqual(len(bracex.expand('{-1..-11}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-1..-11}', limit=10)

    def test_expansion_num_negative_reversed_limt_expand(self):
        """Test expansion numeric negative reversed limit with `expand`."""

        self.assertEqual(len(bracex.expand('{-11..-1}', limit=11)), 11)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-11..-1}', limit=10)

    def test_expansion_num_limt_expand_step(self):
        """Test expansion numeric limit with `expand` step."""

        self.assertEqual(len(bracex.expand('{1..11..5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{1..11..5}', limit=2)

    def test_expansion_num_reverse_limt_expand_step(self):
        """Test expansion numeric reversed limit with `expand` step."""

        self.assertEqual(len(bracex.expand('{11..1..3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{11..1..3}', limit=3)

    def test_expansion_num_negative_limt_expand_step(self):
        """Test expansion numeric negative limit with `expand`."""

        self.assertEqual(len(bracex.expand('{-1..-11..2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-1..-11..2}', limit=5)

    def test_expansion_num_negative_reversed_limt_expand_step(self):
        """Test expansion numeric negative reversed limit with `expand`."""

        self.assertEqual(len(bracex.expand('{-11..-1..7}', limit=2)), 2)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-11..-1..7}', limit=1)

    def test_expansion_num_limt_expand_neg_step(self):
        """Test expansion numeric limit with `expand` negative step."""

        self.assertEqual(len(bracex.expand('{1..11..-5}', limit=3)), 3)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{1..11..-5}', limit=2)

    def test_expansion_num_reverse_limt_expand_neg_step(self):
        """Test expansion numeric reversed limit with `expand` negative step."""

        self.assertEqual(len(bracex.expand('{11..1..-3}', limit=4)), 4)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{11..1..-3}', limit=3)

    def test_expansion_num_negative_limt_expand_neg_step(self):
        """Test expansion numeric negative limit with `expand` negative step."""

        self.assertEqual(len(bracex.expand('{-1..-11..-2}', limit=6)), 6)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-1..-11..-2}', limit=5)

    def test_expansion_num_negative_reversed_limt_expand_neg_step(self):
        """Test expansion numeric negative reversed limit with `expand` negative step."""

        self.assertEqual(len(bracex.expand('{-11..-11..-7}', limit=1)), 1)
        with self.assertRaises(bracex.ExpansionLimitException):
            bracex.expand('{-11..-1..-7}', limit=1)
