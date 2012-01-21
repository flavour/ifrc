# -*- coding: utf-8 -*-

"""
    S3 Navigation Module

    @author: Dominic König <dominic[at]aidiq.com>

    @copyright: 2011 (c) Sahana Software Foundation
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

__all__ = ["S3Menu",
           "s3_rheader_tabs",
           "s3_rheader_resource",
           "s3_popup_comment"]

from gluon import *
from gluon.storage import Storage

# =============================================================================
class S3Menu(DIV):
    """
        MENU implementation -
            * breadcrumbs support
            * greater control / flexibility

        @author Abhishek Mishra
        @author Fran Boon
    """

    # -------------------------------------------------------------------------
    def __init__(self, data, **args):
        self.data = data
        self.attributes = args

    # -------------------------------------------------------------------------
    def serialize(self, data, level=0):
        """
            NOTE on right:
                personal-menu is the one on top right besides login,
                a presence of right in module level menu indicates a personal-menu

                nav is the big menu below the logo,
                an absence of right in module level menu indicates nav items

                main-sub-menu is the left side menu
                a right = True indicates a highlight here (set by 01_menu)

                extension are submenus under main-sub-menu
                a right = True indicates highlight here (set by 01_menu)
        """
        _type = self.attributes["_type"]
        if _type == "personal-menu":
            items = []
            data = [x for x in data if x[1]]
            for item in data:
                (name, link) = item[:2]
                items.append(LI(A(name,
                                  _href=link)
                                )
                            )

            deployment_settings = current.deployment_settings
            if deployment_settings.get_L10n_display_toolbar():
                menu_langs = self.attributes["_menu_langs"]
                current_lang = current.T.accepted_language
                langopts = [ OPTION(x[0], _value=x[2]) for x in menu_langs[3] ]
                langselect = SELECT(langopts,
                                    _name="_language",
                                    _title="Language Selection",
                                    value=current_lang,
                                    _onchange="$('#personal-menu div form').submit();"
                                )
                langform = FORM(langselect,
                                _name="_language",
                                _action="",
                                _method="get")
                return DIV([UL(items), langform], _class="pmenu-wrapper")
            else:
                return DIV(UL(items))
        elif _type == "nav":
            _highlight = "" or self.attributes["_highlight"]
            items = []
            for item in data:
                (name, right, link) = item[:3]
                if not right:
                    import re
                    _link = link
                    if "default" not in _highlight:
                        _highlight = re.match("(.*/).*$", _highlight).group(1)
                        _link = re.match("(.*/).*$", link).group(1)
                    _class = "highlight" if str(_link) in _highlight else " "
                    items.append(LI(
                        A(name, _href=link, _class=_class)
                    ))
            return UL(items, **self.attributes)
        elif _type == "main-sub-menu":
            items = []
            for item in data:
                (name, right, link) = item[:3]
                if link:
                    # Lack of link => lack of permissions
                    items.append(LI(A(name,
                                      _href=link,
                                      _class="highlight" if right==True else " ")
                                    )
                                )
                if len(item) > 3:
                    sub = item[3]
                    append = S3Menu(sub,
                                    _type="extension",
                                    _class="menu-extention").serialize(sub)
                    items.append(append)
            return UL(items, **self.attributes)
        elif _type == "extension":
            items = []
            for item in data:
                (name, right, link) = item[:3]
                if link:
                    # Lack of link => lack of permissions
                    items.append(LI(A("%s" % name,
                                      _href=link,
                                      _class="highlight" if right==True else " ")
                                    )
                                )
            return UL(items, **self.attributes)
        else:
            return UL()

    # -------------------------------------------------------------------------
    def xml(self):
        return self.serialize(self.data, 0).xml()

# =============================================================================
def s3_popup_comment(c=None,
                     f=None,
                     t=None,
                     vars=None,
                     title=None,
                     tooltip=None):

    """
        Generate a ADD-popup comment, return an empty DIV if the user
        is not permitted to add records to the referenced table

        @param c: the target controller
        @param f: the target function
        @param t: the target table (defaults to c_f)
        @param vars: the request vars (format="popup" will be added automatically)
        @param title: the tooltip title
        @param tooltip: the tooltip text

        @todo: replace by S3NavigationItem
    """

    auth = current.auth

    if title is None:
        return None

    if vars is not None:
        _vars = Storage(vars)
    else:
        _vars = Storage()
    _vars.update(format="popup")

    popup = ""
    ttip = ""
    if c and f and auth is not None:
        _href = auth.permission.accessible_url(c=c, f=f, t=t,
                                               p="create",
                                               args="create", vars=_vars)
        if _href is not False:
            popup = A(title,
                      _class="colorbox",
                      _href=_href,
                      _target="top",
                      _title=title)
            if tooltip is not None:
                ttip = DIV(_class="tooltip",
                        _title="%s|%s" % (title, tooltip))

    comment = DIV(popup, ttip)
    return comment

# =============================================================================
def s3_rheader_resource(r):
    """
        Identify the tablename and record ID for the rheader

        @param r: the current S3Request

    """

    _vars = r.get_vars

    if "viewing" in _vars:
        tablename, record_id = _vars.viewing.rsplit(".", 1)
        db = current.db
        record = db[tablename][record_id]
    else:
        tablename = r.tablename
        record = r.record

    return (tablename, record)

# =============================================================================
def s3_rheader_tabs(r, tabs=[]):
    """
        Constructs a DIV of component links for a S3RESTRequest

        @param tabs: the tabs as list of tuples (title, component_name, vars),
            where vars is optional
    """

    rheader_tabs = S3ComponentTabs(tabs)
    return rheader_tabs.render(r)

# =============================================================================
class S3ComponentTabs:

    def __init__(self, tabs=[]):

        self.tabs = [S3ComponentTab(t) for t in tabs]

    # -------------------------------------------------------------------------
    def render(self, r):

        rheader_tabs = []

        tablist = []

        tabs = [t for t in self.tabs if t.active(r)]

        # Check whether there is a tab for this resource method (no component)
        mtab = r.component is None and \
               [t.component for t in tabs if t.component == r.method] and True or False

        record_id = r.id

        for i in xrange(len(tabs)):

            tab = tabs[i]
            title = tab.title
            component = tab.component

            vars_match = tab.vars_match(r)
            if vars_match:
                _vars = Storage(r.get_vars)
            else:
                _vars = Storage(tab.vars)
                if "viewing" in r.get_vars:
                    _vars.viewing = r.get_vars.viewing

            if i == len(tabs)-1:
                _class = "tab_last"
            else:
                _class = "tab_other"

            here = False
            if tab.function is None:
                if "viewing" in _vars:
                    tablename, record_id = _vars.viewing.split(".", 1)
                    function = tablename.split("_", 1)[1]
                else:
                    function = r.function
            else:
                function = tab.function
            if function == r.name or \
               (function == r.function and "viewing" in _vars):
                   here = r.method == component or not mtab
            if component:
                if r.component and r.component.alias == component and vars_match:
                    here = True
                elif r.custom_action and r.method == component:
                    here = True
                else:
                    here = False
            else:
                if r.component or not vars_match:
                    here = False
            if here:
                _class = "tab_here"

            if component:
                if record_id:
                    args = [record_id, component]
                else:
                    args = [component]
                if "viewing" in _vars:
                    del _vars["viewing"]
                _href = URL(function, args=args, vars=_vars)
            else:
                args = []
                if function != r.name:
                    if "viewing" not in _vars and r.id:
                        _vars.update(viewing="%s.%s" % (r.tablename, r.id))
                    elif not tab.component and not tab.function:
                        if "viewing" in _vars:
                            del _vars["viewing"]
                        args = [record_id]
                else:
                    if "viewing" not in _vars and record_id:
                        args = [record_id]
                _href = URL(function, args=args, vars=_vars)

            rheader_tabs.append(SPAN(A(tab.title, _href=_href), _class=_class))

        if rheader_tabs:
            rheader_tabs = DIV(rheader_tabs, _class="tabs")
        else:
            rheader_tabs = ""
        return rheader_tabs

# =============================================================================
class S3ComponentTab:

    def __init__(self, tab):

        title, component = tab[:2]
        if component and component.find("/") > 0:
            function, component = component.split("/", 1)
        else:
            function = None

        self.title = title

        if function:
            self.function = function
        else:
            self.function = None

        if component:
            self.component = component
        else:
            self.component = None

        if len(tab) > 2:
            self.vars = Storage(tab[2])
        else:
            self.vars = None

    # -------------------------------------------------------------------------
    def active(self, r):

        manager = current.manager
        model = manager.model

        get_vars = r.get_vars
        tablename = None
        if "viewing" in get_vars:
            try:
                tablename, record_id = get_vars["viewing"].split(".", 1)
            except:
                pass

        resource = r.resource
        component = self.component
        if component:
            clist = model.get_components(resource.table, names=[component])
            if component in clist:
                return True
            elif tablename:
                clist = model.get_components(tablename, names=[component])
                if component in clist:
                    return True
            handler = model.get_method(resource.prefix,
                                       resource.name,
                                       method=component)
            if handler is None and tablename:
                prefix, name = tablename.split("_", 1)
                handler = model.get_method(prefix, name,
                                           method=component)
            if handler is None:
                handler = r.get_handler(component)
            if handler is None:
                return component in ("create", "read", "update", "delete")
        return True

    # -------------------------------------------------------------------------
    def vars_match(self, r):

        get_vars = r.get_vars
        if self.vars is None:
            return True
        for k, v in self.vars.iteritems():
            if k not in get_vars or \
               k in get_vars and get_vars.get(k) != v:
                return False
        return True

# END =========================================================================
