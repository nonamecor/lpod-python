# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from copy import deepcopy
from datetime import date, datetime, timedelta
from decimal import Decimal

# Import from lpod
from container import odf_get_container, odf_new_container_from_template
from container import odf_new_container_from_class, odf_container
from utils import _check_arguments, _generate_xpath_query
from utils import _check_position_or_name, _get_cell_coordinates
from utils import Date, DateTime, Duration, Boolean
from xmlpart import odf_xmlpart, LAST_CHILD
from xmlpart import odf_create_element


#
# odf creation functions
#

def odf_create_section(style):
    """Create a section element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    _check_arguments(style=style)
    data = '<text:section text:style-name="%s"></text:section>' % style
    return odf_create_element(data)



def odf_create_paragraph(style, text=u''):
    """Create a paragraph element of the given style containing the optional
    given text.
    Arguments:

        style -- str
        text -- unicode

    Return: odf_element
    """
    _check_arguments(style=style, text=text)
    data = '<text:p text:style-name="%s">%s</text:p>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, text))



def odf_create_heading(style, level, text=u''):
    """Create a heading element of the given style and level, containing the
    optional given text.
    Arguments:

        style -- str
        level -- int
        text -- unicode

    Return: odf_element

    Level count begins at 1.
    """
    _check_arguments(style=style, level=level, text=text)
    data = '<text:h text:style-name="%s" text:outline-level="%d">%s</text:h>'
    text = text.encode('utf_8')
    return odf_create_element(data % (style, level, text))



def odf_create_frame(name, style, width, height, page=None, x=None, y=None):
    """Create a frame element of the given style, width and height,
    optionally positionned at the given x and y coordinates, in the given
    page.
    Arguments:

        style -- str
        width -- str
        height -- str
        page -- int
        x -- str
        y -- str

    Return: odf_element

    Width, height, x and y are strings including the units, e.g. "10cm".
    """
    if page is None:
        anchor = 'text:anchor-type="paragraph"'
    else:
        anchor = 'text:anchor-type="page" text:anchor-page-number="%d"' % page
        if x is not None:
            anchor += ' svg:x="%s"' % x
        if y is not None:
            anchor += ' svg:y="%s"' % y
    data = ('<draw:frame draw:name="%s" draw:style-name="%s" '
            'svg:width="%s" svg:height="%s" %s/>')

    return odf_create_element(data % (name, style, width, height, anchor))



def odf_create_image(uri):
    """Create an image element showing the image at the given URI.
    Arguments:

        uri -- str

    Return: odf_element
    """
    return odf_create_element('<draw:image xlink:href="%s"/>' % uri)



def odf_create_cell(value, representation=None, cell_type=None,
                    currency=None):
    """Create a cell element containing the given value. The textual
    representation is automatically formatted but can be provided. Cell type
    can be deduced as well, unless the number is a percentage or currency. If
    cell type is "currency", the currency must be given.
    Arguments:

        value -- bool, int, float, Decimal, date, datetime, str, unicode,
                 timedelta
        representation -- unicode
        cell_type -- 'boolean', 'currency', 'date', 'float', 'percentage',
                     'string' or 'time'
        currency -- three-letter str

    Return: odf_element
    """
    if type(value) is bool:
        if cell_type is None:
            cell_type = 'boolean'
        if representation is None:
            representation = u'true' if value else u'false'
        value = Boolean.encode(value)
    elif isinstance(value, (int, float, Decimal)):
        if cell_type is None:
            cell_type = 'float'
        if representation is None:
            representation = unicode(value)
        value = str(value)
    elif type(value) is date:
        if cell_type is None:
            cell_type = 'date'
        if representation is None:
            representation = unicode(Date.encode(value))
        value = Date.encode(value)
    elif type(value) is datetime:
        if cell_type is None:
            cell_type = 'date'
        if representation is None:
            representation = unicode(DateTime.encode(value))
        value = DateTime.encode(value)
    elif type(value) is str:
        if cell_type is None:
            cell_type = 'string'
        if representation is None:
            representation = unicode(value)
    elif type(value) is unicode:
        if cell_type is None:
            cell_type = 'string'
        if representation is None:
            representation = value
        value = value.encode('utf_8')
    elif type(value) is timedelta:
        if cell_type is None:
            cell_type = 'time'
        if representation is None:
            representation = unicode(Duration.encode(value))
        value = Duration.encode(value)
    else:
        raise TypeError, 'type "%s" is unknown to cells' % type(value)
    _check_arguments(cell_type=cell_type, text=representation,
                     currency=currency)
    data = '<table:table-cell office:value-type="%s"/>'
    cell = odf_create_element(data % cell_type)
    if cell_type == 'boolean':
        cell.set_attribute('office:boolean-value', value)
    elif cell_type == 'currency':
        cell.set_attribute('office:value', value)
        cell.set_attribute('office:currency', currency)
    elif cell_type == 'date':
        cell.set_attribute('office:date-value', value)
    elif cell_type in ('float', 'percentage'):
        cell.set_attribute('office:value', value)
    elif cell_type == 'string':
        cell.set_attribute('office:string-value', value)
    elif cell_type == 'time':
        cell.set_attribute('office:time-value', value)
    cell.set_text_content(representation)
    return cell



def odf_create_row(width=None):
    """Create a row element, optionally filled with "width" number of cells.
    Arguments:

        width -- int

    Return: odf_element
    """
    row = odf_create_element('<table:table-row/>')
    if width is not None:
        for i in xrange(width):
            cell = odf_create_cell(u"")
            row.insert_element(cell, LAST_CHILD)
    return row



def odf_create_column(style):
    """Create a column element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    data = '<table:table-column table:style-name="%s"/>'
    return odf_create_element(data % style)



