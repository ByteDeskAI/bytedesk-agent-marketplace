import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import pytest
import yaml
from canonical import RestrictedYAMLError, canonical_digest, load_restricted_yaml


def test_key_order_does_not_change_digest():
    a = load_restricted_yaml("b: 2\na: 1\n")
    b = load_restricted_yaml("a: 1\nb: 2\n")
    assert canonical_digest(a) == canonical_digest(b)


def test_changing_a_value_changes_the_digest():
    a = load_restricted_yaml("a: 1\n")
    b = load_restricted_yaml("a: 2\n")
    assert canonical_digest(a) != canonical_digest(b)


def test_duplicate_keys_are_rejected():
    with pytest.raises(RestrictedYAMLError):
        load_restricted_yaml("a: 1\na: 2\n")


def test_aliases_are_rejected():
    with pytest.raises(RestrictedYAMLError):
        load_restricted_yaml("a: &anchor 1\nb: *anchor\n")


def test_non_string_keys_are_rejected():
    with pytest.raises(RestrictedYAMLError):
        load_restricted_yaml("1: a\n")


def test_non_finite_numbers_are_rejected():
    with pytest.raises(RestrictedYAMLError):
        load_restricted_yaml("a: .inf\n")
    with pytest.raises(RestrictedYAMLError):
        load_restricted_yaml("a: .nan\n")


def test_custom_tags_are_rejected():
    with pytest.raises(yaml.constructor.ConstructorError):
        load_restricted_yaml("a: !!python/object:builtins.object {}\n")
