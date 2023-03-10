import pytest

import salt.modules.macpackage as macpackage
from tests.support.mock import MagicMock, call, patch


@pytest.fixture
def configure_loader_modules():
    return {macpackage: {}}


def test_install():
    """
    Test installing a PKG file
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run_all": mock}):
        macpackage.install("/path/to/file.pkg")
        mock.assert_called_once_with(
            "installer -pkg /path/to/file.pkg -target LocalSystem",
            python_shell=False,
        )


def test_install_wildcard():
    """
    Test installing a PKG file with a wildcard
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run_all": mock}):
        macpackage.install("/path/to/*.pkg")
        mock.assert_called_once_with(
            "installer -pkg /path/to/*.pkg -target LocalSystem", python_shell=True
        )


def test_install_with_extras():
    """
    Test installing a PKG file with extra options
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run_all": mock}):
        macpackage.install("/path/to/file.pkg", store=True, allow_untrusted=True)
        mock.assert_called_once_with(
            "installer -pkg /path/to/file.pkg -target LocalSystem -store"
            " -allowUntrusted",
            python_shell=False,
        )


def test_install_app():
    """
    Test installing an APP package
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        macpackage.install_app("/path/to/file.app")
        mock.assert_called_once_with(
            'rsync -a --delete "/path/to/file.app/" "/Applications/file.app"'
        )


def test_install_app_specify_target():
    """
    Test installing an APP package with a specific target
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        macpackage.install_app("/path/to/file.app", "/Applications/new.app")
        mock.assert_called_once_with(
            'rsync -a --delete "/path/to/file.app/" "/Applications/new.app"'
        )


def test_install_app_with_slash():
    """
    Test installing an APP package with a specific target
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        macpackage.install_app("/path/to/file.app/")
        mock.assert_called_once_with(
            'rsync -a --delete "/path/to/file.app/" "/Applications/file.app"'
        )


