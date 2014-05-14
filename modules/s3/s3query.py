# -*- coding: utf-8 -*-

""" S3 Query Construction

    @copyright: 2009-2014 (c) Sahana Software Foundation
    @license: MIT

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.
"""

import datetime
import re
import sys

from gluon import current
from gluon.dal import Row, Field
from gluon.storage import Storage

from s3fields import S3RepresentLazy
from s3utils import s3_get_foreign_key, s3_unicode, S3TypeConverter

ogetattr = object.__getattribute__

TEXTTYPES = ("string", "text")

# =============================================================================
class S3FieldSelector(object):
    """ Helper class to construct a resource query """

    LOWER = "lower"
    UPPER = "upper"

    OPERATORS = [LOWER, UPPER]

    def __init__(self, name, type=None):
        """ Constructor """

        if not isinstance(name, basestring) or not name:
            raise SyntaxError("name required")
        self.name = str(name)
        self.type = type

        self.op = None

    # -------------------------------------------------------------------------
    def __lt__(self, value):
        return S3ResourceQuery(S3ResourceQuery.LT, self, value)

    # -------------------------------------------------------------------------
    def __le__(self, value):
        return S3ResourceQuery(S3ResourceQuery.LE, self, value)

    # -------------------------------------------------------------------------
    def __eq__(self, value):
        return S3ResourceQuery(S3ResourceQuery.EQ, self, value)

    # -------------------------------------------------------------------------
    def __ne__(self, value):
        return S3ResourceQuery(S3ResourceQuery.NE, self, value)

    # -------------------------------------------------------------------------
    def __ge__(self, value):
        return S3ResourceQuery(S3ResourceQuery.GE, self, value)

    # -------------------------------------------------------------------------
    def __gt__(self, value):
        return S3ResourceQuery(S3ResourceQuery.GT, self, value)

    # -------------------------------------------------------------------------
    def like(self, value):
        return S3ResourceQuery(S3ResourceQuery.LIKE, self, value)

    # -------------------------------------------------------------------------
    def belongs(self, value):
        return S3ResourceQuery(S3ResourceQuery.BELONGS, self, value)

    # -------------------------------------------------------------------------
    def contains(self, value):
        return S3ResourceQuery(S3ResourceQuery.CONTAINS, self, value)

    # -------------------------------------------------------------------------
    def anyof(self, value):
        return S3ResourceQuery(S3ResourceQuery.ANYOF, self, value)

    # -------------------------------------------------------------------------
    def typeof(self, value):
        return S3ResourceQuery(S3ResourceQuery.TYPEOF, self, value)

    # -------------------------------------------------------------------------
    def lower(self):
        self.op = self.LOWER
        return self

    # -------------------------------------------------------------------------
    def upper(self):
        self.op = self.UPPER
        return self

    # -------------------------------------------------------------------------
    def expr(self, val):

        if self.op and val is not None:
            if self.op == self.LOWER and \
               hasattr(val, "lower") and callable(val.lower) and \
               (not isinstance(val, Field) or val.type in TEXTTYPES):
                return val.lower()
            elif self.op == self.UPPER and \
                 hasattr(val, "upper") and callable(val.upper) and \
                 (not isinstance(val, Field) or val.type in TEXTTYPES):
                return val.upper()
        return val

    # -------------------------------------------------------------------------
    def represent(self, resource):

        try:
            rfield = S3ResourceField(resource, self.name)
        except:
            colname = None
        else:
            colname = rfield.colname
        if colname:
            if self.op is not None:
                return "%s.%s()" % (colname, self.op)
            else:
                return colname
        else:
            return "(%s?)" % self.name

    # -------------------------------------------------------------------------
    @classmethod
    def extract(cls, resource, row, field):
        """
            Extract a value from a Row

            @param resource: the resource
            @param row: the Row
            @param field: the field

            @return: field if field is not a Field/S3FieldSelector instance,
                      the value from the row otherwise
        """

        error = lambda fn: KeyError("Field not found: %s" % fn)

        t = type(field)

        if isinstance(field, Field):
            colname = str(field)
            tname, fname = colname.split(".", 1)

        elif t is S3FieldSelector:
            rfield = S3ResourceField(resource, field.name)
            colname = rfield.colname
            if not colname:
                # unresolvable selector
                raise error(field.name)
            fname = rfield.fname
            tname = rfield.tname

        elif t is S3ResourceField:
            colname = field.colname
            if not colname:
                # unresolved selector
                return None
            fname = field.fname
            tname = field.tname

        else:
            return field

        if type(row) is Row:
            try:
                if tname in row.__dict__:
                    value = ogetattr(ogetattr(row, tname), fname)
                else:
                    value = ogetattr(row, fname)
            except:
                try:
                    value = row[colname]
                except (KeyError, AttributeError):
                    raise error(colname)
        elif fname in row:
            value = row[fname]
        elif colname in row:
            value = row[colname]
        elif tname is not None and \
             tname in row and fname in row[tname]:
            value = row[tname][fname]
        else:
            raise error(colname)

        if callable(value):
            # Lazy virtual field
            try:
                value = value()
            except:
                current.log.error(sys.exc_info()[1])
                value = None

        if hasattr(field, "expr"):
            return field.expr(value)
        return value

    # -------------------------------------------------------------------------
    def resolve(self, resource):
        """
            Resolve this field against a resource

            @param resource: the resource
        """
        return S3ResourceField(resource, self.name)

# =============================================================================
# Short name for the S3FieldSelector class
#
FS = S3FieldSelector

