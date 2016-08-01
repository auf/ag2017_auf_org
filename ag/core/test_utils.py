# -*- encoding: utf-8 -*-


def find_input_by_id(tree, html_id):
        return tree.find("//input[@id='{0}']".format(html_id))


def find_input_by_name(tree, html_name):
        return tree.find("//input[@name='{0}']".format(html_name))

