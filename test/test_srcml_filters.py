import pytest
from srcML.srcml_filters import SrcmlFilters, KeyValueNode

@pytest.mark.parametrize("xml, result_len, result", [("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
                                               ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children(xml, result_len, result):
    s=SrcmlFilters(xml, True)
    children=(s.get_list_of_children(s.tree))
    if len(children) != result_len:
        assert False
        return
    first_child=children[0]

    res=KeyValueNode(result[0], result[1])

    aa=("|{}|{}|".format(res.key, first_child.key))
    bb=("|{}|{}|".format(res.value, first_child.value))

    if res.key==first_child.key and res.value == first_child.value:
        assert True
        return
    assert False

@pytest.mark.parametrize("xml, result_len, result", [("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
                                               ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children_with_text(xml, result_len, result):
    s=SrcmlFilters(xml, True)
    children=(s.get_list_of_children_with_text(s.xml_code))
    if len(children) != result_len:
        assert False
        return
    first_child=children[0]

    res=KeyValueNode(result[0], result[1])

    aa=("|{}|{}|".format(res.key, first_child.key))
    bb=("|{}|{}|".format(res.value, first_child.value))

    if res.key==first_child.key and res.value == first_child.value:
        assert True
        return
    assert False


@pytest.mark.parametrize("xml, result_len, result", [("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
                                               ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children_with_text_from_tree(xml, result_len, result):
    s=SrcmlFilters(xml, True)
    children=(s.get_list_of_children_with_text_from_tree(s.tree))
    if len(children) != result_len:
        assert False
        return
    first_child=children[0]

    res=KeyValueNode(result[0], result[1])

    aa=("|{}|{}|".format(res.key, first_child.key))
    bb=("|{}|{}|".format(res.value, first_child.value))

    if res.key==first_child.key and res.value == first_child.value:
        assert True
        return
    assert False

def test_add_children_to_node():
    assert False


def test_add_children_to_node_with_text():
    assert False


def test_print_tree():
    assert False


def test_check_condition():
    assert False


def test_contain_operator_name():
    assert False


def test_contain_name():
    assert False


def test_contain_operator_name_literal():
    assert False


def test_contain_operator_name_name():
    assert False


def test_contain_equal():
    assert False


def test_apply_all_filters():
    assert False