# =============================================================================
class S3FieldPath(object):
    """ Helper class to parse field selectors """

    # -------------------------------------------------------------------------
    @classmethod
    def resolve(cls, resource, selector, tail=None):
        """
            Resolve a selector (=field path) against a resource

            @param resource: the S3Resource to resolve against
            @param selector: the field selector string
            @param tail: tokens to append to the selector

            The general syntax for a selector is:

            selector = {[alias].}{[key]$}[field|selector]

            (Parts in {} are optional, | indicates alternatives)

            * Alias can be:

            ~           refers to the resource addressed by the
                        preceding parts of the selector (=last
                        resource)
            component   alias of a component of the last resource
            linktable   alias of a link table of the last resource
            table       name of a table that has a foreign key for
                        the last resource (auto-detect the key)
            key:table   same as above, but specifying the foreign key

            * Key can be:

            key         the name of a foreign key in the last resource
            context     a context expression

            * Field can be:

            fieldname   the name of a field or virtual field of the
                        last resource
            context     a context expression

            A "context expression" is a name enclosed in parentheses:

            (context)

            During parsing, context expressions get replaced by the
            string which has been configured for this name for the
            last resource with:

            s3db.configure(tablename, context = dict(name = "string"))

            With context expressions, the same selector can be used
            for different resources, each time resolving into the
            specific field path. However, the field addressed must
            be of the same type in all resources to form valid
            queries.

            If a context name can not be resolved, resolve() will
            still succeed - but the S3FieldPath returned will have
            colname=None and ftype="context" (=unresolvable context).
        """

        if not selector:
            raise SyntaxError("Invalid selector: %s" % selector)
        tokens = re.split("(\.|\$)", selector)
        if tail:
            tokens.extend(tail)
        parser = cls(resource, None, tokens)
        parser.original = selector
        return parser

    # -------------------------------------------------------------------------
    def __init__(self, resource, table, tokens):
        """
            Constructor - not to be called directly, use resolve() instead

            @param resource: the S3Resource
            @param table: the table
            @param tokens: the tokens as list
        """

        s3db = current.s3db

        if table is None:
            table = resource.table

        # Initialize
        self.original = None
        self.tname = table._tablename
        self.fname = None
        self.field = None
        self.ftype = None
        self.virtual = False
        self.colname = None
        self.left = Storage()
        self.join = Storage()

        self.distinct = False
        self.multiple = True

        head = tokens.pop(0)
        tail = None

        if head and head[0] == "(" and head[-1] == ")":

            # Context expression
            head = head.strip("()")
            self.fname = head
            self.ftype = "context"

            if not resource:
                resource = s3db.resource(table, components=[])
            context = resource.get_config("context")
            if context and head in context:
                tail = self.resolve(resource, context[head], tail=tokens)
            else:
                # unresolvable
                pass

        elif tokens:

            # Resolve the tail
            op = tokens.pop(0)
            if tokens:
                if op == ".":
                    # head is a component or linktable alias, and tokens is
                    # a field expression in the component/linked table
                    if not resource:
                        resource = s3db.resource(table, components=[])
                    ktable, j, l, m, d = self._resolve_alias(resource, head)
                    if j is not None and l is not None:
                        self.join[ktable._tablename] = j
                        self.left[ktable._tablename] = l
                    self.multiple = m
                    self.distinct = d
                    tail = S3FieldPath(None, ktable, tokens)

                else:
                    # head is a foreign key in the current table and tokens is
                    # a field expression in the referenced table
                    ktable, join, left = self._resolve_key(table, head)
                    if join is not None and left is not None:
                        self.join[ktable._tablename] = join
                        self.left[ktable._tablename] = left
                    tail = S3FieldPath(None, ktable, tokens)
                    self.distinct = True
            else:
                raise SyntaxError("trailing operator")

        if tail is None:

            # End of the expression
            if self.ftype != "context":
                # Expression is resolved, head is a field name:
                self.field = self._resolve_field(table, head)
                if not self.field:
                    self.virtual = True
                    self.ftype = "virtual"
                else:
                    self.virtual = False
                    self.ftype = str(self.field.type)
                self.fname = head
                self.colname = "%s.%s" % (self.tname, self.fname)

        else:

            # Read field data from tail
            self.tname = tail.tname
            self.fname = tail.fname
            self.field = tail.field
            self.ftype = tail.ftype
            self.virtual = tail.virtual
            self.colname = tail.colname

            self.distinct |= tail.distinct
            self.multiple |= tail.multiple

            self.join.update(tail.join)
            self.left.update(tail.left)

    # -------------------------------------------------------------------------
    @staticmethod
    def _resolve_field(table, fieldname):
        """
            Resolve a field name against the table, recognizes "id" as
            table._id.name, and "uid" as current.xml.UID.

            @param table: the Table
            @param fieldname: the field name

            @return: the Field
        """

        if fieldname == "uid":
            fieldname = current.xml.UID
        if fieldname == "id":
            field = table._id
        elif fieldname in table.fields:
            field = ogetattr(table, fieldname)
        else:
            field = None
        return field

    # -------------------------------------------------------------------------
    @staticmethod
    def _resolve_key(table, fieldname):
        """
            Resolve a foreign key into the referenced table and the
            join and left join between the current table and the
            referenced table

            @param table: the current Table
            @param fieldname: the fieldname of the foreign key

            @return: tuple of (referenced table, join, left join)
            @raise: AttributeError is either the field or
                    the referended table are not found
            @raise: SyntaxError if the field is not a foreign key
        """

        if fieldname in table.fields:
            f = table[fieldname]
        else:
            raise AttributeError("key not found: %s" % fieldname)

        ktablename, pkey, multiple = s3_get_foreign_key(f, m2m=False)

        if not ktablename:
            raise SyntaxError("%s is not a foreign key" % f)

        ktable = current.s3db.table(ktablename,
                                    AttributeError("undefined table %s" % ktablename),
                                    db_only=True)

        pkey = ktable[pkey] if pkey else ktable._id

        join = (f == pkey)
        left = [ktable.on(join)]

        return ktable, join, left

    # -------------------------------------------------------------------------
    @staticmethod
    def _resolve_alias(resource, alias):
        """
            Resolve a table alias into the linked table (component, linktable
            or free join), and the joins and left joins between the current
            resource and the linked table.

            @param resource: the current S3Resource
            @param alias: the alias

            @return: tuple of (linked table, joins, left joins, multiple,
                     distinct), the two latter being flags to indicate
                     possible ambiguous query results (needed by the query
                     builder)
            @raise: AttributeError if one of the key fields or tables
                    can not be found
            @raise: SyntaxError if the alias can not be resolved (e.g.
                    because on of the keys isn't a foreign key, points
                    to the wrong table or is ambiguous)
        """

        # Alias for this resource?
        if alias in ("~", resource.alias):
            return resource.table, None, None, False, False

        multiple = True
        s3db = current.s3db

        tablename = resource.tablename

        # Try to attach the component
        if alias not in resource.components and \
           alias not in resource.links:
            _alias = alias
            hook = s3db.get_component(tablename, alias)
            if not hook:
                _alias = s3db.get_alias(tablename, alias)
                if _alias:
                    hook = s3db.get_component(tablename, _alias)
            if hook:
                resource._attach(_alias, hook)

        components = resource.components
        links = resource.links

        if alias in components:

            # Is a component
            component = components[alias]

            ktable = component.table
            join = component.get_join()
            left = component.get_left_join()
            multiple = component.multiple

        elif alias in links:

            # Is a linktable
            link = links[alias]

            ktable = link.table
            join = link.get_join()
            left = link.get_left_join()

        elif "_" in alias:

            # Is a free join
            DELETED = current.xml.DELETED

            table = resource.table
            tablename = resource.tablename

            pkey = fkey = None

            # Find the table
            fkey, kname = (alias.split(":") + [None])[:2]
            if not kname:
                fkey, kname = kname, fkey

            ktable = s3db.table(kname,
                                AttributeError("table not found: %s" % kname),
                                db_only=True)

            if fkey is None:

                # Autodetect left key
                for fname in ktable.fields:
                    tn, key, m = s3_get_foreign_key(ktable[fname], m2m=False)
                    if not tn:
                        continue
                    if tn == tablename:
                        if fkey is not None:
                            raise SyntaxError("ambiguous foreign key in %s" %
                                              alias)
                        else:
                            fkey = fname
                            if key:
                                pkey = key
                if fkey is None:
                    raise SyntaxError("no foreign key for %s in %s" %
                                      (tablename, kname))

            else:

                # Check left key
                if fkey not in ktable.fields:
                    raise AttributeError("no field %s in %s" % (fkey, kname))

                tn, pkey, m = s3_get_foreign_key(ktable[fkey], m2m=False)
                if tn and tn != tablename:
                    raise SyntaxError("%s.%s is not a foreign key for %s" %
                                      (kname, fkey, tablename))
                elif not tn:
                    raise SyntaxError("%s.%s is not a foreign key" %
                                      (kname, fkey))

            # Default primary key
            if pkey is None:
                pkey = table._id.name

            # Build join
            join = (table[pkey] == ktable[fkey])
            if DELETED in ktable.fields:
                join &= ktable[DELETED] != True
            left = [ktable.on(join)]

        else:
            raise SyntaxError("Invalid tablename: %s" % alias)

        return ktable, join, left, multiple, True

