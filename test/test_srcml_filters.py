import pytest
from srcML.srcml_filters import SrcmlFilters, KeyValueNode, Fields


@pytest.mark.parametrize("xml, result_len, result", [
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
    ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children(xml, result_len, result):
    s = SrcmlFilters(xml, True)
    children = (s.get_list_of_children(s.tree))
    if len(children) != result_len:
        assert False
        return
    first_child = children[0]

    res = KeyValueNode(result[0], result[1])

    aa = ("|{}|{}|".format(res.key, first_child.key))
    bb = ("|{}|{}|".format(res.value, first_child.value))

    if res.key == first_child.key and res.value == first_child.value:
        assert True
        return
    assert False


@pytest.mark.parametrize("xml, result_len, result", [
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
    ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children_with_text(xml, result_len, result):
    s = SrcmlFilters(xml, True)
    children = (s.get_list_of_children_with_text(s.xml_code))
    if len(children) != result_len:
        assert False
        return
    first_child = children[0]

    res = KeyValueNode(result[0], result[1])

    aa = ("|{}|{}|".format(res.key, first_child.key))
    bb = ("|{}|{}|".format(res.value, first_child.value))

    if res.key == first_child.key and res.value == first_child.value:
        assert True
        return
    assert False


@pytest.mark.parametrize("xml, result_len, result", [
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", 1, ("condition", "()")),
    ("<expr><operator>!</operator><name></name></expr>", 2, ("operator", "!"))])
def test_get_list_of_children_with_text_from_tree(xml, result_len, result):
    s = SrcmlFilters(xml, True)
    children = (s.get_list_of_children_with_text_from_tree(s.tree))
    if len(children) != result_len:
        assert False
        return
    first_child = children[0]

    res = KeyValueNode(result[0], result[1])

    aa = ("|{}|{}|".format(res.key, first_child.key))
    bb = ("|{}|{}|".format(res.value, first_child.value))

    if res.key == first_child.key and res.value == first_child.value:
        assert True
        return
    assert False


@pytest.mark.parametrize("xml, xml_to_add, result_len, result", [
    ("<if></if>", "<condition>(<expr><operator></operator><name></name></expr>)</condition>", 1, ("condition", "()")),
    ("<expr></expr>", "<operator>!</operator><name></name>", 2, ("operator", "!"))])
def test_add_children_to_node_with_text(xml, xml_to_add, result_len, result):
    s = SrcmlFilters(xml, True)
    s2 = SrcmlFilters("<father>{}</father>".format(xml_to_add), True)
    s.add_children_to_node_with_text(s.tree, s2.xml_code, Fields.SKIP.value)
    children = s.get_list_of_children_with_text_from_tree(s.tree)
    if len(children) != result_len:
        assert False
        return

    first_child = children[0]
    res = KeyValueNode(result[0], result[1])

    if res.key == first_child.key and res.value == first_child.value:
        assert True
        return
    assert False


@pytest.mark.parametrize("xml, xml_2, result", [
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>",
     "<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>",
     "<if><condition>(<expr><operator>=</operator><name>hello</name></expr>)</condition></if>", False),
    ("<if><condition>(<expr><operator>==</operator><name>hello</name></expr>)</condition></if>",
     "<if><condition>(<expr><operator></operator><name>hello</name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>",
     "<if><condition>(<expr><operator2></operator2><name>hello</name></expr>)</condition></if>", False)
])
def test_check_condition(xml, xml_2, result):
    s = SrcmlFilters(xml, True)
    xml_list = list()
    xml_list.append(xml_2)
    res = s.check_condition(xml_list)
    if res == result:
        assert True
        return

    assert False


@pytest.mark.parametrize("xml, result", [
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if>", True),
    ("<if>if <condition>(<expr><operator>!</operator><name>variable</name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><name></name><operator></operator></expr>)</condition></if>", False),
    ("<if><condition>(<expr><operator></operator><name></name></expr>)</condition></if><block><test>aa</test></block>", True),
    ("<if><condition>(<operator></operator><name></name>)</condition></if>", False)])
def test_contain_operator_name(xml, result):
    s = SrcmlFilters(xml, True)
    res=s.contain_operator_name()
    if res==result:
        assert True
        return

    assert False

@pytest.mark.parametrize("xml, result", [
    ("<if><condition>(<expr><name></name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><name>variable</name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><name></name></expr>)</condition></if><block><test>aa</test></block>", True),
    ("<if><condition>(<expr><name></name><name></name></expr>)</condition></if>", False),
    ("<if><conditions>(<expr><name></name></expr>)</conditions></if>", False)])
def test_contain_name(xml, result):
    s = SrcmlFilters(xml, True)
    res=s.contain_name()
    if res==result:
        assert True
        return

    assert False

@pytest.mark.parametrize("xml, result", [
    ("<if><condition>(<expr><name></name><operator></operator><literal></literal></expr>)</condition></if>", True),
    ("<if><condition>(<expr><name>test</name><operator></operator><literal>10</literal></expr>)</condition></if><block><test>aa</test></block>", True),
    ("<if><condition>(<expr><literal></literal><operator></operator><name>ciao</name></expr>)</condition></if>", True),
    ("<if><condition>(<expr><literal></name><operator></operator><name></literal></expr>)</condition></if>", False),
    ("<if><condition>(<expr><name></name><operator></operator><name></name></expr>)</condition></if>", False)])
def test_contain_operator_name_literal(xml, result):
    s = SrcmlFilters(xml, True)
    res=s.contain_operator_name_literal()
    if res==result:
        assert True
        return

    assert False

def test_contain_operator_name_name():
    assert False


def test_contain_equal():
    assert False


def test_apply_all_filters():
    assert False
