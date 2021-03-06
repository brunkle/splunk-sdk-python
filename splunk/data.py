# Copyright 2011 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A generic ATOM response loader."""

import sys
from xml.etree.ElementTree import XML

__all__ = ["load"]

LNAME_DICT = "dict"
LNAME_ITEM = "item"
LNAME_KEY = "key"
LNAME_LIST = "list"

XNAMEF_REST = "{http://dev.splunk.com/ns/rest}%s"
XNAME_DICT = XNAMEF_REST % LNAME_DICT
XNAME_ITEM = XNAMEF_REST % LNAME_ITEM
XNAME_KEY = XNAMEF_REST % LNAME_KEY
XNAME_LIST = XNAMEF_REST % LNAME_LIST

# Some responses don't use namespaces (eg: search/parse) so we look for
# both the extended and local versions of the following names.

def isdict(name):
    return name == XNAME_DICT or name == LNAME_DICT

def isitem(name):
    return name == XNAME_ITEM or name == LNAME_ITEM

def iskey(name):
    return name == XNAME_KEY or name == LNAME_KEY

def islist(name):
    return name == XNAME_LIST or name == LNAME_LIST

def hasattrs(element):
    return len(element.attrib) > 0

def localname(xname):
    rcurly = xname.find('}')
    return xname if rcurly == -1 else xname[rcurly+1:]

def load(text, match=None):
    """Load the given XML text into a Python structure, optionally loading 
       only the matching sub-elements if a match string is given. The match
       string consists of either a tag name or path."""
    if text is None: return None
    text = text.strip()
    if len(text) == 0: return None
    nametable = {
        'namespaces': [],
        'names': {}
    }
    root = XML(text)
    items = [root] if match is None else root.findall(match)
    count = len(items)
    if count == 0: return None
    if count == 1: return load_root(items[0], nametable)
    return [ load_root(item, nametable) for item in items ]

# Load the attributes of the given element.
def load_attrs(element):
    if not hasattrs(element): return None
    attrs = record()
    for key, value in element.attrib.iteritems(): 
        attrs[key] = value
    return attrs

# Parse a <dict> element and return a Python dict
def load_dict(element, nametable = None):
    value = record()
    children = list(element)
    for child in children:
        assert iskey(child.tag)
        name = child.attrib["name"]
        value[name] = load_value(child, nametable)
    return value

# Loads the given elements attrs & value into single merged dict.
def load_elem(element, nametable=None):
    name = localname(element.tag)
    attrs = load_attrs(element)
    value = load_value(element, nametable)
    if attrs is None: return name, value
    if value is None: return name, attrs
    # If value is simple, merge into attrs dict using special key
    if isinstance(value, str):
        attrs["$text"] = value
        return name, attrs
    # Both attrs & value are complex, so merge the two dicts
    for key, val in attrs.iteritems():
        #assert not value.has_key(k) # Assume no collisions
        value[key] = val
    return name, value

# Parse a <list> element and return a Python list
def load_list(element, nametable=None):
    assert islist(element.tag)
    value = []
    children = list(element)
    for child in children:
        assert isitem(child.tag)
        value.append(load_value(child, nametable))
    return value

# Load the given root element.
def load_root(element, nametable=None):
    tag = element.tag
    if isdict(tag): return load_dict(element, nametable)
    if islist(tag): return load_list(element, nametable)
    k, v = load_elem(element, nametable)
    return Record.fromkv(k, v)

# Load the children of the given element.
def load_value(element, nametable=None):
    children = list(element)
    count = len(children)

    # No children, assume a simple text value
    if count == 0:
        text = element.text
        if text is None: 
            return None
        text = text.strip()
        if len(text) == 0: 
            return None
        return text

    # Look for the special case of a single well-known structure
    if count == 1:
        child = children[0]
        tag = child.tag
        if isdict(tag): return load_dict(child, nametable)
        if islist(tag): return load_list(child, nametable)

    value = record()
    for child in children:
        name, item = load_elem(child, nametable)
        # If we have seen this name before, promote the value to a list
        if value.has_key(name):
            current = value[name]
            if not isinstance(current, list): 
                value[name] = [current]
            value[name].append(item)
        else:
            value[name] = item

    return value

# A generic utility that enables "dot" access to dicts
class Record(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError: 
            raise AttributeError(name)

    def __delattr__(self, name):
        del self[name]

    def __setattr__(self, name, value):
        self[name] = value

    @staticmethod
    def fromkv(k, v):
        result = record()
        result[k] = v
        return result

def record(value=None): 
    if value is None: value = {}
    return Record(value)