# =============================================================================
class S3ResourceField(object):
    """ Helper class to resolve a field selector against a resource """

    # -------------------------------------------------------------------------
    def __init__(self, resource, selector, label=None):
        """
            Constructor

            @param resource: the resource
            @param selector: the field selector (string)
        """

        self.resource = resource
        self.selector = selector

        lf = S3FieldPath.resolve(resource, selector)

        self.tname = lf.tname
        self.fname = lf.fname
        self.colname = lf.colname

        self.join = lf.join
        self.left = lf.left
        self.distinct = lf.distinct
        self.multiple = lf.multiple

        self.field = lf.field

        self.virtual = False
        self.represent = s3_unicode
        self.requires = None

        if self.field is not None:
            field = self.field
            self.ftype = str(field.type)
            if resource.linked is not None and self.ftype == "id":
                # Always represent the link-table's ID as the
                # linked record's ID => needed for data tables
                self.represent = lambda i, resource=resource: \
                                           resource.component_id(None, i)
            else:
                self.represent = field.represent
            self.requires = field.requires
        elif self.colname:
            self.virtual = True
            self.ftype = "virtual"
        else:
            self.ftype = "context"

        # Fall back to the field label
        if label is None:
            fname = self.fname
            if fname in ["L1", "L2", "L3", "L3", "L4", "L5"]:
                try:
                    label = current.gis.get_location_hierarchy(fname)
                except:
                    label = None
            elif fname == "L0":
                label = current.messages.COUNTRY
            if label is None:
                f = self.field
                if f:
                    label = f.label
                elif fname:
                    label = " ".join([s.strip().capitalize()
                                      for s in fname.split("_") if s])
                else:
                    label = None

        self.label = label
        self.show = True

    # -------------------------------------------------------------------------
    def __repr__(self):
        """ String representation of this instance """

        return "<S3ResourceField " \
               "selector='%s' " \
               "label='%s' " \
               "table='%s' " \
               "field='%s' " \
               "type='%s'>" % \
               (self.selector, self.label, self.tname, self.fname, self.ftype)

    # -------------------------------------------------------------------------
    def extract(self, row, represent=False, lazy=False):
        """
            Extract the value for this field from a row

            @param row: the Row
            @param represent: render a text representation for the value
            @param lazy: return a lazy representation handle if available
        """

        tname = self.tname
        fname = self.fname
        colname = self.colname
        error = "Field not found in Row: %s" % colname

        if type(row) is Row:
            try:
                if tname in row.__dict__:
                    value = ogetattr(ogetattr(row, tname), fname)
                else:
                    value = ogetattr(row, fname)
            except:
                try:
                    value = row[colname]
                except (KeyError, AttributeError):
                    raise KeyError(error)
        elif fname in row:
            value = row[fname]
        elif colname in row:
            value = row[colname]
        elif tname is not None and \
             tname in row and fname in row[tname]:
            value = row[tname][fname]
        else:
            raise KeyError(error)

        if callable(value):
            # Lazy virtual field
            try:
                value = value()
            except:
                current.log.error(sys.exc_info()[1])
                value = None

        if represent:
            renderer = self.represent
            if callable(renderer):
                if lazy and hasattr(renderer, "bulk"):
                    return S3RepresentLazy(value, renderer)
                else:
                    return renderer(value)
            else:
                return s3_unicode(value)
        else:
            return value