def test_uninstall():
    """
    Test Uninstalling an APP package with a specific target
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"file.remove": mock}):
        macpackage.uninstall_app("/path/to/file.app")
        mock.assert_called_once_with("/path/to/file.app")


def test_mount():
    """
    Test mounting an dmg file to a temporary location
    """
    cmd_mock = MagicMock()
    temp_mock = MagicMock(return_value="dmg-ABCDEF")
    with patch.dict(macpackage.__salt__, {"cmd.run": cmd_mock, "temp.dir": temp_mock}):
        macpackage.mount("/path/to/file.dmg")
        temp_mock.assert_called_once_with(prefix="dmg-")
        cmd_mock.assert_called_once_with(
            "hdiutil attach -readonly -nobrowse -mountpoint "
            'dmg-ABCDEF "/path/to/file.dmg"'
        )


def test_unmount():
    """
    Test Unmounting an dmg file to a temporary location
    """
    mock = MagicMock()
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        macpackage.unmount("/path/to/file.dmg")
        mock.assert_called_once_with('hdiutil detach "/path/to/file.dmg"')


def test_installed_pkgs():
    """
    Test getting a list of the installed packages
    """
    expected = ["com.apple.this", "com.salt.that"]
    mock = MagicMock(return_value="com.apple.this\ncom.salt.that")
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        out = macpackage.installed_pkgs()
        mock.assert_called_once_with("pkgutil --pkgs")
        assert out == expected


def test_get_pkg_id_with_files():
    """
    Test getting a the id for a package
    """
    with patch(
        "salt.modules.macpackage._get_pkg_id_from_pkginfo"
    ) as pkg_id_pkginfo_mock:
        expected = ["com.apple.this"]
        cmd_mock = MagicMock(
            side_effect=[
                "/path/to/PackageInfo\n/path/to/some/other/fake/PackageInfo",
                "",
                "",
            ]
        )
        pkg_id_pkginfo_mock.side_effect = [["com.apple.this"], []]
        temp_mock = MagicMock(return_value="/tmp/dmg-ABCDEF")
        remove_mock = MagicMock()

        with patch.dict(
            macpackage.__salt__,
            {
                "cmd.run": cmd_mock,
                "temp.dir": temp_mock,
                "file.remove": remove_mock,
            },
        ):
            out = macpackage.get_pkg_id("/path/to/file.pkg")

            temp_mock.assert_called_once_with(prefix="pkg-")
            cmd_calls = [
                call(
                    "xar -t -f /path/to/file.pkg | grep PackageInfo",
                    python_shell=True,
                    output_loglevel="quiet",
                ),
                call(
                    "xar -x -f /path/to/file.pkg /path/to/PackageInfo"
                    " /path/to/some/other/fake/PackageInfo",
                    cwd="/tmp/dmg-ABCDEF",
                    output_loglevel="quiet",
                ),
            ]
            cmd_mock.assert_has_calls(cmd_calls)

            pkg_id_pkginfo_calls = [
                call("/path/to/PackageInfo"),
                call("/path/to/some/other/fake/PackageInfo"),
            ]
            pkg_id_pkginfo_mock.assert_has_calls(pkg_id_pkginfo_calls)
            remove_mock.assert_called_once_with("/tmp/dmg-ABCDEF")

            assert out == expected


def test_get_pkg_id_with_dir():
    """
    Test getting a the id for a package with a directory
    """
    with patch("salt.modules.macpackage._get_pkg_id_dir") as pkg_id_dir_mock:
        expected = ["com.apple.this"]
        pkg_id_dir_mock.return_value = ["com.apple.this"]
        cmd_mock = MagicMock(return_value="Error opening /path/to/file.pkg")
        temp_mock = MagicMock(return_value="/tmp/dmg-ABCDEF")
        remove_mock = MagicMock()

        with patch.dict(
            macpackage.__salt__,
            {
                "cmd.run": cmd_mock,
                "temp.dir": temp_mock,
                "file.remove": remove_mock,
            },
        ):
            out = macpackage.get_pkg_id("/path/to/file.pkg")

            temp_mock.assert_called_once_with(prefix="pkg-")
            cmd_mock.assert_called_once_with(
                "xar -t -f /path/to/file.pkg | grep PackageInfo",
                python_shell=True,
                output_loglevel="quiet",
            )
            pkg_id_dir_mock.assert_called_once_with("/path/to/file.pkg")
            remove_mock.assert_called_once_with("/tmp/dmg-ABCDEF")

            assert out == expected


def test_get_mpkg_ids():
    """
    Test getting the ids of a mpkg file
    """
    with patch("salt.modules.macpackage.get_pkg_id") as get_pkg_id_mock:
        expected = ["com.apple.this", "com.salt.other"]
        mock = MagicMock(return_value="/tmp/dmg-X/file.pkg\n/tmp/dmg-X/other.pkg")
        get_pkg_id_mock.side_effect = [["com.apple.this"], ["com.salt.other"]]

        with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
            out = macpackage.get_mpkg_ids("/path/to/file.mpkg")

            mock.assert_called_once_with("find /path/to -name *.pkg", python_shell=True)

            calls = [call("/tmp/dmg-X/file.pkg"), call("/tmp/dmg-X/other.pkg")]
            get_pkg_id_mock.assert_has_calls(calls)

            assert out == expected


def test_get_pkg_id_from_pkginfo():
    """
    Test getting a package id from pkginfo files
    """
    expected = ["com.apple.this", "com.apple.that"]
    mock = MagicMock(return_value="com.apple.this\ncom.apple.that")
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        out = macpackage._get_pkg_id_from_pkginfo("/tmp/dmg-X/PackageInfo")
        cmd = (
            "cat /tmp/dmg-X/PackageInfo | grep -Eo"
            " 'identifier=\"[a-zA-Z.0-9\\-]*\"' | cut -c 13- | tr -d '\"'"
        )
        mock.assert_called_once_with(cmd, python_shell=True)
        assert out == expected


def test_get_pkg_id_from_pkginfo_no_file():
    """
    Test getting a package id from pkginfo file when it doesn't exist
    """
    expected = []
    mock = MagicMock(return_value="No such file")
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        out = macpackage._get_pkg_id_from_pkginfo("/tmp/dmg-X/PackageInfo")
        cmd = (
            "cat /tmp/dmg-X/PackageInfo | grep -Eo"
            " 'identifier=\"[a-zA-Z.0-9\\-]*\"' | cut -c 13- | tr -d '\"'"
        )
        mock.assert_called_once_with(cmd, python_shell=True)
        assert out == expected


def test_get_pkg_id_dir():
    """
    Test getting a package id from a directory
    """
    expected = ["com.apple.this"]
    mock = MagicMock(return_value="com.apple.this")
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        out = macpackage._get_pkg_id_dir("/tmp/dmg-X/")
        cmd = (
            '/usr/libexec/PlistBuddy -c "print :CFBundleIdentifier"'
            " /tmp/dmg-X/Contents/Info.plist"
        )
        mock.assert_called_once_with(cmd, python_shell=False)
        assert out == expected


def test_get_pkg_id_dir_wildcard():
    """
    Test getting a package id from a directory with a wildcard
    """
    expected = ["com.apple.this"]
    mock = MagicMock(return_value="com.apple.this")
    with patch.dict(macpackage.__salt__, {"cmd.run": mock}):
        out = macpackage._get_pkg_id_dir("/tmp/dmg-X/*.pkg/")
        cmd = (
            '/usr/libexec/PlistBuddy -c "print :CFBundleIdentifier"'
            " '/tmp/dmg-X/*.pkg/Contents/Info.plist'"
        )
        mock.assert_called_once_with(cmd, python_shell=True)
        assert out == expected
