# -*- coding: utf-8 -*-

from collections import OrderedDict

from gluon import current
from gluon.storage import Storage

def config(settings):
    """
        Template for WA-COP + CAD Cloud Integration
    """

    T = current.T

    # =========================================================================
    # System Settings
    #
    settings.base.system_name_short = T("Sahana")

    # Prepop default
    settings.base.prepopulate += ("WACOP", "default/users", "WACOP/Demo")

    # Theme (folder to use for views/layout.html)
    settings.base.theme = "WACOP"

    settings.ui.social_buttons = True

    # -------------------------------------------------------------------------
    # Self-Registration and User Profile
    #
    # Users can self-register
    settings.security.self_registration = False
    # Users need to verify their email
    settings.auth.registration_requires_verification = True
    # Users need to be approved
    settings.auth.registration_requires_approval = True
    settings.auth.registration_requests_organisation = True
    settings.auth.registration_organisation_required = True

    # Approval emails get sent to all admins
    settings.mail.approver = "ADMIN"

    settings.auth.registration_link_user_to = {"staff": T("Staff")}
    settings.auth.registration_link_user_to_default = ["staff"]
    settings.auth.registration_roles = {"organisation_id": ["USER"],
                                        }

    settings.auth.show_utc_offset = False
    settings.auth.show_link = False

    # -------------------------------------------------------------------------
    # Security Policy
    #
    settings.security.policy = 7 # Apply Controller, Function and Table ACLs
    settings.security.map = True

    # -------------------------------------------------------------------------
    # Audit
    #
    def audit_write(method, tablename, form, record, representation):
        if tablename in ("event_incident",
                         "pr_group",
                         ):
            # Track the Source Repository for Incidents / Resources
            return True
        else:
            # Don't Audit
            return False

    settings.security.audit_write = audit_write

    # -------------------------------------------------------------------------
    # L10n (Localization) settings
    #
    settings.L10n.languages = OrderedDict([
        ("en", "English"),
        ("es", "Español"),
    ])
    # Default Language
    settings.L10n.default_language = "en"
    # Default timezone for users
    settings.L10n.utc_offset = "-0800"
    # Unsortable 'pretty' date format
    settings.L10n.date_format = "%b %d %Y"
    # Number formats (defaults to ISO 31-0)
    # Decimal separator for numbers (defaults to ,)
    settings.L10n.decimal_separator = "."
    # Thousands separator for numbers (defaults to space)
    settings.L10n.thousands_separator = ","
    # Default Country Code for telephone numbers
    settings.L10n.default_country_code = 1
    # Enable this to change the label for 'Mobile Phone'
    settings.ui.label_mobile_phone = "Cell Phone"
    # Enable this to change the label for 'Postcode'
    settings.ui.label_postcode = "ZIP Code"

    settings.msg.require_international_phone_numbers = False
    # PDF to Letter
    settings.base.paper_size = T("Letter")

    # Uncomment this to Translate CMS Series Names
    # - we want this on when running s3translate but off in normal usage as we use the English names to lookup icons in render_posts
    #settings.L10n.translate_cms_series = True
    # Uncomment this to Translate Location Names
    #settings.L10n.translate_gis_location = True

    # Has scalability issues, but should be OK with our number of records
    settings.search.dates_auto_range = True

    # -------------------------------------------------------------------------
    # GIS settings
    #
    # Restrict the Location Selector to just certain countries
    settings.gis.countries = ("US",)
    # Levels for the LocationSelector
    #levels = ("L1", "L2", "L3")

    # Uncomment to pass Addresses imported from CSV to a Geocoder to try and automate Lat/Lon
    #settings.gis.geocode_imported_addresses = "google"

    # Until we add support to S3LocationSelector to set dropdowns from LatLons
    settings.gis.check_within_parent_boundaries = False
    # GeoNames username
    settings.gis.geonames_username = "mcop"
    # Uncomment to hide Layer Properties tool
    #settings.gis.layer_properties = False
    # Uncomment to display the Map Legend as a floating DIV
    settings.gis.legend = "float"
    # Uncomment to prevent showing LatLon in Location Represents
    settings.gis.location_represent_address_only = "icon"
    # Resources which can be directly added to the main map
    settings.gis.poi_create_resources = None

    # -------------------------------------------------------------------------
    # UI Settings
    #
    settings.ui.datatables_pagingType = "bootstrap"
    settings.ui.update_label = "Edit"

    # -------------------------------------------------------------------------
    # Modules
    #
    settings.modules = OrderedDict([
        # Core modules which shouldn't be disabled
        ("default", Storage(
            name_nice = "Home",
            restricted = False, # Use ACLs to control access to this module
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = None  # This item is not shown in the menu
        )),
        ("admin", Storage(
            name_nice = "Administration",
            #description = "Site Administration",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = None  # This item is handled separately for the menu
        )),
        ("appadmin", Storage(
            name_nice = "Administration",
            #description = "Site Administration",
            restricted = True,
            module_type = None  # No Menu
        )),
    #    ("errors", Storage(
    #        name_nice = "Ticket Viewer",
    #        #description = "Needed for Breadcrumbs",
    #        restricted = False,
    #        module_type = None  # No Menu
    #    )),
       ("sync", Storage(
           name_nice = "Synchronization",
           #description = "Synchronization",
           restricted = True,
           access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
           module_type = None  # This item is handled separately for the menu
       )),
        #("translate", Storage(
        #    name_nice = "Translation Functionality",
        #    #description = "Selective translation of strings based on module.",
        #    module_type = None,
        #)),
        ("gis", Storage(
            name_nice = "Map",
            #description = "Situation Awareness & Geospatial Analysis",
            restricted = True,
            module_type = 1,     # 1st item in the menu
        )),
        ("pr", Storage(
            name_nice = "Persons",
            description = "Central point to record details on People",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = None
        )),
        ("org", Storage(
            name_nice = "Organizations",
            #description = 'Lists "who is doing what & where". Allows relief agencies to coordinate their activities',
            restricted = True,
            module_type = 10
        )),
        # All modules below here should be possible to disable safely
        ("hrm", Storage(
            name_nice = "Contacts",
            #description = "Human Resources Management",
            restricted = True,
            module_type = None,
        )),
        ("cms", Storage(
                name_nice = "Content Management",
                restricted = True,
                module_type = 10,
            )),
        ("event", Storage(
                name_nice = "Events",
                restricted = True,
                module_type = 2,
            )),
        ("fire", Storage(
                name_nice = "Fire",
                restricted = True,
                module_type = None,
            )),
        ("police", Storage(
                name_nice = "Police",
                restricted = True,
                module_type = None,
            )),
        ("project", Storage(
                name_nice = "Tasks",
                restricted = True,
                module_type = None,
            )),
        ("doc", Storage(
            name_nice = "Documents",
            #description = "A library of digital resources, such as photos, documents and reports",
            restricted = True,
            module_type = None,
        )),
        ("stats", Storage(
            name_nice = "Statistics",
            restricted = True,
            module_type = None
        )),
    ])

    # -------------------------------------------------------------------------
    # CMS Content Management
    #
    settings.cms.bookmarks = True
    settings.cms.richtext = True
    settings.cms.show_tags = True

    # -------------------------------------------------------------------------
    def cms_post_onaccept(form):
        """
            Handle Tags in Create / Update forms
        """

        post_id = form.vars.id

        db = current.db
        s3db = current.s3db
        ttable = s3db.cms_tag
        ltable = s3db.cms_tag_post

        # Delete all existing tags for this post
        db(ltable.post_id == post_id).delete()

        # Add these tags
        tags = current.request.post_vars.get("tags")
        if not tags:
            return

        tags = tags.split(",")
        tag_ids = db(ttable.name.belongs(tags)).select(ttable.id,
                                                       ttable.name).as_dict(key="name")
        for tag in tags:
            row = tag_ids.get("tag")
            if row:
                tag_id = row.get("id")
            else:
                tag_id = ttable.insert(name=tag)
            ltable.insert(post_id = post_id,
                          tag_id = tag_id,
                          )

    # -------------------------------------------------------------------------
    def customise_cms_post_resource(r, tablename):

        db = current.db
        s3db = current.s3db
        table = s3db.cms_post                      
        table.priority.readable = table.priority.writable = True
        table.series_id.readable = table.series_id.writable = True
        table.status_id.readable = table.status_id.writable = True

        method = r.method
        if method in ("create", "update"):
            # Custom Form
            from s3 import S3SQLCustomForm, S3SQLInlineComponent

            s3db.cms_post_team.group_id.widget = None

            crud_fields = [S3SQLInlineComponent("post_team",
                                                fields = [("", "group_id")],
                                                label = T("Resource"),
                                                multiple = False,
                                                ),
                           (T("Type"), "series_id"),
                           (T("Priority"), "priority"),
                           (T("Status"), "status_id"),
                           (T("Title"), "title"),
                           (T("Text"), "body"),
                           (T("Location"), "location_id"),
                           # Tags are added client-side
                           S3SQLInlineComponent("document",
                                                name = "file",
                                                label = T("Files"),
                                                fields = [("", "file"),
                                                          #"comments",
                                                          ],
                                                ),
                           ]

            if r.tablename != "event_incident":
                if r.tablename == "event_event":
                    from gluon import IS_EMPTY_OR
                    from s3 import IS_ONE_OF
                    itable = s3db.event_incident
                    query = (itable.event_id == r.id) & \
                            (itable.closed == False) & \
                            (itable.deleted == False)
                    the_set = db(query)
                    f = s3db.event_post.incident_id
                    f.requires = IS_EMPTY_OR(
                                    IS_ONE_OF(the_set, "event_incident.id",
                                              f.represent,
                                              orderby="event_incident.name",
                                              sort=True))
                crud_fields.insert(0, S3SQLInlineComponent("incident_post",
                                                           fields = [("", "incident_id")],
                                                           label = T("Incident"),
                                                           multiple = False,
                                                           ))

            crud_form = S3SQLCustomForm(*crud_fields
                                        )

            # Client support for Tags
            appname = r.application
            s3 = current.response.s3
            scripts_append = s3.scripts.append
            if s3.debug:
                scripts_append("/%s/static/scripts/tag-it.js" % appname)
            else:
                scripts_append("/%s/static/scripts/tag-it.min.js" % appname)
            scripts_append("/%s/static/themes/WACOP/js/update_tags.js" % appname)
            if method == "create":
                s3.jquery_ready.append('''wacop_update_tags("")''')
            elif method == "update":
                ttable = s3db.cms_tag
                ltable = s3db.cms_tag_post
                if r.tablename == "cms_post":
                    post_id = r.id
                else:
                    post_id = r.component.id
                query = (ltable.post_id == post_id) & \
                        (ltable.tag_id == ttable.id)
                tags = db(query).select(ttable.name)
                tags = [tag.name for tag in tags]
                tags = ",".join(tags)
                s3.jquery_ready.append('''wacop_update_tags("%s")''' % tags)

            # Processing Tags
            default = s3db.get_config(tablename, "onaccept")
            if isinstance(default, list):
                onaccept = default
                onaccept.append(cms_post_onaccept)
            else:
                onaccept = [default, cms_post_onaccept]

            s3db.configure(tablename,
                           crud_form = crud_form,
                           onaccept = onaccept,
                           )

        elif method in ("custom", "datalist", "filter"):
            # dataList configuration
            from templates.WACOP.controllers import cms_post_list_layout

            s3 = current.response.s3
            s3.dl_no_header = True

            s3db.configure(tablename,
                           # No create form in the datalist popups on Resource Browse page
                           insertable = False,
                           list_fields = ["series_id",
                                          "priority",
                                          "status_id",
                                          "date",
                                          "title",
                                          "body",
                                          "created_by",
                                          "tag.name",
                                          "document.file",
                                          "comment.id",
                                          # Extra fields come in unsorted, so can't match up to records
                                          #"comment.body",
                                          #"comment.created_by",
                                          #"comment.created_on",
                                          ],
                           list_layout = cms_post_list_layout,
                           # Default
                           #orderby = "cms_post.date desc",
                           )

            if method in ("custom", "filter"):
                # Filter Widgets
                from s3 import S3DateFilter, \
                               S3LocationFilter, \
                               S3OptionsFilter, \
                               S3TextFilter

                if method == "filter":
                    # Apply filter_vars
                    get_vars = r.get_vars
                    for k, v in get_vars.iteritems():
                        # We only expect a maximum of 1 of these, no need to append
                        from s3 import FS
                        s3.filter = (FS(k) == v)

                date_filter = S3DateFilter("date",
                                           # If we introduce an end_date on Posts:
                                           #["date", "end_date"],
                                           label = "",
                                           #hide_time = True,
                                           slider = True,
                                           clear_text = "X",
                                           )
                date_filter.input_labels = {"ge": "Start Time/Date", "le": "End Time/Date"}

                from templates.WACOP.controllers import text_filter_formstyle

                filter_widgets = [S3TextFilter(["body",
                                                ],
                                               formstyle = text_filter_formstyle,
                                               label = T("Search"),
                                               _placeholder = T("Enter search term…"),
                                               ),
                                  S3OptionsFilter("series_id",
                                                  label = "",
                                                  noneSelectedText = "Type", # T() added in widget
                                                  no_opts = "",
                                                  ),
                                  S3OptionsFilter("priority",
                                                  label = "",
                                                  noneSelectedText = "Priority", # T() added in widget
                                                  no_opts = "",
                                                  ),
                                  S3OptionsFilter("status_id",
                                                  label = "",
                                                  noneSelectedText = "Status", # T() added in widget
                                                  no_opts = "",
                                                  ),
                                  S3OptionsFilter("created_by$organisation_id",
                                                  label = "",
                                                  noneSelectedText = "Source", # T() added in widget
                                                  no_opts = "",
                                                  ),
                                  S3OptionsFilter("tag_post.tag_id",
                                                  label = "",
                                                  noneSelectedText = "Tag", # T() added in widget
                                                  no_opts = "",
                                                  ),
                                  date_filter,
                                  ]
                if r.tablename == "event_event" or \
                   (method == "filter" and get_vars.get("event_post.event_id")):
                    # Event Profile
                    filter_widgets.insert(1, S3OptionsFilter("incident_post.incident_id",
                                                             label = "",
                                                             noneSelectedText = "Incident", # T() added in widget
                                                             no_opts = "",
                                                             ))

                user = current.auth.user
                if user:
                    filter_widgets.insert(1, S3OptionsFilter("bookmark.user_id",
                                                             label = "",
                                                             options = {"*": T("All"),
                                                                        user.id: T("My Bookmarks"),
                                                                        },
                                                             cols = 2,
                                                             multiple = False,
                                                             table = False,
                                                             ))

                s3db.configure(tablename,
                               filter_widgets = filter_widgets,
                               )

    settings.customise_cms_post_resource = customise_cms_post_resource

    # -------------------------------------------------------------------------
    # Event/Incident Management
    #
    settings.event.incident_teams_tab = "Units"
    # Uncomment to preserve linked Incidents when an Event is deleted
    settings.event.cascade_delete_incidents = False

    # -------------------------------------------------------------------------
    def customise_event_event_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod

        db = current.db
        s3db = current.s3db

        # Virtual Fields
        etable = s3db.event_event
        #append = etable._virtual_methods.append

        def event_name(row):
            return A(row["event_event.name"],
                     _href = URL(c="event", f="event",
                                 args=[row["event_event.id"], "custom"],
                                 extension = "", # ensure no .aadata
                                 ),
                     )
        #append(Field.Method("name_click", event_name))
        etable.name_click = s3_fieldmethod("name_click",
                                           event_name,
                                           # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                           represent = lambda v: v,
                                           search_field = "name",
                                           )

        def event_status(row):
            if row["event_event.exercise"]:
                status = T("Testing")
            elif not row["event_event.end_date"]:
                status = T("Open")
            else:
                status = T("Closed")
            return status
        #append(Field.Method("status", event_status))
        etable.status = s3_fieldmethod("status", event_status)

        itable = s3db.event_incident
        def event_incidents(row):
            query = (itable.event_id == row["event_event.id"]) & \
                    (itable.deleted == False)
            incidents = db(query).count()
            return incidents
        #append(Field.Method("incidents", event_incidents))
        etable.incidents = s3_fieldmethod("incidents", event_incidents)

        ertable = s3db.event_team
        def event_resources(row):
            query = (ertable.event_id == row["event_event.id"]) & \
                    (ertable.deleted == False)
            resources = db(query).count()
            return resources
        #append(Field.Method("resources", event_resources))
        etable.resources = s3_fieldmethod("resources", event_resources)

        ettable = s3db.event_tag
        ttable = s3db.cms_tag
        def event_tags(row):
            query = (ettable.event_id == row["event_event.id"]) & \
                    (ettable.deleted == False) & \
                    (ettable.tag_id == ttable.id)
            tags = db(query).select(ttable.name)
            if tags:
                tags = [t.name for t in tags]
                tags = ", ".join(tags)
                return tags
            else:
                return current.messages["NONE"]
        #append(Field.Method("tags", event_tags))
        etable.tags = s3_fieldmethod("tags", event_tags)

        list_fields = [(T("Name"), "name_click"),
                       (T("Status"), "status"),
                       (T("Zero Hour"), "start_date"),
                       (T("Closed"), "end_date"),
                       (T("City"), "location.location_id.L3"),
                       (T("State"), "location.location_id.L1"),
                       (T("Tags"), "tags"),
                       (T("Incidents"), "incidents"),
                       (T("Resources"), "resources"),
                       ]

        s3db.configure(tablename,
                       extra_fields = ("name",
                                       "end_date",
                                       "exercise",
                                       ),
                       list_fields = list_fields,
                       orderby = "event_event.name",
                       )

    settings.customise_event_event_resource = customise_event_event_resource

    # -------------------------------------------------------------------------
    def customise_event_event_controller(**attr):

        s3db = current.s3db
        s3 = current.response.s3

        # Modify Components
        s3db.add_components("event_event",
                            # Events have just a single Location
                            event_event_location = {"joinby": "event_id",
                                                    "multiple": False,
                                                    },
                            # Incidents are linked to Events, not created from them
                            # - not a link table though, so can't change the actuation
                            #event_incident = {"joinby": "event_id",
                            #                  },
                            )

        # Custom Browse
        from templates.WACOP.controllers import event_Browse, event_Profile
        set_method = s3db.set_method
        set_method("event", "event",
                   method = "browse",
                   action = event_Browse)

        # Custom Profile
        set_method("event", "event",
                   method = "custom",
                   action = event_Profile)

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard postp
            if callable(standard_prep):
                result = standard_prep(r)

            cname = r.component_name
            if not cname:
                f = s3db.event_event.event_type_id
                f.readable = f.writable = False

            elif cname == "task":
                from gluon import IS_EMPTY_OR
                from s3 import IS_ONE_OF, S3SQLCustomForm, S3SQLInlineComponent
                itable = s3db.event_incident
                query = (itable.event_id == r.id) & \
                        (itable.closed == False) & \
                        (itable.deleted == False)
                set = current.db(query)
                f = s3db.event_task.incident_id
                f.requires = IS_EMPTY_OR(
                                IS_ONE_OF(set, "event_incident.id",
                                          f.represent,
                                          orderby="event_incident.name",
                                          sort=True))
                crud_form = S3SQLCustomForm(
                    S3SQLInlineComponent("incident",
                                         fields = [("", "incident_id")],
                                         label = T("Incident"),
                                         multiple = False,
                                         filterby = dict(field = "event_id",
                                                         options = r.id,
                                                         )
                                         ),
                    "name",
                    "description",
                    "source",
                    "priority",
                    "pe_id",
                    "date_due",
                    "status",
                    "comments",
                    )
                r.component.configure(crud_form = crud_form,
                                      )
                
            elif r.representation == "popup" and r.get_vars.get("view"):
                # Popups for lists in Parent Event of Incident Screen or Event Profile header
                # No Title since this is on the Popup
                s3.crud_strings["event_event"].title_display = ""
                # No create button & Tweak list_fields
                if cname == "incident":
                    list_fields = ["date",
                                   "name",
                                   "incident_type_id",
                                   ]
                elif cname == "group":
                    list_fields = ["incident_id",
                                   "group_id",
                                   "status_id",
                                   ]
                elif cname == "post":
                    list_fields = ["date",
                                   "series_id",
                                   "priority",
                                   "status_id",
                                   "body",
                                   ]
                else:
                    # Shouldn't get here but want to avoid crashes
                    list_fields = []
                r.component.configure(insertable = False,
                                      list_fields = list_fields,
                                      )

            return True
        s3.prep = custom_prep

        # Custom rheader tabs
        attr = dict(attr)
        attr["rheader"] = wacop_rheader

        return attr

    settings.customise_event_event_controller = customise_event_event_controller

    # -------------------------------------------------------------------------
    def customise_event_incident_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod

        s3db = current.s3db

        # Virtual Fields
        itable = s3db.event_incident
        #append = itable._virtual_methods.append

        def incident_name(row):
            return A(row["event_incident.name"],
                     _href = URL(c="event", f="incident",
                                 args=[row["event_incident.id"], "custom"],
                                 extension = "", # ensure no .aadata
                                 ),
                     )
        #append(Field.Method("name_click", incident_name))
        itable.name_click = s3_fieldmethod("name_click",
                                           incident_name,
                                           # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                           represent = lambda v: v,
                                           search_field = "name",
                                           )

        def incident_status(row):
            if row["event_incident.exercise"]:
                status = T("Testing")
            elif not row["event_incident.end_date"]:
                status = T("Open")
            else:
                status = T("Closed")
            return status
        #append(Field.Method("status", incident_status))
        itable.status = s3_fieldmethod("status", incident_status)

        if r.method == "browse" or r.get_vars.get("browse"):
            # Incident Browse
            db = current.db
            ertable = s3db.event_team
            def incident_resources(row):
                query = (ertable.event_id == row["event_incident.id"]) & \
                        (ertable.deleted == False)
                resources = db(query).count()
                return resources
            #append(Field.Method("resources", incident_resources))
            itable.resources = s3_fieldmethod("resources", incident_resources)

            ettable = s3db.event_tag
            ttable = s3db.cms_tag
            def incident_tags(row):
                query = (ettable.incident_id == row["event_incident.id"]) & \
                        (ettable.deleted == False) & \
                        (ettable.tag_id == ttable.id)
                tags = db(query).select(ttable.name)
                if tags:
                    tags = [t.name for t in tags]
                    tags = ", ".join(tags)
                    return tags
                else:
                    return current.messages["NONE"]
            #append(Field.Method("tags", incident_tags))
            itable.tags = s3_fieldmethod("tags", incident_tags)

            atable = db.s3_audit
            stable = s3db.sync_repository
            def incident_source(row):
                query = (atable.record_id == row["event_incident.id"]) & \
                        (atable.tablename == "event_incident") & \
                        (atable.repository_id == stable.id)
                repo = db(query).select(stable.name,
                                        limitby=(0, 1)
                                        ).first()
                if repo:
                    return repo.name
                else:
                    return T("Internal")
            #append(Field.Method("source", incident_source))
            itable.source = s3_fieldmethod("source", incident_source)

            list_fields = [(T("Name"), "name_click"),
                           (T("Status"), "status"),
                           (T("Type"), "incident_type_id"),
                           (T("Zero Hour"), "date"),
                           (T("Closed"), "end_date"),
                           (T("City"), "location.location_id.L3"),
                           (T("State"), "location.location_id.L1"),
                           (T("Tags"), "tags"),
                           (T("Resources"), "resources"),
                           (T("Event"), "event_id"),
                           ]
        else:
            # Homepage or Event Profile
            list_fields = [(T("Name"), "name_click"),
                           (T("Status"), "status"),
                           (T("Type"), "incident_type_id"),
                           "location_id",
                           (T("Start"), "date"),
                           ]

        s3db.configure(tablename,
                       extra_fields = ("name",
                                       "end_date",
                                       "exercise",
                                       ),
                       list_fields = list_fields,
                       orderby = "event_incident.name",
                       )

    settings.customise_event_incident_resource = customise_event_incident_resource

    # -------------------------------------------------------------------------
    def customise_event_incident_controller(**attr):

        s3db = current.s3db
        response = current.response
        s3 = response.s3

        # Load normal model to be able to override configuration
        table = s3db.event_incident

        table.event_id.readable = table.event_id.writable = True

        # Custom Browse
        from templates.WACOP.controllers import incident_Browse, incident_Profile
        set_method = s3db.set_method
        set_method("event", "incident",
                   method = "browse",
                   action = incident_Browse)

        # Custom Profile
        set_method("event", "incident",
                   method = "custom",
                   action = incident_Profile)

        #s3.crud_strings["event_incident"].title_list =  T("Browse Incidents")

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard postp
            if callable(standard_prep):
                result = standard_prep(r)

            if r.method == "assign":
                current.menu.main = ""

            elif r.component_name == "group":
                if r.component_id:
                    f = s3db.event_team.group_id
                    f.writable = False
                    f.comment = None
                s3db.configure("event_team",
                               update_next = r.url(),
                               )

            elif r.component_name == "task":
                from s3 import S3SQLCustomForm
                crud_form = S3SQLCustomForm("name",
                                            "description",
                                            "source",
                                            "priority",
                                            "pe_id",
                                            "date_due",
                                            "status",
                                            "comments",
                                            )
                r.component.configure(crud_form = crud_form,
                                      )

            elif r.representation == "popup":
                if not r.component:
                    if r.get_vars.get("set_event"):
                        # Popup just used to link to Event
                        #s3.crud_strings["event_incident"].title_update =  T("Add to Event")
                        from s3 import S3SQLCustomForm
                        crud_form = S3SQLCustomForm("event_id",
                                                    )
                        s3db.configure("event_incident",
                                       crud_form = crud_form,
                                       )
                #elif r.component_name == "post":
                #    from s3 import S3SQLCustomForm

                #    crud_form = S3SQLCustomForm("body",
                #                                )

                #    s3db.configure("cms_post",
                #                   crud_form = crud_form,
                #                   )

            return True
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if r.interactive and isinstance(output, dict):
                if r.method == "assign":
                    # No Top Menu
                    current.menu.main = ""
                    # Custom View to waste less space inside popup
                    import os
                    response.view = os.path.join(r.folder,
                                                 "modules", "templates",
                                                 "WACOP", "views",
                                                 "assign.html")

                elif r.component_name == "group":
                    output["title"] = T("Resource Details")

                #elif r.component_name == "post":
                #    # Add Tags - no, do client-side
                #    output["form"].append()

                #else:
                #    # Summary or Profile pages
                #    # Additional styles
                #    s3.external_stylesheets += ["https://cdn.knightlab.com/libs/timeline3/latest/css/timeline.css",
                #                                "https://fonts.googleapis.com/css?family=Merriweather:400,700|Source+Sans+Pro:400,700",
                #                                ]

                    #if r.method == "summary":
                    #    # Open the Custom profile page instead of the normal one
                    #    from gluon import URL
                    #    from s3 import S3CRUD
                    #    custom_url = URL(args = ["[id]", "custom"])
                    #    S3CRUD.action_buttons(r,
                    #                          read_url=custom_url,
                    #                          update_url=custom_url)

            return output
        s3.postp = custom_postp

        # Custom rheader tabs
        #attr = dict(attr)
        attr["rheader"] = wacop_rheader

        # No sidebar menu
        current.menu.options = None

        refresh = current.request.get_vars.get("refresh")
        if refresh:
            # Popup from Resource Browse
            current.menu.main = ""

            attr["rheader"] = wacop_rheader

            #from gluon import A, URL
            #attr["custom_crud_buttons"] = {"list_btn": A(T("Browse Resources"),
            #                                             _class="action-btn",
            #                                             _href=URL(c="pr", f="group", args="browse"),
            #                                             _id="list-btn",
            #                                             )
            #                               }
            attr["custom_crud_buttons"] = {"list_btn": "",
                                           }

            response = current.response
            if response.confirmation:
                script = '''self.parent.$('#%s').dataTable().fnReloadAjax()''' % refresh
                response.s3.jquery_ready.append(script)

        return attr

    settings.customise_event_incident_controller = customise_event_incident_controller

    # -------------------------------------------------------------------------
    def customise_event_human_resource_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod

        s3db = current.s3db

        # Virtual Fields
        # Always used from either the Event or Incident context
        f = r.function
        record_id = r.id
        ehrtable = s3db.event_human_resource
        hr_represent = ehrtable.human_resource_id.represent
        def hr_name(row):
            hr_id = row["event_human_resource.human_resource_id"]
            return A(hr_represent(hr_id),
                     _href = URL(c="event", f=f,
                                 args=[record_id, "human_resource", hr_id, "profile"],
                                 ),
                     )
        ehrtable.name_click = s3_fieldmethod("name_click",
                                             hr_name,
                                             # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                             # @ToDo: Bulk lookups
                                             represent = lambda v: v,
                                             search_field = "human_resource_id",
                                             )

        s3db.configure(tablename,
                       #crud_form = crud_form,
                       extra_fields = ("human_resource_id",
                                       ),
                       list_fields = [(T("Name"), "name_click"),
                                      (T("Title"), "human_resource_id$job_title_id"),
                                      "human_resource_id$organisation_id",
                                      (T("Email"), "human_resource_id$person_id$email.value"),
                                      (T("Phone"), "human_resource_id$person_id$phone.value"),
                                      "status",
                                      (T("Notes"), "comments"),
                                      ],
                       orderby = "event_human_resource.human_resource_id",
                       )

    settings.customise_event_human_resource_resource = customise_event_human_resource_resource

    # -------------------------------------------------------------------------
    def customise_event_organisation_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod

        s3db = current.s3db

        # Virtual Fields
        # Always used from either the Event or Incident context
        f = r.function
        record_id = r.id
        eotable = s3db.event_organisation
        org_represent = eotable.organisation_id.represent
        def org_name(row):
            organisation_id = row["event_organisation.organisation_id"]
            return A(org_represent(organisation_id),
                     _href = URL(c="event", f=f,
                                 args=[record_id, "organisation", organisation_id, "profile"],
                                 ),
                     )
        eotable.name_click = s3_fieldmethod("name_click",
                                            org_name,
                                            # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                            # @ToDo: Bulk lookups
                                            represent = lambda v: v,
                                            search_field = "organisation_id",
                                            )

        s3db.configure(tablename,
                       #crud_form = crud_form,
                       extra_fields = ("organisation_id",
                                       ),
                       list_fields = [(T("Name"), "name_click"),
                                      "status",
                                      "comments",
                                      ],
                       orderby = "event_organisation.organisation_id",
                       )

    settings.customise_event_organisation_resource = customise_event_organisation_resource

    # -------------------------------------------------------------------------
    def customise_event_team_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod, S3SQLCustomForm

        s3db = current.s3db
        ertable = s3db.event_team

        #ertable.group_id.label = T("Resource")

        # Form
        # @ToDo: Have both Team & Event_Team in 1 form
        crud_form = S3SQLCustomForm("incident_id",
                                    "group_id",
                                    "status_id",
                                    )

        # Virtual Fields
        # @ToDo: Replace with a link to Popup a dataTable of the List of Updates
        incident_id = r.get_vars.get("~.incident_id")
        if incident_id:
            f = "incident"
            record_id = incident_id
        else:
            event_id = r.get_vars.get("~.event_id")
            if event_id:
                f = "event"
                record_id = event_id
            else:
                f = r.function
                record_id = r.id
        group_represent = ertable.group_id.represent
        if f in ("group", "team"):
            # Resource Browse (inc aadata)
            def team_name(row):
                group_id = row["event_team.group_id"]
                return A(group_represent(group_id),
                         _href = URL(c="event", f="incident",
                                     args = [row["event_team.incident_id"], "group", group_id, "read"],
                                     vars = {"refresh": "custom-list-event_team",
                                             },
                                     extension = "", # ensure no .aadata
                                     ),
                         _class = "s3_modal",
                         )
        else:
            # Event Profile or Incident Profile
            def team_name(row):
                group_id = row["event_team.group_id"]
                return A(group_represent(group_id),
                         _href = URL(c="event", f=f,
                                     args = [record_id, "group", group_id, "read"],
                                     vars = {"refresh": "custom-list-event_team",
                                             },
                                     extension = "", # ensure no .aadata
                                     ),
                         _class = "s3_modal",
                         )
        ertable.name_click = s3_fieldmethod("name_click",
                                            team_name,
                                            # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                            # @ToDo: Bulk lookups
                                            represent = lambda v: v,
                                            search_field = "group_id",
                                            )

        if f in ("group", "team"):
            # Resource Browse (inc aadata)
            list_fields = [(T("Group"), "name_click"),
                           "incident_id",
                           "status_id",
                           ]
        else:
            # Event Profile or Incident Profile
            list_fields = [(T("Name"), "name_click"),
                           "incident_id",
                           "status_id",
                           ]

        s3db.configure(tablename,
                       crud_form = crud_form,
                       extra_fields = ("group_id",
                                       ),
                       list_fields = list_fields,
                       orderby = "pr_group.name",
                       )

    settings.customise_event_team_resource = customise_event_team_resource

    # -------------------------------------------------------------------------
    def customise_pr_group_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod, S3SQLCustomForm, S3SQLInlineComponent

        db = current.db
        s3db = current.s3db
        table = s3db.pr_group

        current.response.s3.crud_strings[tablename] = Storage(
            label_create = T("Create Resource"),
            title_display = T("Resource Details"),
            title_list = T("Resources"),
            title_update = T("Edit Resource"),
            label_list_button = T("List Resources"),
            label_delete_button = T("Delete Resource"),
            msg_record_created = T("Resource added"),
            msg_record_modified = T("Resource updated"),
            msg_record_deleted = T("Resource deleted"),
            msg_list_empty = T("No Resources currently registered"))

        field = table.status_id
        field.readable = field.writable = True

        crud_form = S3SQLCustomForm((T("Name"), "name"),
                                    "status_id",
                                    S3SQLInlineComponent("organisation_team",
                                                         fields = [("", "organisation_id")],
                                                         label = T("Organization"),
                                                         multiple = False,
                                                         ),
                                    "comments",
                                    )

        # Virtual Fields
        def team_name(row):
            return A(row["pr_group.name"],
                     _href = URL(c="pr", f="group",
                                 args = [row["pr_group.id"], "read"],
                                 vars = {"refresh": "custom-list-pr_group",
                                         },
                                 extension = "", # ensure no .aadata
                                 ),
                     _class = "s3_modal",
                     )
        table.name_click = s3_fieldmethod("name_click",
                                          team_name,
                                          # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                          # @ToDo: Bulk lookups
                                          represent = lambda v: v,
                                          search_field = "name",
                                          )

        utable = s3db.cms_post_team
        gfield = utable.group_id
        query = (utable.deleted == False)
        def updates(row):
            group_id = row["pr_group.id"]
            count = db(query & (gfield == group_id)).count()
            if count:
                return A(count,
                         _href = URL(c="cms", f="post",
                                     args = ["datalist.popup"],
                                     vars = {"post_team.group_id": group_id},
                                     ),
                         _class="s3_modal",
                         )
            else:
                return 0
        table.updates = s3_fieldmethod("updates",
                                       updates,
                                       # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                       # @ToDo: Bulk lookups
                                       represent = lambda v: v,
                                       #search_field = "name",
                                       )

        list_fields = [(T("Name"), "name_click"),
                       "status_id",
                       (T("Current Incident"), "active_incident__link.incident_id"),
                       (T("Organization"), "organisation_team.organisation_id"),
                       # Replaced with VF
                       #(T("Updates"), "post_team.post_id"),
                       (T("Updates"), "updates"),
                       ]

        s3db.configure(tablename,
                       crud_form = crud_form,
                       extra_fields = ("name",
                                       ),
                       list_fields = list_fields,
                       )

    settings.customise_pr_group_resource = customise_pr_group_resource

    # -------------------------------------------------------------------------
    def customise_pr_group_controller(**attr):

        # Custom Browse
        from templates.WACOP.controllers import resource_Browse
        current.s3db.set_method("pr", "group",
                                method = "browse",
                                action = resource_Browse)

        # No sidebar menu
        current.menu.options = None

        refresh = current.request.get_vars.get("refresh")
        if refresh:
            # Popup from Browse
            current.menu.main = ""

            attr["rheader"] = wacop_rheader

            #from gluon import A, URL
            #attr["custom_crud_buttons"] = {"list_btn": A(T("Browse Resources"),
            #                                             _class="action-btn",
            #                                             _href=URL(args="browse"),
            #                                             _id="list-btn",
            #                                             )
            #                               }
            attr["custom_crud_buttons"] = {"list_btn": "",
                                           }

            response = current.response
            if response.confirmation:
                script = '''self.parent.$('#%s').dataTable().fnReloadAjax()''' % refresh
                response.s3.jquery_ready.append(script)

        return attr

    settings.customise_pr_group_controller = customise_pr_group_controller

    # -------------------------------------------------------------------------
    def customise_pr_person_controller(**attr):

        # Custom Profile
        from templates.WACOP.controllers import person_Dashboard
        current.s3db.set_method("pr", "person",
                                method = "dashboard",
                                action = person_Dashboard)

        # No sidebar menu
        current.menu.options = None

        return attr

    settings.customise_pr_person_controller = customise_pr_person_controller

    # -------------------------------------------------------------------------
    def customise_project_task_resource(r, tablename):

        from gluon import A, URL
        from s3 import s3_fieldmethod

        s3db = current.s3db

        # Virtual Fields
        # Always used from either the Event or Incident context
        f = r.function
        record_id = r.id
        def task_name(row):
            return A(row["project_task.name"],
                     _href = URL(c="event", f=f,
                                 args=[record_id, "task", row["project_task.id"], "profile"],
                                 ),
                     )
        s3db.project_task.name_click = s3_fieldmethod("name_click",
                                                      task_name,
                                                      # over-ride the default represent of s3_unicode to prevent HTML being rendered too early
                                                      represent = lambda v: v,
                                                      search_field = "name",
                                                      )

        s3db.configure(tablename,
                       #crud_form = crud_form,
                       extra_fields = ("name",
                                       ),
                       list_fields = ["status",
                                      (T("Description"), "name_click"),
                                      (T("Created"), "created_on"),
                                      (T("Due"), "date_due"),
                                      ],
                       orderby = "project_task.date_due",
                       )

    settings.customise_project_task_resource = customise_project_task_resource