# =============================================================================
class S3LeftJoins(object):

    def __init__(self, tablename, joins=None):
        """
            Constructor

            @param tablename: the tablename
            @param joins: list of left joins
        """

        self.tablename = tablename
        self.joins = {}
        self.tables = []

        self.add(joins)

    # -------------------------------------------------------------------------
    def __iter__(self):

        return self.joins.__iter__()

    # -------------------------------------------------------------------------
    def __getitem__(self, key):

        return self.joins.__getitem__(key)

    # -------------------------------------------------------------------------
    def __setitem__(self, key, value):

        tablename = self.tablename
        joins = self.joins
        tables = current.db._adapter.tables

        joins[key] = value
        if len(value) > 1:
            for join in value:
                try:
                    tname = join.first._tablename
                except AttributeError:
                    tname = str(join.first)
                if tname not in joins and \
                   tablename in tables(join.second):
                    joins[tname] = [join]
        self.tables.append(key)
        return

    # -------------------------------------------------------------------------
    def keys(self):

        return self.joins.keys()

    # -------------------------------------------------------------------------
    def items(self):

        return self.joins.items()

    # -------------------------------------------------------------------------
    def values(self):

        return self.joins.values()

    # -------------------------------------------------------------------------
    def add(self, joins):

        tablenames = []
        if joins:
            if not isinstance(joins, (list, tuple)):
                joins = [joins]
            for join in joins:
                tablename = join.first._tablename
                self[tablename] = [join]
                tablenames.append(tablename)
        return tablenames

    # -------------------------------------------------------------------------
    def extend(self, other):

        if type(other) is S3LeftJoins:
            append = self.tables.append
        else:
            append = None
        joins = self.joins if type(other) is S3LeftJoins else self
        for tablename in other:
            if tablename not in self.joins:
                joins[tablename] = other[tablename]
                if append:
                    append(tablename)
        return other.keys()

    # -------------------------------------------------------------------------
    def __repr__(self):

        return "<S3LeftJoins %s>" % str([str(j) for j in self.as_list()])

    # -------------------------------------------------------------------------
    def as_list(self, tablenames=None, aqueries=None):

        accessible_query = current.auth.s3_accessible_query

        if tablenames is None:
            tablenames = set(self.tables)
        else:
            tablenames = set(tablenames)

        joins = self.joins

        # Resolve dependencies
        required_tables = set()
        get_tables = current.db._adapter.tables
        for tablename in tablenames:
            if tablename not in joins or tablename == self.tablename:
                continue
            required_tables.add(tablename)
            for join in joins[tablename]:
                dependencies = get_tables(join.second)
                if dependencies:
                    required_tables |= set(dependencies)

        # Collect joins
        joins_dict = {}
        for tablename in required_tables:
            if tablename not in joins or tablename == self.tablename:
                continue
            for join in joins[tablename]:
                j = join
                table = j.first
                tname = table._tablename
                if aqueries is not None and tname in tablenames:
                    if tname not in aqueries:
                        aquery = accessible_query("read", table)
                        aqueries[tname] = aquery
                    else:
                        aquery = aqueries[tname]
                    if aquery is not None:
                        j = join.first.on(join.second & aquery)
                joins_dict[tname] = j

        # Sort joins (if possible)
        try:
            return self.sort(joins_dict.values())
        except RuntimeError:
            return joins_dict.values()

    # -------------------------------------------------------------------------
    @classmethod
    def sort(cls, joins):
        """
            Sort a list of left-joins by their interdependency

            @param joins: the list of joins
        """

        if len(joins) <= 1:
            return joins
        r = list(joins)

        tables = current.db._adapter.tables

        append = r.append
        head = None
        for i in xrange(len(joins)):
            join = r.pop(0)
            head = join
            tablenames = tables(join.second)
            for j in r:
                try:
                    tn = j.first._tablename
                except AttributeError:
                    tn = str(j.first)
                if tn in tablenames:
                    head = None
                    break
            if head is not None:
                break
            else:
                append(join)
        if head is not None:
            return [head] + cls.sort(r)
        else:
            raise RuntimeError("circular left-join dependency")

