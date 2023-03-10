import pytest

import salt.modules.baredoc as baredoc
from tests.support.paths import SALT_CODE_DIR


@pytest.fixture
def configure_loader_modules():
    return {
        baredoc: {
            "__opts__": {"extension_modules": SALT_CODE_DIR},
            "__grains__": {"saltpath": SALT_CODE_DIR},
        }
    }


def test_baredoc_list_states():
    """
    Test baredoc state module listing
    """
    ret = baredoc.list_states(names_only=True)
    assert "value_present" in ret["xml"][0]


def test_baredoc_list_states_args():
    """
    Test baredoc state listing with args
    """
    ret = baredoc.list_states()
    assert "value_present" in ret["xml"][0]
    assert "xpath" in ret["xml"][0]["value_present"]


def test_baredoc_list_states_single():
    """
    Test baredoc state listing single state module
    """
    ret = baredoc.list_states("xml")
    assert "value_present" in ret["xml"][0]
    assert "xpath" in ret["xml"][0]["value_present"]


def test_baredoc_list_modules():
    """
    test baredoc executiion module listing
    """
    ret = baredoc.list_modules(names_only=True)
    assert "get_value" in ret["xml"][0]


def test_baredoc_list_modules_args():
    """
    test baredoc execution module listing with args
    """
    ret = baredoc.list_modules()
    assert "get_value" in ret["xml"][0]
    assert "file" in ret["xml"][0]["get_value"]


def test_baredoc_list_modules_single_and_alias():
    """
    test baredoc single module listing
    """
    ret = baredoc.list_modules("mdata")
    assert "put" in ret["mdata"][2]
    assert "keyname" in ret["mdata"][2]["put"]


def test_baredoc_state_docs():
    ret = baredoc.state_docs()
    assert "XML Manager" in ret["xml"]
    assert "zabbix_usergroup" in ret


def test_baredoc_state_docs_single_arg():
    ret = baredoc.state_docs("xml")
    assert "XML Manager" in ret["xml"]
    ret = baredoc.state_docs("xml.value_present")
    assert "Manages a given XML file" in ret["xml.value_present"]


def test_baredoc_state_docs_multiple_args():
    ret = baredoc.state_docs("zabbix_hostgroup.present", "xml")
    assert "Ensures that the host group exists" in ret["zabbix_hostgroup.present"]
    assert "XML Manager" in ret["xml"]
    assert "Manages a given XML file" in ret["xml.value_present"]


def test_baredoc_module_docs():
    ret = baredoc.module_docs()
    assert "A module for testing" in ret["saltcheck"]


def test_baredoc_module_docs_single_arg():
    ret = baredoc.module_docs("saltcheck")
    assert "A module for testing" in ret["saltcheck"]


def test_baredoc_module_docs_multiple_args():
    ret = baredoc.module_docs("saltcheck", "xml.get_value")
    assert "A module for testing" in ret["saltcheck"]
    assert "Returns the value of the matched xpath element" in ret["xml.get_value"]
