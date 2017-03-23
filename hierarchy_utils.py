'''
Utility functions for managing the hierarchy structure of
attributes in the module-attribute relationship tables
'''
import re

import parse_lib as pl

def get_hierarchy_markers(name):
    clean_name = name.strip()
    _, *split = re.split('^(>+)', clean_name)
    return '' if split == [] else split[0]


def get_hierarchy_level(name):
    return len(get_hierarchy_markers(name))


def clean_field(name):
    return re.sub(r'[>]', '', name).strip()


def record_hierarchy_for_module(table):
    last_id = [table['id']]
    current_level = -1
    for attr in table['attributes']:
        last_id, current_level = update_hierarchy_position(attr, last_id, current_level)
        format_attribute_fields(attr, last_id)
    return table


def update_hierarchy_position(attr, last_id, current_level):
    attr_id = pl.create_slug(clean_field(attr['tag']))
    attribute_level = get_hierarchy_level(attr['name'])
    delta_l = attribute_level - current_level
    if attr_id == 'none':
        print(attr)
        raise Exception('this shouldn\'t happen')
    if delta_l > 1:
        # There is a typo in the DICOM standard where two hierarchy
        # markers are used instead of one. This catches that anomaly.
        delta_l = 1
        # Error can be seen at the following link:
        # http://dicom.nema.org/medical/dicom/current/output/html/part03.html#para_a3f9cf09-67b7-4645-943a-6d405dc81b93
        # raise Exception('Shouldn\'t be skipping levels.')
    if delta_l == 0:
        last_id[-1] = attr_id
    elif delta_l == 1:
        last_id.append(attr_id)
        current_level += 1
    elif delta_l < 0:
        last_id = last_id[:(delta_l)]
        last_id[-1] = attr_id
        current_level += (delta_l)
    return last_id, current_level


def format_attribute_fields(attr, last_id):
    attr['name'] = clean_field(attr['name'])
    attr['tag'] = clean_field(attr['tag'])
    attr['type'] = clean_field(attr['type'])
    attr['id'] = ':'.join(last_id)