# =============================================================================
class S3ResourceQuery(object):
    """
        Helper class representing a resource query
        - unlike DAL Query objects, these can be converted to/from URL filters
    """

    # Supported operators
    NOT = "not"
    AND = "and"
    OR = "or"
    LT = "lt"
    LE = "le"
    EQ = "eq"
    NE = "ne"
    GE = "ge"
    GT = "gt"
    LIKE = "like"
    BELONGS = "belongs"
    CONTAINS = "contains"
    ANYOF = "anyof"
    TYPEOF = "typeof"

    OPERATORS = [NOT, AND, OR,
                 LT, LE, EQ, NE, GE, GT,
                 LIKE, BELONGS, CONTAINS, ANYOF, TYPEOF]

    # -------------------------------------------------------------------------
    def __init__(self, op, left=None, right=None):
        """ Constructor """

        if op not in self.OPERATORS:
            raise SyntaxError("Invalid operator: %s" % op)

        self.op = op

        self.left = left
        self.right = right

    # -------------------------------------------------------------------------
    def __and__(self, other):
        """ AND """

        return S3ResourceQuery(self.AND, self, other)

    # -------------------------------------------------------------------------
    def __or__(self, other):
        """ OR """

        return S3ResourceQuery(self.OR, self, other)

    # -------------------------------------------------------------------------
    def __invert__(self):
        """ NOT """

        if self.op == self.NOT:
            return self.left
        else:
            return S3ResourceQuery(self.NOT, self)

    # -------------------------------------------------------------------------
    def joins(self, resource, left=False):
        """
            Get a Storage {tablename: join} for this query.

            @param resource: the resource to resolve the query against
            @param left: get left joins rather than inner joins
        """

        op = self.op
        l = self.left
        r = self.right

        if op in (self.AND, self.OR):
            ljoins, ld = l.joins(resource, left=left)
            rjoins, rd = r.joins(resource, left=left)
            ljoins = Storage(ljoins)
            ljoins.update(rjoins)
            return (ljoins, ld or rd)
        elif op == self.NOT:
            return l.joins(resource, left=left)
        if isinstance(l, S3FieldSelector):
            try:
                rfield = l.resolve(resource)
            except:
                return (Storage(), False)
            if rfield.distinct:
                if left:
                    return (rfield.left, True)
                else:
                    return (Storage(), True)
            else:
                if left:
                    return (Storage(), False)
                else:
                    return (rfield.join, False)
        return(Storage(), False)

    # -------------------------------------------------------------------------
    def fields(self):
        """ Get all field selectors involved with this query """

        op = self.op
        l = self.left
        r = self.right

        if op in (self.AND, self.OR):
            lf = l.fields()
            rf = r.fields()
            return lf + rf
        elif op == self.NOT:
            return l.fields()
        elif isinstance(l, S3FieldSelector):
            return [l.name]
        else:
            return []

    # -------------------------------------------------------------------------
    def split(self, resource):
        """
            Split this query into a real query and a virtual one (AND)

            @param resource: the S3Resource
            @return: tuple (DAL-translatable sub-query, virtual filter),
                     both S3ResourceQuery instances
        """

        op = self.op
        l = self.left
        r = self.right

        if op == self.AND:
            lq, lf = l.split(resource)
            rq, rf = r.split(resource)
            q = lq
            if rq is not None:
                if q is not None:
                    q &= rq
                else:
                    q = rq
            f = lf
            if rf is not None:
                if f is not None:
                    f &= rf
                else:
                    f = rf
            return q, f
        elif op == self.OR:
            lq, lf = l.split(resource)
            rq, rf = r.split(resource)
            if lf is not None or rf is not None:
                return None, self
            else:
                q = lq
                if rq is not None:
                    if q is not None:
                        q |= rq
                    else:
                        q = rq
                return q, None
        elif op == self.NOT:
            if l.op == self.OR:
                i = (~(l.left)) & (~(l.right))
                return i.split(resource)
            else:
                q, f = l.split(resource)
                if q is not None and f is not None:
                    return None, self
                elif q is not None:
                    return ~q, None
                elif f is not None:
                    return None, ~f

        l = self.left
        try:
            if isinstance(l, S3FieldSelector):
                lfield = l.resolve(resource)
            else:
                lfield = S3ResourceField(resource, l)
        except:
            lfield = None
        if not lfield or lfield.field is None:
            return None, self
        else:
            return self, None

    # -------------------------------------------------------------------------
    def transform(self, resource):
        """
            Placeholder for transformation method

            @param resource: the S3Resource
        """

        # @todo: implement
        return self

    # -------------------------------------------------------------------------
    def query(self, resource):
        """
            Convert this S3ResourceQuery into a DAL query, ignoring virtual
            fields (the necessary joins for this query can be constructed
            with the joins() method)

            @param resource: the resource to resolve the query against
        """

        op = self.op
        l = self.left
        r = self.right

        # Resolve query components
        if op == self.AND:
            l = l.query(resource)
            r = r.query(resource)
            if l is None or r is None:
                return None
            elif l is False or r is False:
                return l if r is False else r if l is False else False
            else:
                return l & r
        elif op == self.OR:
            l = l.query(resource)
            r = r.query(resource)
            if l is None or r is None:
                return None
            elif l is False or r is False:
                return l if r is False else r if l is False else False
            else:
                return l | r
        elif op == self.NOT:
            l = l.query(resource)
            if l is None:
                return None
            elif l is False:
                return False
            else:
                return ~l

        # Resolve the fields
        if isinstance(l, S3FieldSelector):
            try:
                rfield = S3ResourceField(resource, l.name)
            except:
                return None
            if rfield.virtual:
                return None
            elif not rfield.field:
                return False
            lfield = l.expr(rfield.field)
        elif isinstance(l, Field):
            lfield = l
        else:
            return None # not a field at all
        if isinstance(r, S3FieldSelector):
            try:
                rfield = S3ResourceField(resource, r.name)
            except:
                return None
            rfield = rfield.field
            if rfield.virtual:
                return None
            elif not rfield.field:
                return False
            rfield = r.expr(rfield.field)
        else:
            rfield = r

        # Resolve the operator
        invert = False
        query_bare = self._query_bare
        ftype = str(lfield.type)
        if isinstance(rfield, (list, tuple)) and ftype[:4] != "list":
            if op == self.EQ:
                op = self.BELONGS
            elif op == self.NE:
                op = self.BELONGS
                invert = True
            elif op not in (self.BELONGS, self.TYPEOF):
                query = None
                for v in rfield:
                    q = query_bare(op, lfield, v)
                    if q is not None:
                        if query is None:
                            query = q
                        else:
                            query |= q
                return query

        # Convert date(time) strings
        if ftype  == "datetime" and \
           isinstance(rfield, basestring):
            rfield = S3TypeConverter.convert(datetime.datetime, rfield)
        elif ftype  == "date" and \
             isinstance(rfield, basestring):
            rfield = S3TypeConverter.convert(datetime.date, rfield)

        query = query_bare(op, lfield, rfield)
        if invert:
            query = ~(query)
        return query

    # -------------------------------------------------------------------------
    def _query_bare(self, op, l, r):
        """
            Translate a filter expression into a DAL query

            @param op: the operator
            @param l: the left operand
            @param r: the right operand
        """

        if op == self.CONTAINS:
            q = l.contains(r, all=True)
        elif op == self.ANYOF:
            # NB str/int doesn't matter here
            q = l.contains(r, all=False)
        elif op == self.BELONGS:
            q = self._query_belongs(l, r)
        elif op == self.TYPEOF:
            q = self._query_typeof(l, r)
        elif op == self.LIKE:
            q = l.like(s3_unicode(r))
        elif op == self.LT:
            q = l < r
        elif op == self.LE:
            q = l <= r
        elif op == self.EQ:
            q = l == r
        elif op == self.NE:
            q = l != r
        elif op == self.GE:
            q = l >= r
        elif op == self.GT:
            q = l > r
        else:
            q = None
        return q

    # -------------------------------------------------------------------------
    def _query_typeof(self, l, r):
        """
            Translate TYPEOF into DAL expression

            @param l: the left operator
            @param r: the right operator
        """

        ktablename, key, multiple = s3_get_foreign_key(l)
        if not ktablename:
            ktablename = l.tablename

        from s3hierarchy import S3Hierarchy
        hierarchy = S3Hierarchy(ktablename)
        if hierarchy.config is None:
            return self._query_belongs(l, r)

        field = l
        keys = r
            
        if not key:

            ktable = current.s3db[ktablename]
            if l.name != ktable._id.name:
                
                kresource = current.s3db.resource(ktablename)
                fs = S3FieldSelector(l.name)
                if isinstance(r, (list, tuple, set)):
                    expr = fs.belongs(r)
                elif str(l.type) in ("string", "text") and \
                     isinstance(r, basestring):
                    if "*" in r and "%" not in r:
                        s = r.replace("*", "%")
                    else:
                        s = r
                    expr = (fs.like(s)) if "%" in s else (fs == s)
                else:
                    expr = (fs == r)
                subquery = expr.query(kresource)
                if not subquery:
                    return None
                if current.xml.DELETED in ktable.fields:
                    subquery &= ktable[current.xml.DELETED] != True
                rows = current.db(subquery).select(ktable._id)
                keys = set([row[ktable._id.name] for row in rows])

                field = ktable._id

        if keys:
            
            none = False
            if not isinstance(keys, (list, tuple, set)):
                keys = set([keys])
            nodes = set()
            for node in keys:
                if node is None:
                    none = True
                else:
                    try:
                        node_id = long(node)
                    except ValueError:
                        continue
                    nodes.add(node_id)
            nodeset = hierarchy.findall(nodes, inclusive=True)
            q = field.belongs(nodeset)
            if none:
                q |= (field == None)
        else:
            q = field.belongs(set())
            
        return q

    # -------------------------------------------------------------------------
    def _query_belongs(self, l, r):
        """
            Translate BELONGS into DAL expression

            @param l: the left operator
            @param r: the right operator
        """

        if not isinstance(r, (list, tuple, set)):
            r = [r]
        if None in r:
            _r = [item for item in r if item is not None]
            q = ((l.belongs(_r)) | (l == None))
        else:
            q = l.belongs(r)
        return q

    # -------------------------------------------------------------------------
    def __call__(self, resource, row, virtual=True):
        """
            Probe whether the row matches the query

            @param resource: the resource to resolve the query against
            @param row: the DB row
            @param virtual: execute only virtual queries
        """

        if self.op == self.AND:
            l = self.left(resource, row, virtual=False)
            r = self.right(resource, row, virtual=False)
            if l is None:
                return r
            if r is None:
                return l
            return l and r
        elif self.op == self.OR:
            l = self.left(resource, row, virtual=False)
            r = self.right(resource, row, virtual=False)
            if l is None:
                return r
            if r is None:
                return l
            return l or r
        elif self.op == self.NOT:
            l = self.left(resource, row)
            if l is None:
                return None
            else:
                return not l

        real = False
        left = self.left
        if isinstance(left, S3FieldSelector):
            try:
                lfield = left.resolve(resource)
            except (AttributeError, KeyError, SyntaxError):
                return None
            if lfield.field is not None:
                real = True
            elif not lfield.virtual:
                # Unresolvable expression => skip
                return None
        else:
            lfield = left
            if isinstance(left, Field):
                real = True
        right = self.right
        if isinstance(right, S3FieldSelector):
            try:
                rfield = right.resolve(resource)
            except (AttributeError, KeyError, SyntaxError):
                return None
            if rfield.virtual:
                real = False
            elif rfield.field is None:
                # Unresolvable expression => skip
                return None
        else:
            rfield = right
        if virtual and real:
            return None

        extract = lambda f: S3FieldSelector.extract(resource, row, f)
        try:
            l = extract(lfield)
            r = extract(rfield)
        except (KeyError, SyntaxError):
            current.log.error(sys.exc_info()[1])
            return None

        if isinstance(left, S3FieldSelector):
            l = left.expr(l)
        if isinstance(right, S3FieldSelector):
            r = right.expr(r)

        op = self.op
        invert = False
        probe = self._probe
        if isinstance(rfield, (list, tuple)) and \
           not isinstance(lfield, (list, tuple)):
            if op == self.EQ:
                op = self.BELONGS
            elif op == self.NE:
                op = self.BELONGS
                invert = True
            elif op != self.BELONGS:
                for v in r:
                    try:
                        r = probe(op, l, v)
                    except (TypeError, ValueError):
                        r = False
                    if r:
                        return True
                return False
        try:
            r = probe(op, l, r)
        except (TypeError, ValueError):
            return False
        if invert and r is not None:
            return not r
        else:
            return r

    # -------------------------------------------------------------------------
    def _probe(self, op, l, r):
        """
            Probe whether the value pair matches the query

            @param l: the left value
            @param r: the right value
        """

        result = False

        contains = self._contains
        convert = S3TypeConverter.convert
        if op == self.CONTAINS:
            r = convert(l, r)
            result = contains(l, r)
        elif op == self.ANYOF:
            if not isinstance(r, (list, tuple)):
                r = [r]
            for v in r:
                if isinstance(l, (list, tuple, basestring)):
                    if contains(l, v):
                        return True
                elif l == v:
                    return True
            return False
        elif op == self.BELONGS:
            if not isinstance(r, (list, tuple)):
                r = [r]
            r = convert(l, r)
            result = contains(r, l)
        elif op == self.LIKE:
            pattern = re.escape(str(r)).replace("\\%", ".*").replace(".*.*", "\\%")
            return re.match(pattern, str(l)) is not None
        else:
            r = convert(l, r)
            if op == self.LT:
                result = l < r
            elif op == self.LE:
                result = l <= r
            elif op == self.EQ:
                result = l == r
            elif op == self.NE:
                result = l != r
            elif op == self.GE:
                result = l >= r
            elif op == self.GT:
                result = l > r
        return result

    # -------------------------------------------------------------------------
    @staticmethod
    def _contains(a, b):
        """
            Probe whether a contains b
        """

        if a is None:
            return False
        try:
            if isinstance(a, basestring):
                return str(b) in a
            elif isinstance(a, (list, tuple)):
                if isinstance(b, (list, tuple)):
                    convert = S3TypeConverter.convert
                    found = True
                    for _b in b:
                        if _b not in a:
                            found = False
                            for _a in a:
                                try:
                                    if convert(_a, _b) == _a:
                                        found = True
                                        break
                                except (TypeError, ValueError):
                                    continue
                        if not found:
                            break
                    return found
                else:
                    return b in a
            else:
                return str(b) in str(a)
        except:
            return False

    # -------------------------------------------------------------------------
    def represent(self, resource):
        """
            Represent this query as a human-readable string.

            @param resource: the resource to resolve the query against
        """

        op = self.op
        l = self.left
        r = self.right
        if op == self.AND:
            l = l.represent(resource)
            r = r.represent(resource)
            return "(%s and %s)" % (l, r)
        elif op == self.OR:
            l = l.represent(resource)
            r = r.represent(resource)
            return "(%s or %s)" % (l, r)
        elif op == self.NOT:
            l = l.represent(resource)
            return "(not %s)" % l
        else:
            if isinstance(l, S3FieldSelector):
                l = l.represent(resource)
            elif isinstance(l, basestring):
                l = '"%s"' % l
            if isinstance(r, S3FieldSelector):
                r = r.represent(resource)
            elif isinstance(r, basestring):
                r = '"%s"' % r
            if op == self.CONTAINS:
                return "(%s in %s)" % (r, l)
            elif op == self.BELONGS:
                return "(%s in %s)" % (l, r)
            elif op == self.ANYOF:
                return "(%s contains any of %s)" % (l, r)
            elif op == self.TYPEOF:
                return "(%s is a type of %s)" % (l, r)
            elif op == self.LIKE:
                return "(%s like %s)" % (l, r)
            elif op == self.LT:
                return "(%s < %s)" % (l, r)
            elif op == self.LE:
                return "(%s <= %s)" % (l, r)
            elif op == self.EQ:
                return "(%s == %s)" % (l, r)
            elif op == self.NE:
                return "(%s != %s)" % (l, r)
            elif op == self.GE:
                return "(%s >= %s)" % (l, r)
            elif op == self.GT:
                return "(%s > %s)" % (l, r)
            else:
                return "(%s ?%s? %s)" % (l, op, r)

    # -------------------------------------------------------------------------
    def serialize_url(self, resource=None):
        """
            Serialize this query as URL query

            @return: a Storage of URL variables
        """

        op = self.op
        l = self.left
        r = self.right

        url_query = Storage()
        def _serialize(n, o, v, invert):
            try:
                quote = lambda s: s if "," not in s else '"%s"' % s
                if isinstance(v, list):
                    v = ",".join([quote(S3TypeConverter.convert(str, val))
                                  for val in v])
                else:
                    v = quote(S3TypeConverter.convert(str, v))
            except:
                return
            if "." not in n:
                if resource is not None:
                    n = "~.%s" % n
                else:
                    return url_query
            if o == self.LIKE:
                v = v.replace("%", "*")
            if o == self.EQ:
                operator = ""
            else:
                operator = "__%s" % o
            if invert:
                operator = "%s!" % operator
            key = "%s%s" % (n, operator)
            if key in url_query:
                url_query[key] = "%s,%s" % (url_query[key], v)
            else:
                url_query[key] = v
            return url_query
        if op == self.AND:
            lu = l.serialize_url(resource=resource)
            url_query.update(lu)
            ru = r.serialize_url(resource=resource)
            url_query.update(ru)
        elif op == self.OR:
            sub = self._or()
            if sub is None:
                # This OR-subtree is not serializable
                return url_query
            n, o, v, invert = sub
            _serialize(n, o, v, invert)
        elif op == self.NOT:
            lu = l.serialize_url(resource=resource)
            for k in lu:
                url_query["%s!" % k] = lu[k]
        elif isinstance(l, S3FieldSelector):
            _serialize(l.name, op, r, False)
        return url_query

    # -------------------------------------------------------------------------
    def _or(self):
        """
            Helper method to URL-serialize an OR-subtree in a query in
            alternative field selector syntax if they all use the same
            operator and value (this is needed to URL-serialize an
            S3SearchSimpleWidget query).
        """

        op = self.op
        l = self.left
        r = self.right

        if op == self.AND:
            return None
        elif op == self.NOT:
            lname, lop, lval, linv = l._or()
            return (lname, lop, lval, not linv)
        elif op == self.OR:
            lvars = l._or()
            rvars = r._or()
            if lvars is None or rvars is None:
                return None
            lname, lop, lval, linv = lvars
            rname, rop, rval, rinv = rvars
            if lop != rop or linv != rinv:
                return None
            if lname == rname:
                return (lname, lop, [lval, rval], linv)
            elif lval == rval:
                return ("%s|%s" % (lname, rname), lop, lval, linv)
            else:
                return None
        else:
            return (l.name, op, r, False)