def odf_create_table(name, style, width=None, height=None):
    """Create a table element of the given style, with "width" columns and
    "height" rows.
    Arguments:

        style -- str
        width -- int
        height -- int

    Return: odf_element
    """
    data = '<table:table table:name="%s" table:style-name="%s"/>'
    table = odf_create_element(data % (name, style))
    if width is not None or height is not None:
        width = width if width is not None else 1
        height = height if height is not None else 1
        for i in xrange(height):
            row = odf_create_row(width)
            table.insert_element(row, LAST_CHILD)
    return table



def odf_create_list_item(text=None):
    """Create a list item element.
    Arguments:

        text -- unicode

    Return: odf_element

    The "text" argument is just a shortcut for the most common case. To create
    a list item with several paragraphs or anything else (except tables),
    first create an empty list item, insert it in the document, and insert
    your element using the list item as the context.
    """
    element = odf_create_element('<text:list-item/>')
    if text is not None:
        _check_arguments(text=text)
        element.set_text_content(text)
    return element



def odf_create_list(style):
    """Create a list element of the given style.
    Arguments:

        style -- str

    Return: odf_element
    """
    return odf_create_element('<text:list text:style-name="%s"/>' % style)



def odf_create_style(name, family='paragraph'):
    """Create a style element with the given name, related to the given
    family.
    Arguments:

        name -- str
        family -- 'paragraph', 'text', 'section', 'table', 'tablecolumn',
                  'table-row', 'table-cell', 'table-page', 'chart',
                  'default', 'drawing-page', 'graphic', 'presentation',
                  'control' or 'ruby'
    Return: odf_element
    """
    _check_arguments(family=family)
    data = '<style:style style:name="%s" style:family="%s"/>'
    return odf_create_element(data % (name, family))



def odf_create_style_text_properties():
    """Create a text properties element.
    Return: odf_element
    """
    # TODO should take parameters
    return odf_create_element('<style:text-properties/>')



