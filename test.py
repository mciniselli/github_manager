from utils.command_line import CommandLineHelper

from utils.github_helper import GithubHelper
import json
import os
from srcML.srcml_filters import SrcmlFilters, KeyValueNode, Fields
from srcML.srcml_parser import SrcmlParser

from utils.settings import init_global

class Operation():

    def max(values):

      _max = values[0]

      for val in values:
          if val > _max:
              _max = val

      return _max


    def min(values):

      _min = values[0]

      for val in values:
          if val < _min:
              _min = val

      return _min



def main():

    g=GithubHelper()
    # g.clone("mciniselli/test", "test/test_folder/github_helper/output")
    # g.checkout("test/test_folder/github_helper/output/test")

    g.clone("mciniselli/test_branch", "test/test_folder/github_helper/output")
    g.checkout("test/test_folder/github_helper/output/test_branch")

def test_xml():
    import xml.etree.ElementTree as ET
    tree = ET.parse("test/test_folder/srcml_manager/file_1.xml")
    root = tree.getroot()
    print(root)
    print(root.tag)
    print(root.attrib)
    print("CHILD")
    for c in root:
        print(c.tag, c.attrib)
        # for cc in c:
        #     print(cc.tag, cc.attrib)

    # print("___")
    # print(root.findall("import"))
    for elem in tree.iter():
        if elem.tag=="{http://www.srcML.org/srcML/src}if":
            for i in elem.iter():
                print(i.text)

                a=1
                # if i.tail is not None:
                #     print("TAIL {}".format(i.tail))
                # if i.tail is not None:
                #     print(i.tail)
                a=1
                # print(i.tag, "|{}|".format(i.text))
            print("____")


def read_file(filepath):  # read generic file
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.readlines()
        c_ = list()
        for c in content:
            r = c.rstrip("\n").rstrip("\r")
            c_.append(r)

    except Exception as e:
        print("Error ReadFile: " + str(e))
        c_ = []
    return c_

def test_xml_2():
    # from xml.dom.minidom import parse, parseString
    from lxml import etree
    root = etree.parse("test/test_folder/srcml_manager/file_1.xml")
    for tag in root.iter():
        if tag.tag=="{http://www.srcML.org/srcML/src}if":

            for t in tag.iter():
                print(t.text)
                a=1

def test_xml_3():

    import xml.etree.ElementTree as ET
    tree = ET.parse("test/test_folder/srcml_manager/file_1.xml")
    root = tree.getroot()

    for elem in tree.iter():
        if elem.tag=="{http://www.srcML.org/srcML/src}if":

            print(ET.tostring(elem, method='c14n'))
            print("____")


    # for a in top.iter('a'):
    #     s = ET.tostring(a, method='text')
    #     print
    #     s

def test_xml_4():
    from bs4 import BeautifulSoup

    with open('test/test_folder/srcml_manager/file_1.xml', 'r') as f:

        contents = f.read()

        soup = BeautifulSoup(contents, 'lxml')

        for child in soup.recursiveChildGenerator():

            if child.name=="if":
                a=1
                for c in child.recursiveChildGenerator():
                    if str(type(c))=="<class 'bs4.element.NavigableString'>":
                        print(type(c), "|{}|".format(c))
                        b=type(c)
                        a=1
                    else:
                        print(c.name)
                print("____")


def return_text(items, C, result):
    res_curr=result
    if len(items)==1:
        for child in C.recursiveChildGenerator():
            if child.name == items[0]:
                res_temp = list()

                for c in child.recursiveChildGenerator():
                    if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                        print(type(c), "|{}|".format(c))
                        res_temp.append("|{}|".format(c))

                print("____")
                res_curr.append(res_temp)
        return res_curr
    else:
        for child in C.recursiveChildGenerator():
            if child.name == items[0]:
                return_text(items[1:], child, result)


