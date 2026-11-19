#!/usr/bin/env python3
"""Add application rules while retaining the base image's desktop controls."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

NS = 'http://openbox.org/3.4/rc'
ET.register_namespace('', NS)


def tag(name):
    return f'{{{NS}}}{name}'


def configure(path):
    tree = ET.parse(path)
    root = tree.getroot()
    apps = root.find(tag('applications'))
    if apps is None:
        apps = ET.SubElement(root, tag('applications'))
    # The LSIO base maximizes every window, including floating Wine dialogs.
    for rule in apps.findall(tag('application')):
        if rule.get('class') == '*':
            for maximized in rule.findall(tag('maximized')):
                rule.remove(maximized)
    for kind in ('normal', 'dialog'):
        rule = ET.SubElement(apps, tag('application'), {'class': '*', 'type': kind})
        position = ET.SubElement(rule, tag('position'), {'force': 'yes'})
        ET.SubElement(position, tag('x')).text = 'center'
        ET.SubElement(position, tag('y')).text = 'center'
        ET.SubElement(position, tag('monitor')).text = 'active'
        ET.SubElement(rule, tag('maximized')).text = 'no'
        if kind == 'dialog':
            ET.SubElement(rule, tag('decor')).text = 'yes'
    for executable in ('ahnblatt.exe', 'ahnenblatt*.exe'):
        rule = ET.SubElement(apps, tag('application'), {
            'class': executable, 'type': 'normal', 'title': '*Ahnenblatt*',
        })
        ET.SubElement(rule, tag('decor')).text = 'no'
        ET.SubElement(rule, tag('maximized')).text = 'yes'
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    configure(Path(sys.argv[1]))