def odf_create_note(text, note_class='footnote', id=None):
    """Create either a footnote or a endnote element with the given text,
    optionally referencing it using the given id.
    Arguments:

        text -- unicode
        note_class -- 'footnote' or 'endnote'
        id -- str

    Return: odf_element
    """
    _check_arguments(text=text, note_class=note_class)
    data = ('<text:note text:note-class="%s">'
              '<text:note-citation>%s</text:note-citation>'
              '<text:note-body/>'
            '</text:note>')
    text = text.encode('utf_8')
    note = odf_create_element(data % (note_class, text))

    if id is not None:
        note.set_attribute('text:id', id)

    return note



def odf_create_annotation(creator, text, date=None):
    """Create an annotation element credited to the given creator with the
    given text, optionally dated (current date by default).
    Arguments:

        creator -- unicode
        text -- unicode
        date -- datetime

    Return: odf_element
    """
    # TODO allow paragraph and text styles
    _check_arguments(creator=creator, text=text, date=date)
    data = ('<office:annotation>'
               '<dc:creator>%s</dc:creator>'
               '<dc:date>%s</dc:date>'
               '<text:p>%s</text:p>'
            '</office:annotation>')
    creator = creator.encode('utf_8')
    if date is None:
        date = datetime.now()
    date = DateTime.encode(date)
    text = text.encode('utf_8')
    return odf_create_element(data % (creator, date, text))


#
# The odf_document object
#