def return_text_new(items, C, result, index):
    res_curr=result
    index_curr=index
    if len(items)==1:
        for child in C.recursiveChildGenerator():
            if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                index_curr+=1
            if child.name == items[0]:
                res_temp = list()
                index_local=0
                for c in child.recursiveChildGenerator():
                    if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                        print(type(c), "|{}|".format(c))
                        res_temp.append("{} |{}|".format(index_curr+index_local, c))
                        index_local+=1

                print("____")
                res_curr.append(res_temp)
        return res_curr
    else:
        for child in C.recursiveChildGenerator():
            if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                index_curr+=1
            if child.name == items[0]:
                return_text_new(items[1:], child, result, index_curr)


def return_text_new_new(items, C, result, index, line):
    res_curr=result
    index_curr=index
    line_curr=line
    if len(items)==1:
        for child in C.recursiveChildGenerator():
            if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                index_curr+=1
                if child == "\n":
                    line_curr+=1
            if child.name == items[0]:
                res_temp = list()
                index_local=0
                line_local=0
                for c in child.recursiveChildGenerator():
                    if str(type(c)) == "<class 'bs4.element.NavigableString'>":
                        if c =="\n":
                            line_local+=1
                        print(type(c), "|{}|".format(c))
                        res_temp.append("CHAR {} LINE {} |{}|".format(index_curr+index_local, line_curr+line_local, c))
                        index_local+=1

                print("____")
                res_curr.append(res_temp)
        return res_curr
    else:
        for child in C.recursiveChildGenerator():
            if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                index_curr+=1
                if child=="\n":
                    line_curr+=1
            if child.name == items[0]:
                return_text_new_new(items[1:], child, result, index_curr, line_curr)

def test_xml_5():
    from bs4 import BeautifulSoup

    with open('test/test_folder/srcml_manager/file_1.xml', 'r') as f:

        contents = f.read()

        soup = BeautifulSoup(contents, 'lxml')

        items=["if", "condition"]
        result=list()
        return_text(items, soup, result)

        print(len(result))
        for r in result:
            print(" ".join(r))
            print("_____")

def test_xml_6():
    from bs4 import BeautifulSoup

    with open('test/test_folder/srcml_manager/file_1.xml', 'r') as f:

        contents = f.read()

        soup = BeautifulSoup(contents, 'lxml')

        items=["function", "if", "call"]
        # items=["if"]
        result=list()
        index=0

        for child in soup.recursiveChildGenerator():
            if str(type(child)) == "<class 'bs4.element.NavigableString'>":
                print(index, child)
                index+=1


        index=0

        return_text_new(items, soup, result, index)

        print(len(result))
        for r in result:
            print(" ".join(r))
            print("_____")

def test_xml_7():
    from bs4 import BeautifulSoup

    with open('test/test_folder/srcml_manager/file_1.xml', 'r') as f:

        contents = f.read()

        soup = BeautifulSoup(contents, 'lxml')

        items=["function", "if"]
        # items=["if"]
        result=list()
        index=0
        line=0

        # for child in soup.recursiveChildGenerator():
        #     if str(type(child)) == "<class 'bs4.element.NavigableString'>":
        #         print(index, child)
        #         index+=1
        #         if child=="\n":
        #             print("AAA")


        for child in soup.recursiveChildGenerator():
            print(child)


        return
        index=0

        return_text_new_new(items, soup, result, index, line)

        print(len(result))
        for r in result:
            print(" ".join(r))
            print("_____")


def test_xml_8():
    from bs4 import BeautifulSoup
    with open('test/test_folder/srcml_manager/file_1.xml', 'r') as f:

        contents = f.read()

        soup = BeautifulSoup(contents, 'lxml')
        ifs = soup.select("if")

        for i in ifs:
            a=1
            c=i.findChild()
            # print(c)
            for a in c.children:
                print("{} child of {}".format(a.name, c.name))
            c2=c.findChild()
            # print(c2)
            for a in c2.children:
                print("{} child of {}".format(a.name, c2.name))
            c3=c2.findChild()
            # print(c3)
            for a in c3.children:
                print("{} child of {}".format(a.name, c3.name))
            return

