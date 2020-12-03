from srcML.srcml_manager import SrcmlManager
import os
import pytest

@pytest.mark.parametrize("name, result", [("test_folder/srcml/srcml_manager/file_1_correct.xml", 65),
                                               ("test_folder/srcml/srcml_manager/file_1.java", 63), ("test_folder/srcml_srcml_manager/file_1.cpp", 0)])
def test_read_file(name, result):
    s=SrcmlManager()
    res=s.read_file(name)
    if len(res)==result:
        assert True
        return
    assert False

@pytest.mark.parametrize("name, result", [("test_folder/srcml/srcml_manager/file_1.java", "test_folder/srcml/srcml_manager/file_1.xml"),
                                               ("test_folder/srcml/srcml_manager/file_2.java", "test_folder/srcml/srcml_manager/file_2.xml")])
def test_process_with_srcml(name, result):
    s=SrcmlManager()
    s.process_with_srcml(os.path.join(os.getcwd(), name))

    generated_file=s.read_file(name.replace(".java", ".xml"))

    real_file=s.read_file(result)

    if generated_file == real_file:
        assert True
        return

    assert False

