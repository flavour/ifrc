# -*- coding: utf-8 -*-

try:
    # Python 2.7
    from collections import OrderedDict
except:
    # Python 2.6
    from gluon.contrib.simplejson.ordered_dict import OrderedDict

from gluon import current
from gluon.storage import Storage

def config(settings):
    """
        Template settings: 'Skeleton' designed to be copied to quickly create
                           custom templates

        All settings which are to configure a specific template are located
        here. Deployers should ideally not need to edit any other files outside
        of their template folder.
    """

    T = current.T

    settings.base.system_name = T("Sahana Disaster Management System")
    settings.base.system_name_short = T("NEOC Sahana")

    # PrePopulate data
    settings.base.prepopulate = ("NepalNEOC", "default/users")

    # Theme (folder to use for views/layout.html)
    settings.base.theme = "NepalNEOC"

    # Authentication settings
    # Should users be allowed to register themselves?
    #settings.security.self_registration = False
    # Do new users need to verify their email address?
    #settings.auth.registration_requires_verification = True
    # Do new users need to be approved by an administrator prior to being able to login?
    #settings.auth.registration_requires_approval = True
    #settings.auth.registration_requests_organisation = True

    # Approval emails get sent to all admins
    settings.mail.approver = "ADMIN"

    # Restrict the Location Selector to just certain countries
    # NB This can also be over-ridden for specific contexts later
    # e.g. Activities filtered to those of parent Project
    settings.gis.countries = ("NP",)
    # Uncomment to display the Map Legend as a floating DIV
    settings.gis.legend = "float"
    # Uncomment to Disable the Postcode selector in the LocationSelector
    #settings.gis.postcode_selector = False # @ToDo: Vary by country (include in the gis_config!)
    # Uncomment to show the Print control:
    # http://eden.sahanafoundation.org/wiki/UserGuidelines/Admin/MapPrinting
    #settings.gis.print_button = True

    # L10n settings
    # Languages used in the deployment (used for Language Toolbar & GIS Locations)
    # http://www.loc.gov/standards/iso639-2/php/code_list.php
    settings.L10n.languages = OrderedDict([
    #    ("ar", "العربية"),
    #    ("bs", "Bosanski"),
        ("en", "English"),
    #    ("fr", "Français"),
    #    ("de", "Deutsch"),
    #    ("el", "ελληνικά"),
    #    ("es", "Español"),
    #    ("it", "Italiano"),
    #    ("ja", "日本語"),
    #    ("km", "ភាសាខ្មែរ"),
    #    ("ko", "한국어"),
        ("ne", "नेपाली"),          # Nepali
    #    ("prs", "دری"), # Dari
    #    ("ps", "پښتو"), # Pashto
    #    ("pt", "Português"),
    #    ("pt-br", "Português (Brasil)"),
    #    ("ru", "русский"),
    #    ("tet", "Tetum"),
    #    ("tl", "Tagalog"),
    #    ("tr", "Türkçe"),
    #    ("ur", "اردو"),
    #    ("vi", "Tiếng Việt"),
    #    ("zh-cn", "中文 (简体)"),
    #    ("zh-tw", "中文 (繁體)"),
    ])
    # Default language for Language Toolbar (& GIS Locations in future)
    #settings.L10n.default_language = "en"
    # Uncomment to Hide the language toolbar
    #settings.L10n.display_toolbar = False
    # Default timezone for users
    settings.L10n.utc_offset = "+0545"
    # Number formats (defaults to ISO 31-0)
    # Decimal separator for numbers (defaults to ,)
    settings.L10n.decimal_separator = "."
    # Thousands separator for numbers (defaults to space)
    settings.L10n.thousands_separator = ","
    # Uncomment this to Translate Layer Names
    #settings.L10n.translate_gis_layer = True
    # Uncomment this to Translate Location Names
    #settings.L10n.translate_gis_location = True
    # Uncomment this to Translate Organisation Names/Acronyms
    #settings.L10n.translate_org_organisation = True
    # Finance settings
    #settings.fin.currencies = {
    #    "EUR" : T("Euros"),
    #    "GBP" : T("Great British Pounds"),
    #    "USD" : T("United States Dollars"),
    #}
    #settings.fin.currency_default = "USD"

    # Security Policy
    # http://eden.sahanafoundation.org/wiki/S3AAA#System-widePolicy
    # 1: Simple (default): Global as Reader, Authenticated as Editor
    # 2: Editor role required for Update/Delete, unless record owned by session
    # 3: Apply Controller ACLs
    # 4: Apply both Controller & Function ACLs
    # 5: Apply Controller, Function & Table ACLs
    # 6: Apply Controller, Function, Table ACLs and Entity Realm
    # 7: Apply Controller, Function, Table ACLs and Entity Realm + Hierarchy
    # 8: Apply Controller, Function, Table ACLs, Entity Realm + Hierarchy and Delegations
    #
    settings.security.policy = 7 # Organisation-ACLs, hierarchical realms

    #settings.project.mode_3w = True
    settings.project.activities = True
    settings.project.sectors = True

    settings.event.incident_impact_tab = True

    # -------------------------------------------------------------------------
    def customise_event_incident_controller(**attr):

        db = current.db
        s3db = current.s3db

        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            if r.method in ("report", "summary"):

                indicators = ("Death Total",
                              "Injured Total",
                              "Missing Total",
                              "Fully Damaged Cemented House",
                              "Partially Damaged Cemented House",
                              )
                report_facts = [(T("Number of Incidents"), "count(id)"),
                                ]

                ptable = s3db.stats_parameter
                query = ptable.name.belongs(indicators)
                rows = db(query).select(ptable.parameter_id,
                                        ptable.name,
                                        )
                for row in rows:
                    name = row.name
                    parameter_id = row.parameter_id
                    component_name = "impact_%s" % "_".join([s.lower() for s in name.split()])
                    s3db.add_components("event_incident",
                                        stats_impact={"name": component_name,
                                                      "link": "event_event_impact",
                                                      "joinby": "incident_id",
                                                      "key": "impact_id",
                                                      "filterby": "parameter_id",
                                                      "filterfor": parameter_id,
                                                      },
                                        )
                    report_facts.append((T(name), "sum(%s.value)" % component_name))

                report_axis = ["event_id",
                               "incident_type_id",
                               ]
                default_axis = None
                levels = current.gis.get_relevant_hierarchy_levels()
                for level in levels:
                    lfield = "location_id$%s" % level
                    if not default_axis:
                        default_axis = lfield
                    report_axis.append(lfield)
                if not default_axis:
                    default_axis = "event_id"

                report_options = {
                        "rows": report_axis,
                        "cols": report_axis,
                        "fact": report_facts,
                        "defaults": {
                            "rows": default_axis,
                            "cols": "incident_type_id",
                            "fact": "count(id)",
                        }
                    }
                resource.configure(report_options=report_options)


            if r.interactive or r.representation in "aadata":

                if not r.component:
                    table = resource.table

                    # Show event_id
                    field = table.event_id
                    field.readable = field.writable = True

                    # List fields
                    list_fields = ["event_id",
                                   "name",
                                   "incident_type_id",
                                   "location_id",
                                   "zero_hour",
                                   "exercise",
                                   "closed",
                                   "comments",
                                   ]

                    # Filter widgets
                    from s3 import S3TextFilter, S3OptionsFilter, S3DateFilter, S3LocationFilter
                    filter_widgets = [S3TextFilter(field=["name",
                                                          "comments",
                                                          ]),
                                      S3OptionsFilter(field="event_id",
                                                      ),
                                      S3OptionsFilter(field="incident_type_id",
                                                      ),
                                      S3DateFilter(field="zero_hour",
                                                   ),
                                      S3LocationFilter(field="location_id",
                                                       ),
                                      ]

                    # Update table configuration
                    resource.configure(filter_widgets=filter_widgets,
                                       list_fields=list_fields,
                                       )

                elif r.component_name == "task":
                    # Custom Form
                    from s3 import S3SQLCustomForm, S3SQLInlineComponent
                    crud_fields = ["name",
                                   "description",
                                   "priority",
                                   "pe_id",
                                   "date_due",
                                   "status",
                                   ]
                    crud_form = S3SQLCustomForm(*crud_fields)
                    list_fields = ["priority",
                                   "name",
                                   "description",
                                   "pe_id",
                                   "status",
                                   "date_due",
                                   ]
                    r.component.configure(crud_form=crud_form,
                                          list_fields=list_fields,
                                          copyable=False,
                                          )
            return result
        s3.prep = custom_prep

        return attr

    settings.customise_event_incident_controller = customise_event_incident_controller
    # -------------------------------------------------------------------------
    # Comment/uncomment modules here to disable/enable them
    # Modules menu is defined in modules/eden/menu.py
    settings.modules = OrderedDict([
        # Core modules which shouldn't be disabled
        ("default", Storage(
            name_nice = T("Home"),
            restricted = False, # Use ACLs to control access to this module
            access = None,      # All Users (inc Anonymous) can see this module in the default menu & access the controller
            module_type = None  # This item is not shown in the menu
        )),
        ("admin", Storage(
            name_nice = T("Administration"),
            #description = "Site Administration",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
            module_type = None  # This item is handled separately for the menu
        )),
        ("appadmin", Storage(
            name_nice = T("Administration"),
            #description = "Site Administration",
            restricted = True,
            module_type = None  # No Menu
        )),
        ("errors", Storage(
            name_nice = T("Ticket Viewer"),
            #description = "Needed for Breadcrumbs",
            restricted = False,
            module_type = None  # No Menu
        )),
        #("sync", Storage(
        #    name_nice = T("Synchronization"),
        #    #description = "Synchronization",
        #    restricted = True,
        #    access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        #    module_type = None  # This item is handled separately for the menu
        #)),
        #("tour", Storage(
        #    name_nice = T("Guided Tour Functionality"),
        #    module_type = None,
        #)),
        #("translate", Storage(
        #    name_nice = T("Translation Functionality"),
        #    #description = "Selective translation of strings based on module.",
        #    module_type = None,
        #)),
        ("gis", Storage(
            name_nice = T("Map"),
            #description = "Situation Awareness & Geospatial Analysis",
            restricted = True,
            module_type = 6,     # 6th item in the menu
        )),
        ("pr", Storage(
            name_nice = T("Person Registry"),
            #description = "Central point to record details on People",
            restricted = True,
            access = "|1|",     # Only Administrators can see this module in the default menu (access to controller is possible to all still)
            module_type = 10
        )),
        ("org", Storage(
            name_nice = T("Organizations"),
            #description = 'Lists "who is doing what & where". Allows relief agencies to coordinate their activities',
            restricted = True,
            module_type = 1
        )),
        ("hrm", Storage(
            name_nice = T("Staff"),
            #description = "Human Resources Management",
            restricted = True,
            module_type = 2,
        )),
        #("vol", Storage(
        #    name_nice = T("Volunteers"),
        #    #description = "Human Resources Management",
        #    restricted = True,
        #    module_type = 2,
        #)),
        #("cms", Storage(
        #  name_nice = T("Content Management"),
        #  #description = "Content Management System",
        #  restricted = True,
        #  module_type = 10,
        #)),
        ("doc", Storage(
           name_nice = T("Documents"),
           #description = "A library of digital resources, such as photos, documents and reports",
           restricted = True,
           module_type = 10,
        )),
        #("msg", Storage(
        #    name_nice = T("Messaging"),
        #    #description = "Sends & Receives Alerts via Email & SMS",
        #    restricted = True,
        #    # The user-visible functionality of this module isn't normally required. Rather it's main purpose is to be accessed from other modules.
        #    module_type = None,
        #)),
        # Needed for Req
        ("supply", Storage(
            name_nice = T("Supply Chain Management"),
            #description = "Used within Inventory Management, Request Management and Asset Management",
            restricted = True,
            module_type = None, # Not displayed
        )),
        ("inv", Storage(
           name_nice = T("Warehouses"),
           #description = "Receiving and Sending Items",
           restricted = True,
           module_type = 4
        )),
        ("asset", Storage(
           name_nice = T("Assets"),
           #description = "Recording and Assigning Assets",
           restricted = True,
           module_type = 5,
        )),
        # Vehicle depends on Assets
        #("vehicle", Storage(
        #    name_nice = T("Vehicles"),
        #    #description = "Manage Vehicles",
        #    restricted = True,
        #    module_type = 10,
        #)),
        ("req", Storage(
            name_nice = T("Requests"),
            #description = "Manage requests for supplies, assets, staff or other resources. Matches against Inventories where supplies are requested.",
            restricted = True,
            module_type = 10,
        )),
        ("project", Storage(
           name_nice = T("Projects"),
           #description = "Tracking of Projects, Activities and Tasks",
           restricted = True,
           module_type = 2
        )),
        ("cr", Storage(
            name_nice = T("Shelters"),
            #description = "Tracks the location, capacity and breakdown of victims in Shelters",
            restricted = True,
            module_type = 10
        )),
        ("hms", Storage(
            name_nice = T("Hospitals"),
            #description = "Helps to monitor status of hospitals",
            restricted = True,
            module_type = 10
        )),
        #("dvr", Storage(
        #   name_nice = T("Disaster Victim Registry"),
        #   #description = "Allow affected individuals & households to register to receive compensation and distributions",
        #   restricted = True,
        #   module_type = 10,
        #)),
        ("event", Storage(
           name_nice = T("Events"),
           #description = "Activate Events (e.g. from Scenario templates) for allocation of appropriate Resources (Human, Assets & Facilities).",
           restricted = True,
           module_type = 10,
        )),
        #("transport", Storage(
        #   name_nice = T("Transport"),
        #   restricted = True,
        #   module_type = 10,
        #)),
        ("stats", Storage(
            name_nice = T("Statistics"),
            #description = "Manages statistics",
            restricted = True,
            module_type = None,
        )),
    ])

# END =========================================================================