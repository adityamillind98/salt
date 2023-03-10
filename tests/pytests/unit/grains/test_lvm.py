"""
    :codeauthor: :email:`Shane Lee <slee@saltstack.com>`
"""

import pytest

import salt.grains.lvm as lvm
from tests.support.mock import MagicMock, patch


@pytest.fixture
def configure_loader_modules():
    return {
        lvm: {"__salt__": {}},
    }


def test__linux_lvm():
    """
    Test grains._linux_lvm, normal return
    Should return a populated dictionary
    """

    vgs_out = {"pid": 123, "retcode": 0, "stdout": "  vg00\n  vg01", "stderr": ""}
    lvs_out_vg00 = {
        "pid": 456,
        "retcode": 0,
        "stdout": "  root\n  swap\n  tmp \n  usr \n  var",
        "stderr": "",
    }
    lvs_out_vg01 = {"pid": 789, "retcode": 0, "stdout": "  opt", "stderr": ""}
    cmd_out = MagicMock(
        autospec=True, side_effect=[vgs_out, lvs_out_vg00, lvs_out_vg01]
    )

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lvm"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret == {
        "lvm": {"vg00": ["root", "swap", "tmp", "usr", "var"], "vg01": ["opt"]}
    }, ret


def test__linux_lvm_with_WARNINGs():
    """
    Test grains._linux_lvm, with WARNINGs in lvm command output
    Should return a populated dictionary
    """

    vgs_out = {
        "pid": 123,
        "retcode": 0,
        "stdout": "  vg00\n  vg01",
        "stderr": "WARNING: Something wrong is not right",
    }
    lvs_out_vg00 = {
        "pid": 456,
        "retcode": 0,
        "stdout": "  root\n  swap\n  tmp \n  usr \n  var",
        "stderr": "WARNING: Something wrong is not right",
    }
    lvs_out_vg01 = {
        "pid": 789,
        "retcode": 0,
        "stdout": "  opt",
        "stderr": "WARNING: Something wrong is not right",
    }
    cmd_out = MagicMock(
        autospec=True, side_effect=[vgs_out, lvs_out_vg00, lvs_out_vg01]
    )

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lvm"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret == {
        "lvm": {"vg00": ["root", "swap", "tmp", "usr", "var"], "vg01": ["opt"]}
    }, ret


def test__linux_lvm_with_non_zero_exit_codes():
    """
    Test grains._linux_lvm, with non-zero exit codes for lvm command
    Should return a populated dictionary
    """

    vgs_out = {
        "pid": 123,
        "retcode": 5,
        "stdout": "  vg00\n  vg01",
        "stderr": "  Skipping clustered volume vgcluster\n  Skipping volume group vgcluster",
    }
    lvs_out_vg00 = {
        "pid": 456,
        "retcode": 0,
        "stdout": "  root\n  swap\n  tmp \n  usr \n  var",
        "stderr": "",
    }
    lvs_out_vg01 = {"pid": 789, "retcode": 0, "stdout": "  opt", "stderr": ""}
    cmd_out = MagicMock(
        autospec=True, side_effect=[vgs_out, lvs_out_vg00, lvs_out_vg01]
    )

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lvm"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret == {
        "lvm": {"vg00": ["root", "swap", "tmp", "usr", "var"], "vg01": ["opt"]}
    }, ret


def test__linux_lvm_no_lvm():
    """
    Test grains._linux_lvm, no lvm installed
    Should return nothing
    """

    vgs_out = {"pid": 123, "retcode": 0, "stdout": "  vg00\n  vg01", "stderr": ""}
    lvs_out_vg00 = {
        "pid": 456,
        "retcode": 0,
        "stdout": "  root\n  swap\n  tmp \n  usr \n  var",
        "stderr": "",
    }
    lvs_out_vg01 = {"pid": 789, "retcode": 0, "stdout": "  opt", "stderr": ""}
    cmd_out = MagicMock(
        autospec=True, side_effect=[vgs_out, lvs_out_vg00, lvs_out_vg01]
    )

    patch_which = patch("salt.utils.path.which", autospec=True, return_value="")
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret is None, ret


def test__linux_lvm_no_volume_groups():
    """
    Test grains._linux_lvm, lvm is installed but no volume groups created.
    Should return a dictionary only with the header
    """

    vgs_out = {"pid": 123, "retcode": 0, "stdout": "", "stderr": ""}
    cmd_out = MagicMock(autospec=True, side_effect=[vgs_out])

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lvm"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret == {"lvm": {}}, ret


def test__linux_lvm_no_logical_volumes():
    """
    Test grains._linux_lvm, lvm is installed, volume groups created but
    no logical volumes present.
    Should return a dictionary only with the header
    """

    vgs_out = {"pid": 123, "retcode": 0, "stdout": "  vg00\n  vg01", "stderr": ""}
    lvs_out = {"pid": 456, "retcode": 0, "stdout": "", "stderr": ""}
    cmd_out = MagicMock(autospec=True, side_effect=[vgs_out, lvs_out, lvs_out])

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lvm"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run_all": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._linux_lvm()

    assert ret == {"lvm": {"vg00": [], "vg01": []}}, ret


def test__aix_lvm():
    """
    Test grains._aix_lvm, normal return
    Should return a populated dictionary
    """

    lsvg_out = "rootvg\nothervg"
    lsvg_out_rootvg = (
        "rootvg:\nLV NAME             TYPE       LPs     PPs     PVs  LV STATE     "
        " MOUNT POINT\nhd5                 boot       1       1       1   "
        " closed/syncd  N/A\nhd6                 paging     32      32      1   "
        " open/syncd    N/A\nhd8                 jfs2log    1       1       1   "
        " open/syncd    N/A\nhd4                 jfs2       32      32      1   "
        " open/syncd    /\nhd2                 jfs2       16      16      1   "
        " open/syncd    /usr\nhd9var              jfs2       32      32      1   "
        " open/syncd    /var\nhd3                 jfs2       32      32      1   "
        " open/syncd    /tmp\nhd1                 jfs2       16      16      1   "
        " open/syncd    /home\nhd10opt             jfs2       16      16      1   "
        " open/syncd    /opt"
    )
    lsvg_out_othervg = (
        "othervg:\nLV NAME             TYPE       LPs     PPs     PVs  LV STATE    "
        "  MOUNT POINT\nloglv01             jfs2log    1       1       1   "
        " open/syncd    N/A\ndatalv              jfs2       16      16      1   "
        " open/syncd    /data"
    )
    cmd_out = MagicMock(
        autospec=True, side_effect=[lsvg_out, lsvg_out_rootvg, lsvg_out_othervg]
    )

    patch_which = patch(
        "salt.utils.path.which", autospec=True, return_value="/usr/sbin/lsvg"
    )
    patch_cmd_lvm = patch.dict(lvm.__salt__, {"cmd.run": cmd_out})
    with patch_which, patch_cmd_lvm:
        ret = lvm._aix_lvm()

    assert ret == {
        "lvm": {
            "rootvg": [
                "hd5",
                "hd6",
                "hd8",
                "hd4",
                "hd2",
                "hd9var",
                "hd3",
                "hd1",
                "hd10opt",
            ],
            "othervg": ["loglv01", "datalv"],
        }
    }, ret
