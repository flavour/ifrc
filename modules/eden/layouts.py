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
           - remove S3Menu
"""

__all__ = ["S3LanguageMenuLayout", "ML",
           "S3PersonalMenuLayout", "MP",
           "S3MainMenuLayout", "MM",
           "S3OptionsMenuLayout", "M",
           "S3MenuSeparatorLayout", "SEP",
           "S3BreadcrumbsLayout",
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

# =========================================================================

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

# =========================================================================

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

# =========================================================================
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
class S3Menu(DIV):
    """
        MENU implementation -
            * breadcrumbs support
            * greater control / flexibility

        @author Abhishek Mishra
        @author Fran Boon

        @deprecated: retained here for reference
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
                current_language = item.options.get("current_language", None)
                items = item.render_components()
                select = SELECT(items, value=current_language,
                                    _name="_language",
                                    _title="Language Selection",
                                    _onchange="$('#personal-menu div form').submit();")
                form = FORM(select, _name="_language",
                                    _action="",
                                    _method="get")
                return form
            else:
                # A language entry
                return OPTION(item.option.lang_code,
                              item.option.lang_name)
        else:
            return None

    # -------------------------------------------------------------------------
    def check_enabled(self):
        """ Check whether the language menu is enabled """

        settings = current.deployment_settings

        if settings.get_L10n_display_toolbar():
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
