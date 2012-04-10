# -*- coding: utf-8 -*-

""" Sahana-Eden GUI Layouts (HTML Renderers)

    @copyright: 2012 (c) Sahana Software Foundation
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

    @status: work in progress
    @todo: - complete layout implementations
           - render "selected" (flag in item)
"""

__all__ = ["S3LanguageMenuLayout", "ML",
           "S3PersonalMenuLayout", "MP",
           "S3MainMenuLayout", "MM",
           "S3OptionsMenuLayout", "M",
           "S3MenuSeparatorLayout", "SEP",
           "S3BreadcrumbsLayout",
           "S3AddResourceLink",
           "homepage"]

from gluon import *
from gluon.storage import Storage
from ..s3 import *

# =============================================================================
class S3MainMenuLayout(S3NavigationItem):
    """ Application Main Menu Layout """

    @staticmethod
    def layout(item):

        if item.parent is None:
            # The main menu
            items = item.render_components()
            return UL(items, _id="nav")
        else:
            if item.components:
                # A submenu
                items = item.render_components()
                _class = item.selected and "highlight" or ""
                return LI(A(item.label, _href=item.url(), _class=_class),
                          UL(items, _class="sub-menu"))
            else:
                # A menu item
                if item.enabled and item.authorized:
                    return LI(A(item.label, _href=item.url()))
                else:
                    return None

# -----------------------------------------------------------------------------
# Shortcut
MM = S3MainMenuLayout

# =============================================================================
class S3OptionsMenuLayout(S3NavigationItem):
    """ Controller Options Menu Layout """

    @staticmethod
    def layout(item):

        if item.parent is None:
            # The menu itself
            items = item.render_components()
            return UL(items, _id="main-sub-menu", _class="sub-menu")
        else:
            if item.enabled and item.authorized:
                if item.components:
                    _class = ""
                    if item.parent.parent is None and item.selected:
                        _class = "highlight"
                    items = item.render_components()
                    if items:
                        items = LI(UL(items, _class="menu-extention"))
                    return [LI(A(item.label, _href=item.url(), _class=_class)), items]
                else:
                    if item.parent.parent is None:
                        _class = item.selected and "highlight" or ""
                    else:
                        _class = " "
                    return LI(A(item.label, _href=item.url(), _class=_class))

# -----------------------------------------------------------------------------
# Shortcut
M = S3OptionsMenuLayout

# =============================================================================
class S3MenuSeparatorLayout(S3NavigationItem):
    """ Simple menu separator """

    @staticmethod
    def layout(item):

        if item.parent is not None:
            return LI(HR(), _class="menu_separator")
        else:
            return None

# -----------------------------------------------------------------------------
# Shortcut
SEP = S3MenuSeparatorLayout

# =============================================================================
class S3BreadcrumbsLayout(S3NavigationItem):
    """ Breadcrumbs layout """

    @staticmethod
    def layout(item):

        if item.parent is None:
            items = item.render_components()
            return DIV(UL(items), _class='breadcrumbs')
        else:
            if item.is_last():
                _class = "highlight"
            else:
                _class = "ancestor"
            return LI(A(item.label, _href=item.url(), _class=_class))

# =============================================================================
class S3AddResourceLink(S3NavigationItem):
    """
        Links in form fields comments to show a form for adding
        a new foreign key record.
    """

    def __init__(self,
                 label=None,
                 c=None,
                 f=None,
                 t=None,
                 vars=None,
                 info=None,
                 title=None,
                 tooltip=None):
        """
            Constructor

            @param c: the target controller
            @param f: the target function
            @param t: the target table (defaults to c_f)
            @param vars: the request vars (format="popup" will be added automatically)
            @param label: the link label (falls back to label_create_button)
            @param info: hover-title for the label
            @param title: the tooltip title
            @param tooltip: the tooltip text
        """

        if label is None:
            label = title
        if info is None:
            info = title

        # Fall back to label_create_button
        if label is None:
            if t is None:
                t = "%s_%s" % (c, f)
            label = S3CRUD.crud_string(t, "label_create_button")

        # Always have format=popup in the URL
        if vars is None:
            vars = Storage()
        vars["format"] = "popup"

        super(S3AddResourceLink, self).__init__(label, c=c, f=f, t=t,
                                                m="create",
                                                vars=vars,
                                                info=info,
                                                title=title,
                                                tooltip=tooltip,
                                                mandatory=True)

    # -------------------------------------------------------------------------
    @staticmethod
    def layout(item):
        """ Layout for popup link """

        if not item.authorized:
            return None

        popup = A(item.label,
                  _href=item.url(),
                  _class="colorbox",
                  _target="top",
                  _title=item.opts.info)

        tooltip = item.opts.tooltip
        if tooltip is not None:
            ttip = DIV(_class="tooltip",
                       _title="%s|%s" % (item.label, tooltip))
        else:
            ttip = ""

        return DIV(popup, ttip)

# =============================================================================
def homepage(module=None, *match, **attr):
    """
        Shortcut for module homepage menu items using the MM layout,
        retrieves the module's nice name.

        @param module: the module's prefix (controller)
        @param match: additional prefixes
        @param attr: attributes for the navigation item
    """

    settings = current.deployment_settings
    all_modules = settings.modules

    layout = S3MainMenuLayout

    if module is None:
        module = "default"
    if module in all_modules:
        m = all_modules[module]
        c = [module] + list(match)
        return layout(m.name_nice, c=c, f="index", **attr)
    return None

# =============================================================================
class S3LanguageMenuLayout(S3NavigationItem):

    @staticmethod
    def layout(item):
        """ Language menu layout

            options for each entry:
                - lang_code: the language code
                - lang_name: the language name
            option for the menu
                - current_language: code of the current language
        """

        if item.enabled:
            if item.components:
                # The language menu itself
                current_language = current.T.accepted_language
                items = item.render_components()
                select = SELECT(items, value=current_language,
                                    _name="_language",
                                    _title="Language Selection",
                                    _onchange="$('#personal-menu div form').submit();")
                form = FORM(select, _id="language_selector",
                                    _name="_language",
                                    _action="",
                                    _method="get")
                return form
            else:
                # A language entry
                return OPTION(item.opts.lang_name,
                              _value=item.opts.lang_code)
        else:
            return None

    # -------------------------------------------------------------------------
    def check_enabled(self):
        """ Check whether the language menu is enabled """

        if current.deployment_settings.get_L10n_display_toolbar():
            return True
        else:
            return False

# -----------------------------------------------------------------------------
# Shortcut
ML = S3LanguageMenuLayout

# =============================================================================
class S3PersonalMenuLayout(S3NavigationItem):

    @staticmethod
    def layout(item):

        if item.parent is None:
            # The menu
            items = item.render_components()
            if items:
                return DIV(UL(items), _class="pmenu-wrapper")
            else:
                return "" # menu is empty
        else:
            # A menu item
            if item.enabled and item.authorized:
                return LI(A(item.label, _href=item.url()))
            else:
                return None

# -----------------------------------------------------------------------------
# Shortcut
MP = S3PersonalMenuLayout

# END =========================================================================