# =============================================================================
def event_team_rheader(incident_id, group_id, updates=False):
    """
        RHeader for event_team
    """

    from gluon import A, DIV, SPAN, TABLE, TR, TH, URL

    T = current.T

    table = current.s3db.event_team
    query = (table.incident_id == incident_id) & \
            (table.group_id == group_id)
    record = current.db(query).select(table.status_id,
                                      limitby=(0, 1),
                                      ).first()

    rheader_tabs = DIV(SPAN(A(T("Resource Details"),
                              _href=URL(c="event", f="incident",
                                        args = [incident_id, "group", group_id],
                                        vars = {"refresh": "custom-list-event_team",
                                                },
                                        ),
                              _id="rheader_tab_group",
                              ),
                            _class="tab_here" if not updates else "tab_other",
                            ),
                       SPAN(A(T("Updates"),
                              _href=URL(c="pr", f="group",
                                        args = [group_id, "post", "datalist"],
                                        vars = {"incident_id": incident_id,
                                                "refresh": "custom-list-event_team",
                                                }
                                        ),
                              _id="rheader_tab_post",
                              ),
                            _class="tab_here" if updates else "tab_last",
                            ),
                       _class="tabs",
                       )
    rheader = DIV(TABLE(TR(TH("%s: " % table.group_id.label),
                           table.group_id.represent(group_id),
                           ),
                        TR(TH("%s: " % table.incident_id.label),
                           table.incident_id.represent(incident_id),
                           ),
                        TR(TH("%s: " % table.status_id.label),
                           table.status_id.represent(record.status_id),
                           ),
                        ),
                  rheader_tabs)
    return rheader
    