# =============================================================================
class S3URLQuery(object):
    """ URL Query Parser """

    # -------------------------------------------------------------------------
    @classmethod
    def parse(cls, resource, vars):
        """
            Construct a Storage of S3ResourceQuery from a Storage of get_vars

            @param resource: the S3Resource
            @param vars: the get_vars
            @return: Storage of S3ResourceQuery like {alias: query}, where
                     alias is the alias of the component the query concerns
        """

        query = Storage()

        if resource is None:
            return query
        if not vars:
            return query

        subquery = cls._subquery
        allof = lambda l, r: l if r is None else r if l is None else r & l

        for key, value in vars.iteritems():

            if not("." in key or key[0] == "(" and ")" in key):
                continue

            selectors, op, invert = cls.parse_expression(key)

            if type(value) is list:
                # Multiple queries with the same selector (AND)
                q = reduce(allof,
                           [subquery(selectors, op, invert, v) for v in value],
                           None)
            else:
                q = subquery(selectors, op, invert, value)

            if q is None:
                continue

            # Append to query
            if len(selectors) > 1:
                aliases = [s.split(".", 1)[0] for s in selectors]
                if len(set(aliases)) == 1:
                    alias = aliases[0]
                else:
                    alias = resource.alias
                #alias = resource.alias
            else:
                alias = selectors[0].split(".", 1)[0]
            if alias == "~":
                alias = resource.alias
            if alias not in query:
                query[alias] = [q]
            else:
                query[alias].append(q)

        return query

    # -------------------------------------------------------------------------
    @staticmethod
    def parse_url(url):
        """
            Parse a URL query into get_vars

            @param query: the URL query string
            @return: the get_vars (Storage)
        """

        if not url:
            return Storage()
        elif "?" in url:
            query = url.split("?", 1)[1]
        elif "=" in url:
            query = url
        else:
            return Storage()

        import cgi
        dget = cgi.parse_qsl(query, keep_blank_values=1)

        get_vars = Storage()
        for (key, value) in dget:
            if key in get_vars:
                if type(get_vars[key]) is list:
                    get_vars[key].append(value)
                else:
                    get_vars[key] = [get_vars[key], value]
            else:
                get_vars[key] = value
        return get_vars

    # -------------------------------------------------------------------------
    @staticmethod
    def parse_expression(key):
        """
            Parse a URL expression

            @param key: the key for the URL variable
            @return: tuple (selectors, operator, invert)
        """

        if key[-1] == "!":
            invert = True
        else:
            invert = False
        fs = key.rstrip("!")
        op = None
        if "__" in fs:
            fs, op = fs.split("__", 1)
            op = op.strip("_")
        if not op:
            op = "eq"
        if "|" in fs:
            selectors = [s for s in fs.split("|") if s]
        else:
            selectors = [fs]
        return selectors, op, invert

    # -------------------------------------------------------------------------
    @staticmethod
    def parse_value(value):
        """
            Parse a URL query value

            @param value: the value
            @return: the parsed value
        """

        uquote = lambda w: w.replace('\\"', '\\"\\') \
                            .strip('"') \
                            .replace('\\"\\', '"')
        NONE = ("NONE", "None")
        if type(value) is not list:
            value = [value]
        vlist = []
        for item in value:
            w = ""
            quote = False
            ignore_quote = False
            for c in item:
                if c == '"' and not ignore_quote:
                    w += c
                    quote = not quote
                elif c == "," and not quote:
                    if w in NONE:
                        w = None
                    else:
                        w = uquote(w).encode("utf-8")
                    vlist.append(w)
                    w = ""
                else:
                    w += c
                if c == "\\":
                    ignore_quote = True
                else:
                    ignore_quote = False
            if w in NONE:
                w = None
            else:
                w = uquote(w).encode("utf-8")
            vlist.append(w)
        if len(vlist) == 1:
            return vlist[0]
        return vlist

    # -------------------------------------------------------------------------
    @classmethod
    def _subquery(cls, selectors, op, invert, value):
        """
            Construct a sub-query from URL selectors, operator and value

            @param selectors: the selector(s)
            @param op: the operator
            @param invert: invert the query
            @param value: the value
        """

        v = cls.parse_value(value)

        q = None
        for fs in selectors:

            if op == S3ResourceQuery.LIKE:
                # Auto-lowercase and replace wildcard
                f = S3FieldSelector(fs).lower()
                if isinstance(v, basestring):
                    v = v.replace("*", "%").lower()
                elif isinstance(v, list):
                    v = [x.replace("*", "%").lower() for x in v if x is not None]
            else:
                f = S3FieldSelector(fs)

            rquery = None
            try:
                rquery = S3ResourceQuery(op, f, v)
            except SyntaxError:
                current.log.error("Invalid URL query operator: %s (sub-query ignored)" % op)
                q = None
                break

            # Invert operation
            if invert:
                rquery = ~rquery

            # Add to subquery
            if q is None:
                q = rquery
            elif invert:
                q &= rquery
            else:
                q |= rquery

        return q

# END =========================================================================
