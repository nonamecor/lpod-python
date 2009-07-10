# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime, timedelta
from sys import _getframe, modules
from os import getcwd
from os.path import splitdrive, join, sep


DATE_FORMAT = '%Y-%m-%d'


DATETIME_FORMAT = DATE_FORMAT + 'T%H:%M:%S'


DURATION_FORMAT = 'PT%02dH%02dM%02dS'


CELL_TYPES = ('boolean', 'currency', 'date', 'float', 'percentage', 'string',
              'time')

STYLE_FAMILIES = ('paragraph', 'text', 'section', 'table', 'table-column',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control', 'ruby', 'page-layout')

NOTE_CLASSES = ('footnote', 'endnote')



def _get_abspath(local_path):
    """Returns the absolute path to the required file.
    """

    mname = _getframe(1).f_globals.get('__name__')

    if mname == '__main__' or mname == '__init__':
        mpath = getcwd()
    else:
        module = modules[mname]
        if hasattr(module, '__path__'):
            mpath = module.__path__[0]
        elif '.' in mname:
            mpath = modules[mname[:mname.rfind('.')]].__path__[0]
        else:
            mpath = mname

    drive, mpath = splitdrive(mpath)
    mpath = drive + join(mpath, local_path)

    # Make it working with Windows. Internally we use always the "/".
    if sep == '\\':
        mpath = mpath.replace(sep, '/')

    return mpath



def _make_xpath_query(element_name, style=None, family=None, frame_name=None,
                      frame_style=None, table_name=None, style_name=None,
                      note_class=None, text_id=None, level=None,
                      position=None, context=None, **kw):
    if context is None:
        query = ['//']
    else:
        query = []
    query.append(element_name)
    attributes = kw
    if style:
        attributes['text:style-name'] = style
    if family:
        attributes['style:family'] = family
    if frame_name:
        attributes['draw:name'] = frame_name
    if frame_style:
        attributes['draw:style-name'] = frame_style
    if table_name:
        attributes['table:name'] = table_name
    if style_name:
        attributes['style:name'] = style_name
    if note_class:
        attributes['text:note-class'] = note_class
    if text_id:
        attributes['text:id'] = text_id
    if level:
        attributes['text:outline-level'] = level
    # Sort attributes for reproducible test cases
    for qname in sorted(attributes):
        value = attributes[qname]
        if value is not None:
            query.append('[@{qname}="{value}"]'.format(qname=qname,
                                                      value=str(value)))
        else:
            query.append('[@{qname}]'.format(qname=qname))
    if position is not None:
        query.append('[{position}]'.format(position=str(position)))
    return ''.join(query)



def _get_cell_coordinates(name):
    lower = name.lower()

    # First "x"
    x = 0
    for p in xrange(len(lower)):
        c = lower[p]
        if not c.isalpha():
            break
        v = ord(c) - ord('a') + 1
        x = x * 26 + v
    if x == 0:
        raise ValueError, 'cell name "%s" is malformed' % name

    # And "y"
    try:
        y = int(lower[p:])
    except ValueError:
        raise ValueError, 'cell name "%s" is malformed' % name
    if y <= 0:
        raise ValueError, 'cell name "%s" is malformed' % name

    return x, y



def _check_arguments(context=None, element=None, xmlposition=None,
                     position=None, level=None, text=None, style=None,
                     family=None, cell_type=None, currency=None,
                     note_class=None, creator=None, date=None,
                     start_date=None, end_date=None, offset=None,
                     retrieve_by=None):
    if context is not None:
        # FIXME cyclic import
        from xmlpart import odf_element
        if not isinstance(context, odf_element):
            raise TypeError, "context must be an odf element"
    if element is not None:
        # FIXME cyclic import
        from xmlpart import odf_element
        if not isinstance(element, odf_element):
            raise TypeError, "element must be an odf element"
    if xmlposition is not None:
        # FIXME cyclic import
        from xmlpart import STOPMARKER
        if type(xmlposition) is not int or xmlposition >= STOPMARKER:
            raise ValueError, "invalid XML position"
    if position is not None:
        if type(position) is not int:
            raise TypeError, "an integer position is expected"
        if position < 1:
            raise ValueError, "position count begin at 1"
    if level is not None:
        if not isinstance(level, int):
            raise TypeError, "an integer level is expected"
        if level < 1:
            raise ValueError, "level count begin at 1"
    if text is not None:
        if type(text) is not unicode:
            raise TypeError, "text must be an unicode string"
    if style is not None:
        if type(style) is not str:
            raise TypeError, "a style name is expected"
    if family is not None:
        if not family in STYLE_FAMILIES:
            raise ValueError, '"%s" is not a valid style family' % family
    if cell_type is not None:
        if not cell_type in CELL_TYPES:
            raise ValueError, '"%s" is not a valid cell type' % cell_type
        if cell_type == 'currency':
            if currency is None:
                raise ValueError, 'currency is mandatory in monetary cells'
            if type(currency) is not str:
                raise TypeError, 'currency must be a three-letter code'
    if note_class is not None:
        if not note_class in NOTE_CLASSES:
            raise ValueError, '"%s" is not a valid note class' % note_class
    if creator is not None:
        if type(creator) is not unicode:
            raise TypeError, "creator must be an unicode string"
    if date is not None:
        if type(date) is not datetime:
            raise TypeError, "date must be a datetime object"
    if start_date is not None:
        if type(start_date) is not datetime:
            raise TypeError, "start date must be a datetime object"
    if end_date is not None:
        if type(end_date) is not datetime:
            raise TypeError, "end date must be a datetime object"
    if offset is not None:
        if type(offset) is not int:
            raise TypeError, "offset must be an integer"
    if retrieve_by is not None:
        if retrieve_by not in ('name', 'display-name'):
            raise ValueError, ('retrieve_by must be "name" '
                               'or "display-name"')




def _check_position_or_name(position, name):
    if not ((position is None) ^ (name is None)):
        raise ValueError, 'You must choose either position or name'



class Date(object):

    @staticmethod
    def decode(data):
        return datetime.strptime(data, DATE_FORMAT)


    @staticmethod
    def encode(value):
        return value.strftime(DATE_FORMAT)



class DateTime(object):

    @staticmethod
    def decode(data):
        return datetime.strptime(data, DATETIME_FORMAT)


    @staticmethod
    def encode(value):
        return value.strftime(DATETIME_FORMAT)



class Duration(object):
    """ISO 8601 format.
    """

    @staticmethod
    def decode(data):
        if not data.startswith('PT'):
            raise ValueError, "duration is not '%s" % DURATION_FORMAT
        hours = ''
        minutes = ''
        seconds = ''
        bufffer = ''
        for c in data:
            if c.isdigit():
                bufffer += c
            elif c == 'H':
                hours = int(bufffer)
                bufffer = ''
            elif c == 'M':
                minutes = int(bufffer)
                bufffer = ''
            elif c == 'S':
                seconds = int(bufffer)
                break
        else:
            raise ValueError, "duration is not '%s" % DURATION_FORMAT
        return timedelta(0, seconds, 0, 0, minutes, hours, 0)


    @staticmethod
    def encode(value):
        if type(value) is not timedelta:
            raise TypeError, "duration must be a timedelta"
        days = value.days
        hours = days * 24
        minutes = value.seconds / 60
        seconds = value.seconds % 60
        return DURATION_FORMAT % (hours, minutes, seconds)



class Boolean(object):

    @staticmethod
    def decode(data):
        if data == 'true':
            return True
        elif data == 'false':
            return False
        raise ValueError, 'boolean "%s" is invalid' % data


    @staticmethod
    def encode(value):
        if value is True:
            return 'true'
        elif value is False:
            return 'false'
        raise TypeError, '"%s" is not a boolean' % value