def test_srcml_parser():
    from srcML.srcml_parser import SrcmlParser
    from srcML.srcml_manager import SrcmlManager
    from srcML.srcml_filters import SrcmlFilters
    m=SrcmlManager()
    m.process_with_srcml("test/test_folder/srcml/srcml_manager/file_1.java")
    xml=m.get_xml()

    s=SrcmlParser(xml)
    s.extract_methods()

    print(len(s.methods))

    s.apply_filters_if()

def test_tree():
    from anytree import Node, RenderTree

    udo = Node("Udo")
    marc = Node("Marc", parent=udo)
    lian = Node("Lian", parent=marc)
    dan = Node("Dan", parent=udo)
    jet = Node("Jet", parent=dan)
    jan = Node("Jan", parent=dan)
    joe = Node("Joe", parent=dan)

    print("CHILD")
    print(dan.children)
    print(dan.name)

    print(udo)
    Node('/Udo')
    print(joe)
    Node('/Udo/Dan/Joe')

    for pre, fill, node in RenderTree(udo):
        print("%s%s" % (pre, node.name))

    from anytree.exporter import JsonExporter

    exporter = JsonExporter(indent=2, sort_keys=True)
    print("EXPORT")
    print(exporter.export(udo))

def test_merge_tree():
    s = SrcmlFilters("<if></if>", True)
    s2 = SrcmlFilters("<fake><condition>(<expr><operator></operator><name></name></expr>)</condition></fake>", True)
    s.add_children_to_node(s.tree, s2.xml_code, Fields.SKIP.value)
    s.print_tree()

def test_equal():
    xml="<if><condition>(<expr><operator></operator><call><name><name></name><operator>.</operator><name>equal</name></name><argument_list>(<argument><expr><name></name></expr></argument>)</argument_list></call></expr>)</condition></if>"
    s = SrcmlFilters(xml, True)
    s.print_tree()
    res = s.contain_equal()
    print(res)

def test():
    from srcML.srcml_filters import SrcmlFilters
    xml_code = "<xml><hello>hello</hello></xml>"
    xml_code2 = "<fake><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></fake>"

    filters = SrcmlFilters(xml_code, True)
    filters.print_tree()

    filters2 = SrcmlFilters(xml_code2, True)
    filters2.print_tree()

    filters.add_children_to_node_with_text(filters.tree, filters2.tree, [None, "block"])
    filters.print_tree()

def process_json_file():
    json_file = "json_data/results.json"

    start=0
    end=10
    do_abstraction=False


    file_data = read_file(json_file)
    data = json.loads(file_data[0])
    items = (data["items"])[start:end]
    print(len(items))

    # for i, item in enumerate(items):
    #     print(i, item)

    file_name="results.json"

    from utils.logger import Logger
    log=Logger("logger.log")

    from repoManager.repo import Repo

    from datetime import datetime
    print(datetime.now())

    for i, item in enumerate(items):
        try:
            print("Processed {} repositories of out {}".format(i+1, len(items)))
            repo_name = item["name"]
            repo_commit = item["lastCommitSHA"]
            repo_url = "https://github.com/{}".format(repo_name)
            print(repo_url)
            r = Repo(repo_name, repo_url, repo_commit, start+i, do_abstraction)
            r.clone_repo("cloning_folder")
            r.add_files()

            for f in r.files:
                for m in f.methods:
                    m.check_conditions()

            from repoManager.store import Store

            store = Store()
            store.export_data(r)
        except Exception as e:
            print("ERROR {}".format(e))

    print(datetime.now())