class odf_document(object):
    """An abstraction of the Open Document file.
    """
    def __init__(self, container):
        if not isinstance(container, odf_container):
            raise TypeError, "container is not an ODF container"
        self.container = container

        # Cache of XML parts
        self.__xmlparts = {}


    def __get_xmlpart(self, part_name):
        parts = self.__xmlparts
        part = parts.get(part_name)
        if part is None:
            container = self.container
            part = odf_xmlpart(part_name, container)
            parts[part_name] = part
        return part


    def __get_element_list(self, qname, style=None, attributes=None,
                           frame_style=None, context=None, part='content'):
        _check_arguments(style=style, context=context)
        part = self.__get_xmlpart(part)
        if attributes is None:
            attributes = {}
        if style:
            attributes['text:style-name'] = style
        if frame_style:
            attributes['draw:style-name'] = frame_style
        query = _generate_xpath_query(qname, attributes=attributes,
                context=context)
        if context is None:
            return part.get_element_list(query)
        return context.get_element_list(query)


    def __get_element(self, qname, position=None, attributes=None,
                      context=None, part='content'):
        _check_arguments(position=position, context=context)
        part = self.__get_xmlpart(part)
        if attributes is None:
            attributes = {}
        query = _generate_xpath_query(qname, attributes=attributes,
                                      position=position, context=context)
        if context is None:
            result = part.get_element_list(query)
        else:
            result = context.get_element_list(query)
        if not result:
            return None
        return result[0]


    def __insert_element(self, element, context, xmlposition, offset):
        _check_arguments(element=element, context=context,
                         xmlposition=xmlposition, offset=offset)
        if context is not None:
            context.insert_element(element, xmlposition)
        else:
            # We insert it in the last office:text
            content = self.__get_xmlpart('content')
            # FIXME hardcoded odt body element
            office_text = content.get_element_list('//office:text')[-1]
            office_text.insert_element(element, LAST_CHILD)


    def insert_element(self, element, context=None, xmlposition=LAST_CHILD,
                       offset=0):

        # Search the good method to insert the element
        qname = element.get_name()

        # => An image
        if qname == 'draw:image':
            self.__insert_image(element, context, xmlposition, offset)

        # => With these elements, the context cannot be None
        elif qname in ('table:table-column', 'table:table-row',
                       'table:table-cell', 'text:list-item',
                       'style:text-properties'):
            if context is None:
                raise TypeError, ('insertion of "%s": context cannot be None'
                                  % qname)
            self.__insert_element(element, context, xmlposition, offset)

        # => 'In paragraph' elements
        # Offset is the position in the paragraph where the element is
        # inserted. Hence the context is mandatory and the XML position makes
        # no sense.
        elif qname in ('text:note', 'office:annotation'):
            if context is None:
                raise TypeError, ('insertion of "%s": context cannot be None'
                                  % qname)
            text = context.get_text()
            before, after = text[:offset], text[offset:]
            context.set_text(before)
            context.insert_element(element, xmlposition=LAST_CHILD)
            element.set_text(after, after=True)

        # => Styles
        elif qname == 'style:style':
            _check_arguments(element=element)
            styles = self.__get_xmlpart('styles')
            office_styles = styles.get_element('//office:styles')
            office_styles.insert_element(element, LAST_CHILD)

        # => Generic insert
        else:
            self.__insert_element(element, context, xmlposition, offset)


    def clone(self):
        """Return an exact copy of the document.
        Return: odf_document
        """
        clone = object.__new__(self.__class__)
        for name in self.__dict__:
            if name == 'container':
                setattr(clone, name, self.container.clone())
            elif name == '_odf_document__xmlparts':
                # TODO odf_xmlpart.clone
                setattr(clone, name, {})
            else:
                value = getattr(self, name)
                value = deepcopy(value)
                setattr(clone, name, value)
        return clone


    def save(self, uri=None, packaging=None, pretty=False):
        """Save the document, at the same place it was opened or at the given
        URI. It can be saved as a Zip file or as a plain XML file. The XML
        can be pretty printed.
        Arguments:

            uri -- str
            packaging -- 'zip' or 'flat'
            pretty -- bool
        """
        # Synchronize data with container
        for part_name, part in self.__xmlparts.items():
            if part is not None:
                self.container.set_part(part_name, part.serialize(pretty))

        # Save the container
        self.container.save(uri, packaging)


    #
    # Sections
    #

    def get_section_list(self, style=None, context=None):
        return self.__get_element_list('text:section', style=style,
                                       context=context)


    def get_section(self, position, context=None):
        return self.__get_element('text:section', position, context=context)


    #
    # Paragraphs
    #

    def get_paragraph_list(self, style=None, context=None):
        return self.__get_element_list('text:p', style=style,
                                       context=context)


    def get_paragraph(self, position, context=None):
        return self.__get_element('text:p', position, context=context)


    #
    # Headings
    #

    def get_heading_list(self, style=None, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element_list('text:h', style=style,
                                       attributes=attributes,
                                       context=context)


    def get_heading(self, position, level=None, context=None):
        if level is not None:
            _check_arguments(level=level)
            attributes = {'text:outline-level': level}
        else:
            attributes = None
        return self.__get_element('text:h', position, attributes=attributes,
                                  context=context)


    #
    # Frames
    #

    def get_frame_list(self, style=None, context=None):
        return self.__get_element_list('draw:frame', frame_style=style,
                                       context=context)


    def get_frame(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'draw:name': name} if name is not None else {}
        return self.__get_element('draw:frame', position,
                                  attributes=attributes,
                                  context=context)


    #
    # Images
    #

    def __insert_image(self, element, context, xmlposition, offset):
        # XXX If context is None
        #     => auto create a frame with the good dimensions
        if context is None:
            raise NotImplementedError

        self.__insert_element(element, context, xmlposition, offset)


    def get_image(self, position=None, name=None, context=None):
        # Automatically get the frame
        frame = self.get_frame(position, name, context)
        return self.__get_element('draw:image', context=frame)


    #
    # Tables
    #

    def get_table_list(self, style=None, context=None):
        return self.__get_element_list('table:table', style=style,
                                       context=context)


    def get_table(self, position=None, name=None, context=None):
        _check_position_or_name(position, name)
        attributes = {'table:name': name} if name is not None else {}
        return self.__get_element('table:table', position,
                                  attributes=attributes, context=context)


    def get_row_list(self, style=None, context=None):
        return self.__get_element_list('table:table-row', style=style,
                                       context=context)


    #
    # Cells
    #

    def get_cell_list(self, style=None, context=None):
        return self.__get_element_list('table:table-cell', style=style,
                                       context=context)


    # Warning: This function gives just a "read only" odf_element
    def get_cell(self, name, context):
        # The coordinates of your cell
        x, y = _get_cell_coordinates(name)

        # First, we must find the good row
        cell_y = 0
        for row in self.get_row_list(context=context):
            repeat = row.get_attribute('table:number-rows-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_y + 1 <= y and y <= (cell_y + repeat):
                break
            cell_y += repeat
        else:
            raise IndexError, 'I cannot find cell "%s"' % name

        # Second, we must find the good cell
        cell_x = 0
        for cell in self.get_cell_list(context=row):
            repeat = cell.get_attribute('table:number-columns-repeated')
            repeat = int(repeat) if repeat is not None else 1
            if cell_x + 1 <= x and x <= (cell_x + repeat):
                break
            cell_x += repeat
        else:
            raise IndexError, 'i cannot find your cell "%s"' % name

        return cell


    #
    # Notes
    #

    def get_note_list(self, note_class=None, context=None):
        _check_arguments(note_class=note_class)
        if note_class is not None:
            attributes = {'text:note-class': note_class}
        else:
            attributes = None
        return self.__get_element_list('text:note', attributes=attributes,
                                       context=context)


    def get_note(self, id, context=None):
        attributes = {'text:id': id}
        return self.__get_element('text:note', attributes=attributes,
                                  context=context)


    def insert_note_body(self, element, context):
        body = context.get_element_list('//text:note-body')[-1]
        body.insert_element(element, LAST_CHILD)


    #
    # Annotations
    #

    def get_annotation_list(self, creator=None, start_date=None,
                            end_date=None, context=None):
        """XXX end date is not included (as expected in Python).
        """
        _check_arguments(creator=creator, start_date=start_date,
                         end_date=end_date)
        annotations = []
        for annotation in self.__get_element_list('office:annotation',
                                                  context=context):
            if creator is not None and creator != annotation.get_creator():
                continue
            date = annotation.get_date()
            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date >= end_date:
                continue
            annotations.append(annotation)
        return annotations


    def get_annotation(self, creator=None, start_date=None, end_date=None,
                       context=None):
        annotations = self.get_annotation_list(creator=creator,
                start_date=start_date, end_date=end_date, context=context)
        if not annotations:
            return None
        return annotations[0]


    #
    # Styles
    #

    def get_style_list(self, family=None, context=None):
        _check_arguments(family=family, context=context)
        attributes = {}
        if family is not None:
            attributes['style:family'] = family
        return (self.__get_element_list('style:style', attributes=attributes,
                                        context=context, part='content')
                + self.__get_element_list('style:style',
                                          attributes=attributes,
                                          context=context, part='styles'))


    def get_style(self, name, family=None):
        _check_arguments(family=family)
        attributes = {'style:name': name}
        if family is not None:
            attributes['style:family'] = family
        # 1. content
        element = self.__get_element('style:style', attributes=attributes,
                                     part='content')
        if element is not None:
            return element
        # 2. styles
        return self.__get_element('style:style', attributes=attributes,
                                  part='styles')


    #
    # Metadata
    #

    def get_title(self):
        """Get the title of the document.
        Return: unicode (or None if inexistant)

        This is not the first heading but the title metadata.
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:title')
        if element is None:
            return None
        title = element.get_text()
        return unicode(title, 'utf_8')


    def set_title(self, title):
        """Set the title of the document.
        Arguments:

            title -- unicode

        This is not the first heading but the title metadata.
        """
        _check_arguments(text=title)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:title')
        if element is None:
            raise NotImplementedError
        title = title.encode('utf_8')
        element.set_text(title)


    def get_description(self):
        """Get the description of the document.
        Return: unicode (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:description')
        if element is None:
            return None
        description = element.get_text()
        return unicode(description, 'utf_8')


    def set_description(self, description):
        """Set the title of the document.
        Arguments:

            description -- unicode
        """
        _check_arguments(text=description)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:description')
        if element is None:
            raise NotImplementedError
        description = description.encode('utf_8')
        element.set_text(description)


    def get_subject(self):
        """Get the subject of the document.
        Return: unicode (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:subject')
        if element is None:
            return None
        subject = element.get_text()
        return unicode(subject, 'utf_8')


    def set_subject(self, subject):
        """Set the subject of the document.
        Arguments:

            subject -- unicode
        """
        _check_arguments(text=subject)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:subject')
        if element is None:
            raise NotImplementedError
        subject = subject.encode('utf_8')
        element.set_text(subject)


    def get_language(self):
        """Get the language code of the document.
        Return: str (or None if inexistant)

        Example::

            >>> document.get_language()
            >>> 'fr-FR'
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:language')
        if element is None:
            return None
        return element.get_text()


    def set_language(self, language):
        """Set the language code of the document.
        Arguments:

            language -- str

        Example::

            >>> document.set_language('fr-FR')
        """
        if type(language) is not str:
            raise TypeError, ('language must be "xx-YY" lang-COUNTRY code '
                              '(RFC3066)')
        # FIXME test validity?
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:language')
        if element is None:
            raise NotImplementedError
        element.set_text(language)


    def get_modification_date(self):
        """Get the last modified date of the document.
        Return: datetime (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:date')
        if element is None:
            return None
        date = element.get_text()
        return DateTime.decode(date)


    def set_modification_date(self, date):
        """Set the last modified date of the document.
        Arguments:

            date -- datetime
        """
        _check_arguments(date=date)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//dc:date')
        if element is None:
            raise NotImplementedError
        date = DateTime.encode(date)
        element.set_text(date)


    def get_creation_date(self):
        """Get the creation date of the document.
        Return: datetime (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:creation-date')
        if element is None:
            return None
        date = element.get_text()
        return DateTime.decode(date)


    def set_creation_date(self, date):
        """Set the creation date of the document.
        Arguments:

            date -- datetime
        """
        _check_arguments(date=date)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:creation-date')
        if element is None:
            raise NotImplementedError
        date = DateTime.encode(date)
        element.set_text(date)


    def get_initial_creator(self):
        """Get the first creator of the document.
        Return: unicode (or None if inexistant)

        Example::

            >>> document.get_initial_creator()
            >>> u"Unknown"
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:initial-creator')
        if element is None:
            return None
        creator = element.get_text()
        return unicode(creator, 'utf_8')


    def set_initial_creator(self, creator):
        """Set the first creator of the document.
        Arguments:

            creator -- unicode

        Example::

            >>> document.set_initial_creator(u"Plato")
        """
        _check_arguments(text=creator)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:initial-creator')
        if element is None:
            raise NotImplementedError
        creator = creator.encode('utf_8')
        element.set_text(creator)


    def get_keyword(self):
        """Get the keyword(s) of the document.
        Return: unicode (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:keyword')
        if element is None:
            return None
        keyword = element.get_text()
        return unicode(keyword, 'utf_8')


    def set_keyword(self, keyword):
        """Set the keyword(s) of the document.
        Arguments:

            keyword -- unicode
        """
        _check_arguments(text=keyword)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:keyword')
        if element is None:
            raise NotImplementedError
        keyword = keyword.encode('utf_8')
        element.set_text(keyword)


    def get_editing_duration(self):
        """Get the time the document was edited, as reported by the generator.
        Return: timedelta (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:editing-duration')
        if element is None:
            return None
        duration = element.get_text()
        return Duration.decode(duration)


    def set_editing_duration(self, duration):
        """Set the time the document was edited.
        Arguments:
        duration -- timedelta
        """
        if type(duration) is not timedelta:
            raise TypeError, u"duration must be a timedelta"
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:editing-duration')
        if element is None:
            raise NotImplementedError
        duration = Duration.encode(duration)
        element.set_text(duration)


    def get_editing_cycles(self):
        """Get the number of times the document was edited, as reported by the
        generator.
        Return: int (or None if inexistant)
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:editing-cycles')
        if element is None:
            return None
        cycles = element.get_text()
        return int(cycles)


    def set_editing_cycles(self, cycles):
        """Set the number of times the document was edited.
        Arguments:

            cycles -- int
        """
        if type(cycles) is not int:
            raise TypeError, u"cycles must be an int"
        if cycles < 1:
            raise ValueError, "cycles must be a positive int"
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:editing-cycles')
        if element is None:
            raise NotImplementedError
        cycles = str(cycles)
        element.set_text(cycles)


    def get_generator(self):
        """Get the signature of the software that generated this document.
        Return: unicode (or None if inexistant)

        Example::

            >>> document.get_generator()
            >>> u"KOffice/2.0.0"
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:generator')
        if element is None:
            return None
        generator = element.get_text()
        return unicode(generator, 'utf_8')


    def set_generator(self, generator):
        """Set the signature of the software that generated this document.
        Arguments:

            generator -- unicode

        Example::

            >>> document.set_generator(u"lpOD Project")
        """
        _check_arguments(text=generator)
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:generator')
        if element is None:
            raise NotImplementedError
        generator = generator.encode('utf_8')
        element.set_text(generator)


    def get_statistic(self):
        """Get the statistic from the software that generated this document.
        Return: dict (or None if inexistant)

        Example::

            >>> document.get_statistic():
            {'meta:table-count': 1,
             'meta:image-count': 2,
             'meta:object-count': 3,
             'meta:page-count': 4,
             'meta:paragraph-count': 5,
             'meta:word-count': 6,
             'meta:character-count': 7}
        """
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:document-statistic')
        if element is None:
            return None
        statistic = {}
        for key, value in element.get_attributes().iteritems():
            statistic[key] = int(value)
        return statistic


    def set_statistic(self, statistic):
        """Set the statistic for the documents: number of words, paragraphs,
        etc.
        Arguments:

            statistic -- dict

        Example::

            >>> statistic = {'meta:table-count': 1,
                             'meta:image-count': 2,
                             'meta:object-count': 3,
                             'meta:page-count': 4,
                             'meta:paragraph-count': 5,
                             'meta:word-count': 6,
                             'meta:character-count': 7}
            >>> document.set_statistic(statistic)
        """
        if type(statistic) is not dict:
            raise TypeError, "statistic must be a dict"
        meta = self.__get_xmlpart('meta')
        element = meta.get_element('//meta:document-statistic')
        for key, value in statistic.get_attributes().iteritems():
            if type(key) is not str:
                raise TypeError, "statistic key must be a str"
            if type(value) is not int:
                raise TypeError, "statistic value must be a int"
            element.set_attribute(key, str(value))



#
# odf_document factories
#

def odf_get_document(uri):
    """Return an "odf_document" instance of the ODF document stored at the
    given URI.

    Example::

        >>> uri = 'uri://of/a/document.odt'
        >>> document = odf_get_document(uri)
    """
    container = odf_get_container(uri)
    return odf_document(container)



def odf_new_document_from_template(template_uri):
    """Return an "odf_document" instance using the given template.

    Example::

        >>> uri = 'uri://of/a/template.ott'
        >>> document = odf_new_document_from_template(uri)
    """
    container = odf_new_container_from_template(template_uri)
    return odf_document(container)



def odf_new_document_from_class(odf_class):
    """Return an "odf_document" instance of the given class.
    Arguments:

        odf_class -- 'text', 'spreadsheet', 'presentation' or 'drawing'

    Example::

        >>> document = odf_new_document_from_class('spreadsheet')
    """
    container = odf_new_container_from_class(odf_class)
    return odf_document(container)
