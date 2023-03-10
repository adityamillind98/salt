import pytest

import salt.modules.macdefaults as macdefaults
from tests.support.mock import MagicMock, patch


@pytest.fixture
def configure_loader_modules():
    return {macdefaults: {}}


def test_write_default():
    """
    Test writing a default setting
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run_all": mock}):
        macdefaults.write("com.apple.CrashReporter", "DialogType", "Server")
        mock.assert_called_once_with(
            'defaults write "com.apple.CrashReporter" "DialogType" -string "Server"',
            runas=None,
        )


def test_write_with_user():
    """
    Test writing a default setting with a specific user
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run_all": mock}):
        macdefaults.write(
            "com.apple.CrashReporter", "DialogType", "Server", user="frank"
        )
        mock.assert_called_once_with(
            'defaults write "com.apple.CrashReporter" "DialogType" -string "Server"',
            runas="frank",
        )


def test_write_default_boolean():
    """
    Test writing a default setting
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run_all": mock}):
        macdefaults.write("com.apple.CrashReporter", "Crash", True, type="boolean")
        mock.assert_called_once_with(
            'defaults write "com.apple.CrashReporter" "Crash" -boolean "TRUE"',
            runas=None,
        )


def test_read_default():
    """
    Test reading a default setting
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run": mock}):
        macdefaults.read("com.apple.CrashReporter", "Crash")
        mock.assert_called_once_with(
            'defaults read "com.apple.CrashReporter" "Crash"', runas=None
        )


def test_read_default_with_user():
    """
    Test reading a default setting as a specific user
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run": mock}):
        macdefaults.read("com.apple.CrashReporter", "Crash", user="frank")
        mock.assert_called_once_with(
            'defaults read "com.apple.CrashReporter" "Crash"', runas="frank"
        )


def test_delete_default():
    """
    Test delete a default setting
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run_all": mock}):
        macdefaults.delete("com.apple.CrashReporter", "Crash")
        mock.assert_called_once_with(
            'defaults delete "com.apple.CrashReporter" "Crash"',
            output_loglevel="debug",
            runas=None,
        )


def test_delete_default_with_user():
    """
    Test delete a default setting as a specific user
    """
    mock = MagicMock()
    with patch.dict(macdefaults.__salt__, {"cmd.run_all": mock}):
        macdefaults.delete("com.apple.CrashReporter", "Crash", user="frank")
        mock.assert_called_once_with(
            'defaults delete "com.apple.CrashReporter" "Crash"',
            output_loglevel="debug",
            runas="frank",
        )
