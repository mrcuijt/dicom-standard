'''
Find and mark references to external sections in attribute descriptions.
Each reference is keyed by its source URL.
'''
import sys
import re

from bs4 import BeautifulSoup

import parse_lib as pl

IGNORED_REFERENCES_RE = re.compile(r'(.*ftp.*)|(.*http.*)|(.*part05.*)|(.*chapter.*)|(.*PS3.*)|(.*DCM.*)|(.*glossentry.*)')


def get_reference_requests_from_pairs(module_attr_pairs):
    return [references_from_module_attr_pair(pair) for pair in module_attr_pairs]


def references_from_module_attr_pair(pair):
    references = get_valid_reference_anchors(BeautifulSoup(pair['description'], 'html.parser'))
    return list(map(get_resolved_reference_href, references))


def get_valid_reference_anchors(parsed_html):
    anchor_tags = parsed_html.find_all('a', href=True)
    return [a for a in anchor_tags if not re.match(IGNORED_REFERENCES_RE, a['href'])]


def get_resolved_reference_href(reference_anchor_tag):
    relative_link = reference_anchor_tag.get('href')
    standard_page, section_id = relative_link.split('#')
    standard_page = 'part03.html' if standard_page == '' else standard_page
    return standard_page + '#' + section_id


def record_references_inside_pairs(module_attr_pairs):
    updated_pairs = [record_reference_in_pair(pair) for pair in module_attr_pairs]
    return updated_pairs


def record_reference_in_pair(pair):
    parsed_description = BeautifulSoup(pair['description'], 'html.parser')
    references = get_valid_reference_anchors(parsed_description)
    external_references = list(map(reference_structure_from_anchor, references))
    list(map(mark_as_recorded, references))
    pair['externalReferences'] = [] if len(external_references) < 1 else external_references
    pair['description'] = str(parsed_description)
    return pair


def reference_structure_from_anchor(reference):
    return {
        "sourceUrl": pl.BASE_DICOM_URL + get_resolved_reference_href(reference),
        "title": reference.get_text()
    }


def mark_as_recorded(anchor):
    anchor['href'] = ''
    anchor.name = 'span'


if __name__ == '__main__':
    module_attr_pairs = pl.read_json_to_dict(sys.argv[1])
    updated_pairs = record_references_inside_pairs(module_attr_pairs)
    pl.write_pretty_json(updated_pairs)
