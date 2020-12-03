import pytest
from srcML.srcml_parser import SrcmlParser
from srcML.srcml_manager import SrcmlManager


@pytest.mark.parametrize("file, tag, result", [("test_folder/srcml/srcml_parser/file_1.xml", "if", 9),
                                               ("test_folder/srcml/srcml_parser/file_1.xml", "name", 66),
                                               ("test_folder/srcml/srcml_parser/file_1.xmll", "if", 0),
                                               ("test_folder/srcml/srcml_parser/file_1.xml", "operator", 24)])
def test_extract_all_tags(file, tag, result):

    m = SrcmlManager()
    xml_code = m.read_file(file)

    xml_code = "\n".join(xml_code)
    p = SrcmlParser(xml_code)

    tags=p.extract_all_tags(tag, p.soup)

    if len(tags)==result:
        assert True
        return

    assert False

@pytest.mark.parametrize("file, result", [("test_folder/srcml/srcml_parser/file_1.xml", 1),
                                               ("test_folder/srcml/srcml_parser/calculator.xml", 5)])
def test_extract_methods(file, result):
    m = SrcmlManager()
    xml_code = m.read_file(file)

    xml_code = "\n".join(xml_code)
    p = SrcmlParser(xml_code)
    p.extract_methods()

    if len(p.methods) == result:
        assert True
        return

    assert False

@pytest.mark.parametrize("file, tag, result", [("test_folder/srcml/srcml_parser/file_1.xml", "if", True),
                                               ("test_folder/srcml/srcml_parser/file_1.xml", "namee", False),
                                               ("test_folder/srcml/srcml_parser/file_1.xmll", "if", False),
                                               ("test_folder/srcml/srcml_parser/file_1.xml", "operator", True)])
def test_contain_tag(file, tag, result):
    m = SrcmlManager()
    xml_code = m.read_file(file)

    xml_code = "\n".join(xml_code)
    p = SrcmlParser(xml_code)

    res=p.contain_tag(tag, p.soup)
    if res == result:
        assert True
        return

    assert False


def test_check_contain_if():
    assert False


def test_apply_filters_if():
    assert False
