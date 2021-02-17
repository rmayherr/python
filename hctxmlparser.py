"""Xml parser module for HCT application.

Program accepts xml files as argument and print Namespace binding
configurations like id, key and its value.

    Typical usage example:

    python3 hctxmlparser.py -f hct01.xml

"""
import xml.etree.ElementTree as ET
import argparse


def read_xml(filename):
    """Read xml file and return xml root element.
    Args:
        filename: filename with the proper path.

    Returns:
        root element of XML structure.

    Raises:
        FileNotFoundError: Error occures if the file doesn't exist or it has
        wrong path specified.
        General exception: Anything else might occures

    """
    try:
        tree = ET.parse(filename)
    except FileNotFoundError:
        print('File not found.')
        return None
    except NameError:
        print('Parsing error.')
        return None
    return tree.getroot()

def get_nsb(root_tree):
    """Search 3 items 'nsb', 'nsb-name' and 'nsb-value' in the tree.

    Args:
        root_tree: the root of XML tree object.

    Returns:
        A List contains all necessary name space binding configuration
        encapsulated in a tuple.

    """
    out = []
    for i in root_tree.iter('nsb'):
        bind_id = i.attrib['id']
        key_value = i.find('nsb-name').attrib['value']
        string_value = i.find('nsb-value').attrib['value']
        out.append((bind_id, key_value, string_value))
    return out

def main():
    """Main function sets argument parser. Read filename passed as arguemnt.

    Args:
        No args.

    Returns:
        No returns.

    Raises:
        TypeError: Occurs when no argument added after -f switch.

    """
    _parser = argparse.ArgumentParser(description='Gain NSB information\
                                                from HCT xml file.')
    _parser.add_argument('-f', help='Add filename.', nargs='+')
    try:
        filename = vars(_parser.parse_args())['f'][0]
        if filename:
            _in = read_xml(filename)
            if _in :
                for i in get_nsb(_in):
                    print(','.join([*i]))
    except TypeError:
        print('No argument.')


if __name__ == '__main__':
    main()
