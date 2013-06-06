# -*- coding: utf-8 -*-

""" Resource Summary Pages

    @copyright: 2013 (c) Sahana Software Foundation
    @license: MIT

    @requires: U{B{I{gluon}} <http://web2py.com>}

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

from gluon import *
from gluon.storage import Storage

from s3filter import S3FilterForm
from s3rest import S3Method

# =============================================================================
class S3Summary(S3Method):
    """ Resource Summary Pages """

    # -------------------------------------------------------------------------
    def apply_method(self, r, **attr):
        """
            Entry point for REST interface

            @param r: the S3Request
            @param attr: controller attributes
        """

        if "w" in r.get_vars:
            # Ajax-request for a specific widget
            return self.ajax(r, **attr)
            
        else:
            # Full page request
            # @todo: check for proper format + method
            return self.summary(r, **attr)

    # -------------------------------------------------------------------------
    def summary(self, r, **attr):
        """
            Render the summary page

            @param r: the S3Request
            @param attr: controller attributes
        """

        output = {}
        resource = self.resource
        get_config = resource.get_config

        # Get Summary Page Configuration
        config = self._get_config(resource)

        # Page title
        crud_string = self.crud_string
        title = crud_string(self.tablename, "title_list")
        output["title"] = title

        # Tabs
        tablist = UL()
        sections = []

        # Active tab
        if "t" in r.get_vars:
            active = r.get_vars["t"]
        else:
            active = None
        active_tab = "null"

        # Render sections
        
        section_idx = 0
        widget_idx = 0
        targets = []
        for section in config:

            # Active tab?
            if active and active == str(section_idx):
                active_tab = section_idx

            # Label
            label = section["label"]
            translate = section.get("translate", True)
            if isinstance(label, basestring) and translate:
                self.label = current.T(label)
            else:
                self.label = label

            # Tab
            section_id = section["name"]
            tablist.append(LI(A(label, _href="#%s" % section_id)))

            # Section container
            s = DIV(_class="section-container", _id=section_id)

            # Widgets
            widgets = section.get("widgets", [])
            for widget in widgets:

                # Widget ID
                widget_id = "summary-%s" % widget_idx

                # Make sure widgets include the widget ID when
                # generating Ajax URLs:
                r.get_vars["w"] = r.vars["w"] = widget_id

                # Append to filter targets
                filterable = widget.get("filterable", True)
                if filterable:
                    targets.append(widget_id)

                # Apply method
                method = widget.get("method", None)
                content = None
                if callable(method):
                    content = method(r, widget_id=widget_id, **attr)
                else:
                    handler = r.get_widget_handler(method)
                    if handler is not None:
                        content = handler(r,
                                          method=method,
                                          widget_id=widget_id,
                                          **attr)
                    else:
                        r.error(405, r.ERROR.BAD_METHOD)

                # Add content to section
                if isinstance(content, dict):
                    for k, v in content.items():
                        if k not in ("tabs", "sections", "widget"):
                            output[k] = v
                    content = content.get("widget", "EMPTY")
                s.append(DIV(content,
                             _id="%s-container" % widget_id,
                             _class="widget-container"))
                widget_idx += 1

            sections.append(s)
            section_idx += 1

        # Add tabs + sections to output
        if len(sections) > 1:
            output["tabs"] = tablist
        else:
            # hide tabs if there's only one section
            output["tabs"] = ""
        output["sections"] = sections

        # Filter targets
        target = " ".join(targets)

        # Filter form
        filter_ajax = True
        form_id = "summary-filter-form"
        filter_widgets = get_config("filter_widgets", None)
        hide_filter = attr.get("hide_filter", False)
        if filter_widgets and not hide_filter:

            # Where to retrieve filtered data from:
            if active_tab != "null":
                submit_url_vars = {"t": active_tab}
            else:
                submit_url_vars = {}
            filter_submit_url = attr.get("filter_submit_url",
                                         r.url(vars=submit_url_vars))
            
            # Where to retrieve updated filter options from:
            filter_ajax_url = attr.get("filter_ajax_url",
                                        r.url(method="filter",
                                              vars={},
                                              representation="json"))

            filter_formstyle = get_config("filter_formstyle", None)
            filter_submit = get_config("filter_submit", True)
            filter_form = S3FilterForm(filter_widgets,
                                       formstyle=filter_formstyle,
                                       submit=filter_submit,
                                       ajax=filter_ajax,
                                       url=filter_submit_url,
                                       ajaxurl=filter_ajax_url,
                                       _class="filter-form",
                                       _id=form_id)
            fresource = current.s3db.resource(resource.tablename)
            
            alias = resource.alias if r.component else None
            output["filter_form"] = filter_form.html(fresource,
                                                     r.get_vars,
                                                     target=target,
                                                     alias=alias)
        else:
            # Render as empty string to avoid the exception in the view
            output["filter_form"] = ""

        # View
        response = current.response
        response.view = self._view(r, "summary.html")

        # Script for tabs & map
        if len(sections) > 1:
            script = """
$('#summary-tabs').tabs({
 active:%(active_tab)s,
 activate:function(event,ui){
  if(ui.newTab.length){
   S3.search.updateFilterSubmitURL('%(form_id)s','t',$(ui.newTab).index())
  }
  S3.search.updatePendingTargets('%(form_id)s')
 }
});""" % dict(form_id = form_id, active_tab = active_tab)

            response.s3.jquery_ready.append(script)

        return output

    # -------------------------------------------------------------------------
    def ajax(self, r, **attr):
        """
            Render a specific widget for pulling-in via AJAX

            @param r: the S3Request
            @param attr: controller attributes
        """

        # Get Summary Page Configuration
        config = self._get_config(self.resource)

        widget_id = r.get_vars.get("w")
        i = 0
        for section in config:
            widgets = section.get("widgets", [])
            for widget in widgets:
                if widget_id == "summary-%s" % i:
                    method = widget.get("method", None)
                    output = None
                    if callable(method):
                        output = method(r, widget_id=widget_id, **attr)
                    else:
                        handler = r.get_widget_handler(method)
                        if handler is not None:
                            output = handler(r,
                                             method=method,
                                             widget_id=widget_id,
                                             **attr)
                        else:
                            r.error(405, r.ERROR.BAD_METHOD)
                    return output
                i += 1

        # Not found?
        return None
        
    # -------------------------------------------------------------------------
    def _get_config(self, resource):
        """
            Get the summary page configuration

            @param resource: the target S3Resource
        """

        get_config = resource.get_config
        config = get_config("summary",
                            current.deployment_settings.get_ui_summary())
        if not config:
            config = [{"name": "table",
                       "label": "Table",
                       "widgets": [
                            {"name": "datatable",
                             "method": "datatable"
                            }
                       ]}]
        return config

# END =========================================================================
