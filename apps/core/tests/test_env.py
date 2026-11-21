import os
from unittest import mock

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.env import env, env_bool, env_int, env_list


class EnvironmentHelpersTests(SimpleTestCase):
    def test_env_returns_value_or_default(self) -> None:
        with mock.patch.dict(os.environ, {"SM_VALUE": "abc"}, clear=False):
            self.assertEqual(env("SM_VALUE", "default"), "abc")
        self.assertEqual(env("SM_MISSING", "default"), "default")
        self.assertEqual(env("SM_MISSING"), "")

    def test_env_raises_when_required_value_is_missing_or_blank(self) -> None:
        with self.assertRaises(ImproperlyConfigured):
            env("SM_MISSING", required=True)
        with (
            mock.patch.dict(os.environ, {"SM_BLANK": "  "}),
            self.assertRaises(ImproperlyConfigured),
        ):
            env("SM_BLANK", required=True)

    def test_env_bool_parses_common_values(self) -> None:
        for raw, expected in {"true": True, "1": True, "On": True, "no": False, "0": False}.items():
            with self.subTest(raw=raw), mock.patch.dict(os.environ, {"SM_FLAG": raw}):
                self.assertIs(env_bool("SM_FLAG"), expected)
        self.assertTrue(env_bool("SM_MISSING", True))

    def test_env_bool_rejects_invalid_values(self) -> None:
        with (
            mock.patch.dict(os.environ, {"SM_FLAG": "maybe"}),
            self.assertRaises(ImproperlyConfigured),
        ):
            env_bool("SM_FLAG")

    def test_env_int_parses_and_validates(self) -> None:
        with mock.patch.dict(os.environ, {"SM_INT": "42"}):
            self.assertEqual(env_int("SM_INT", 0), 42)
        with mock.patch.dict(os.environ, {"SM_INT": ""}):
            self.assertEqual(env_int("SM_INT", 7), 7)
        with mock.patch.dict(os.environ, {"SM_INT": "x"}), self.assertRaises(ImproperlyConfigured):
            env_int("SM_INT", 0)

    def test_env_list_splits_and_strips(self) -> None:
        with mock.patch.dict(os.environ, {"SM_LIST": " a, b ,,c "}):
            self.assertEqual(env_list("SM_LIST"), ["a", "b", "c"])
        self.assertEqual(env_list("SM_MISSING", "x,y"), ["x", "y"])