# =============================================================================
def pr_group_rheader(r):
    """
        RHeader for pr_group
    """

    from gluon import A, DIV, SPAN, TABLE, TR, TH, URL

    T = current.T
    s3db = current.s3db
    group_id = r.id
    record = r.record
    table = s3db.pr_group

    updates = r.component

    ltable = s3db.org_organisation_team
    query = (ltable.group_id == group_id) & \
            (ltable.deleted == False)
    org = current.db(query).select(ltable.organisation_id,
                                   limitby=(0, 1)
                                   ).first()
    if org:
        org = TR(TH("%s: " % ltable.organisation_id.label),
                 ltable.organisation_id.represent(org.organisation_id),
                 )
    else:
        org = ""

    rheader_tabs = DIV(SPAN(A(T("Resource Details"),
                              _href=URL(c="pr", f="group",
                                        args = [group_id],
                                        vars = {"refresh": "custom-list-pr_group",
                                                },
                                        ),
                              _id="rheader_tab_group",
                              ),
                            _class="tab_here" if not updates else "tab_other",
                            ),
                       SPAN(A(T("Updates"),
                              _href=URL(c="pr", f="group",
                                        args = [group_id, "post", "datalist"],
                                        vars = {"refresh": "custom-list-pr_group",
                                                },
                                        ),
                              _id="rheader_tab_post",
                              ),
                            _class="tab_here" if updates else "tab_last",
                            ),
                       _class="tabs",
                       )
    rheader = DIV(TABLE(TR(TH("%s: " % table.name.label),
                           record.name,
                           ),
                        TR(TH("%s: " % table.status_id.label),
                           table.status_id.represent(record.status_id),
                           ),
                        org,
                        TR(TH("%s: " % table.comments.label),
                           record.comments or current.messages["NONE"],
                           ),
                        ),
                  rheader_tabs)
    return rheader