def test_remove():
    from srcML.srcml_filters import SrcmlFilters
    xml_code2 = "<fake><function><if>if <condition>(<expr><name>var</name></expr>)</condition><condition>(<expr><name>var</name></expr>)</condition></if></function></fake>"
    # xml_code2 = "<fake><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if></function></fake>"


    filters2 = SrcmlFilters(xml_code2, True)
    filters2.print_tree()

    xml=filters2.xml_code
    print(xml)
    a=xml.select("condition")

    old_condition=SrcmlFilters("<condition>(<expr><name>var</name></expr>)</condition>", True)

    # b=xml.select_one(old_condition.xml_code)

    curr=a[0]


    # bb=xml.find(curr)
    from bs4 import BeautifulSoup
    aa=BeautifulSoup("<new_condition>aa</new_condition>", "lxml")

    # aaaa=xml.find(BeautifulSoup("<condition>(<expr><name>var</name></expr>)</condition>"))

    # xml.find("condition").replaceWith(aa)

    filter_new=SrcmlFilters("<new_condition>aa</new_condition>", True)

    # xml.find("condition").replaceWith(filter_new.xml_code)

    # xml.select_one("condition").name="BB"
    # xml.find("condition").name="BA"


    xml.select("condition")[1].replaceWith(filter_new.xml_code)


    xml.select_one("condition").replaceWith(filter_new.xml_code)


    # filters2.xml_code=filters2.xml_code.select("condition")[0].decompose()
    filters2.print_tree()


def test_add_tag():
    from srcML.srcml_filters import SrcmlFilters
    xml_code = "<fake><function><if>if <condition>(<expr><name>var</name></expr>)</condition></if> <if>if <condition>(<expr><name>NEW</name></expr>)</condition> </if></function></fake>"
    xml_code = "<fake><function><if test=\"A\">if <condition>(<expr><name>var</name></expr>)</condition></if> <if test=\"B\">if <condition>(<expr><name>NEW</name></expr>)</condition> </if></function></fake>"

    parser = SrcmlParser(xml_code)

    xml=parser.soup

    xml.find("if",  {"test": "B"}).replaceWith("AA")

    aa=1

    # if_conditions = parser.extract_all_tags("if", parser.soup)
    # for if_condition in if_conditions:
    #     if_condition["test"]="CC"
    # print(len(if_conditions))

def tt():

    json_file = "json_data/results.json"
    file_data = read_file(json_file)
    data = json.loads(file_data[0])
    items = (data["items"])
    print(len(items))

    file_name="results.json"

    from repoManager.repo import Repo

    r=None

    for i, item in enumerate(items):

        print("Processed {} repositories of out {}".format(i, len(items)))
        repo_name = item["name"]
        repo_commit = item["lastCommitSHA"]
        repo_url = "https://github.com/{}".format(repo_name)
        print(repo_url)
        r = Repo(repo_name, repo_url, repo_commit)
        # r.clone_repo("cloning_folder")
        r.add_files()

        for f in r.files:
            for m in f.methods:
                m.check_conditions()


        break

    from repoManager.store import Store

    store=Store()
    store.create_file_masked(r)


def test_src2abs():

    cwd="abstraction"

    file_to_process=os.listdir(cwd)

    n=100
    file="source_method2.java"
    import shutil
    from subprocess import Popen, PIPE, \
        STDOUT  # use subprocess to run a python file inside the script. It is quicker than os.system()

    from datetime import datetime
    print(datetime.now())

    for i in range(n):
        if os.path.exists(os.path.join(cwd, file.replace("2", str(i)))) == False:
            shutil.copy(os.path.join(cwd, file), os.path.join(cwd, file.replace("2", str(i))))

    for i in range(n):
        cmd = "java -jar src2abs-0.1-jar-with-dependencies.jar single method ./source_method{}.java ./source_method{}_abs.java ./Java_Idioms.csv".format(i, i)

        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True, cwd=cwd)
        output = p.stdout.read()

    print(datetime.now())

def method_nested():
    from repoManager.repo import Repo
    r = Repo("a", "b", "c", 1000, True)
    r.cloned_directory="test/method_nested"
    r.add_files()

    for f in r.files:
        for m in f.methods:
            m.check_conditions()

    from repoManager.store import Store

    store = Store()
    store.export_data(r)

if __name__=="__main__":
    init_global("logger.log")
    # main()
    # test_srcml_parser()
    # test_tree()
    # test_merge_tree()
    # test_equal()
    # test()
    process_json_file()
    # test_remove()
    # test_add_tag()
    # tt()
    # test_src2abs()
    # method_nested()