# =============================================================================
def wacop_rheader(r, tabs=[]):
    """ WACOP custom resource headers """

    if r.representation != "html":
        # Resource headers only used in interactive views
        return None

    from s3 import s3_rheader_resource, S3ResourceHeader

    tablename, record = s3_rheader_resource(r)
    if tablename != r.tablename:
        resource = current.s3db.resource(tablename, id=record.id)
    else:
        resource = r.resource

    rheader = None
    rheader_fields = []

    if record:
        T = current.T

        if tablename == "pr_group":

            incident_id = r.get_vars.get("incident_id")
            if incident_id and r.component_name == "post":
                # Look like event_team details
                group_id = r.id
                rheader = event_team_rheader(incident_id, group_id, updates=True)
                return rheader
            else:
                # Normal
                rheader = pr_group_rheader(r)
                return rheader

        elif tablename == "event_incident":
            if r.component_name == "group":
                incident_id = r.id
                group_id = r.component_id
                rheader = event_team_rheader(incident_id, group_id, updates=False)
                return rheader
            else:
                # Unused
                return None

                if not tabs:
                    tabs = [(T("Incident Details"), None),
                            (T("Units"), "group"),
                            (T("Tasks"), "task"),
                            (T("Updates"), "post"),
                            ]

                rheader_fields = [["name"],
                                  ["date"],
                                  ["comments"],
                                  ]

        elif tablename == "event_event":
            # No normal workflows use this

            if not tabs:
                tabs = [(T("Event Details"), None),
                        (T("Incidents"), "incident"),
                        (T("Units"), "group"),
                        (T("Tasks"), "task"),
                        (T("Updates"), "post"),
                        ]

            rheader_fields = [["name"],
                              ["start_date"],
                              ["comments"],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )
    return rheader

# END =========================================================================
