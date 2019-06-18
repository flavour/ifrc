# -*- coding: utf-8 -*-

from collections import OrderedDict

from gluon import current
from gluon.storage import Storage

def config(settings):
    """
        Logistics generic template

        Based on:
        Relief Goods and Inventory Management System
        http://eden.sahanafoundation.org/wiki/Deployments/Philippines/RGIMS
    """

    T = current.T

    settings.base.system_name = "Sahana Logistics Management"
    settings.base.system_name_short = "Sahana Logs"

    # Pre-Populate
    settings.base.prepopulate += ("Logistics",)
    #settings.base.prepopulate_demo += ("Projects/Demo",)

    # Theme
    #settings.base.theme = "Logistics"

    settings.auth.registration_requests_organisation = True
    settings.auth.registration_requests_site = True

    # Security Policy
    settings.security.policy = 6 # Site-specific restrictions
    settings.security.map = True

    def rgims_realm_entity(table, row):
        """
            Assign a Realm Entity to records
        """

        tablename = table._tablename
        if tablename not in ("inv_recv", "inv_send"):
            # Normal lookup
            return 0

        # For these tables we need to assign the site_id's realm not organisation_id's
        db = current.db
        stable = db.org_site
        record = db(stable.site_id == row.site_id).select(stable.realm_entity,
                                                          limitby=(0, 1)
                                                          ).first()
        if record:
            return record.realm_entity

        # Normal lookup
        return 0

    settings.auth.realm_entity = rgims_realm_entity

    # Enable this for a UN-style deployment
    #settings.ui.cluster = True
    # Enable this to use the label 'Camp' instead of 'Shelter'
    #settings.ui.camp = True

    # Requests
    settings.req.use_commit = False
    #settings.req.req_form_name = "Request Issue Form"
    #settings.req.req_shortname = "RIS"
    # Restrict the type of requests that can be made, valid values in the
    # list are ["Stock", "People", "Other"]. If this is commented out then
    # all types will be valid.
    settings.req.req_type = ["Stock"]

    # Inventory Management
    # Uncomment if you need a simpler (but less accountable) process for managing stock levels
    settings.inv.direct_stock_edits = True
    #settings.inv.send_form_name = "Tally Out Sheet"
    #settings.inv.send_short_name = "TOS"
    #settings.inv.send_ref_field_name = "Tally Out Number"
    #settings.inv.recv_form_name = "Acknowledgement Receipt for Donations Received Form"
    #settings.inv.recv_shortname = "ARDR"
    #settings.inv.recv_type = {
    #    #0: T("-"),
    #    #1: T("Other Warehouse"),
    #    32: T("Donation"),
    #    33: T("Foreign Donation"),
    #    34: T("Local Purchases"),
    #    35: T("Confiscated Goods from Bureau Of Customs")
    #    }

    # -------------------------------------------------------------------------
    # Setup
    settings.setup.wizard_questions += [{"question": "Will you record data for multiple Organisations?",
                                         "setting": "hrm.multiple_orgs",
                                         "options": {True: "Yes", False: "No"},
                                         },
                                        {"question": "Do you need support for Branch Organisations?",
                                         "setting": "org.branches",
                                         "options": {True: "Yes", False: "No"},
                                         },
                                        ]

    # Comment/uncomment modules here to disable/enable them
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
        ("setup", Storage(
            name_nice = T("Setup"),
            #description = "Configuration Wizard",
            restricted = False,
            module_type = None  # No Menu
        )),
        #("sync", Storage(
        #        name_nice = T("Synchronization"),
        #        #description = "Synchronization",
        #        restricted = True,
        #        access = "|1|",     # Only Administrators can see this module in the default menu & access the controller
        #        module_type = None  # This item is handled separately for the menu
        #    )),
        ("gis", Storage(
                name_nice = T("Map"),
                #description = "Situation Awareness & Geospatial Analysis",
                restricted = True,
                module_type = 10,
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
                module_type = 10
            )),
        # All modules below here should be possible to disable safely
        ("hrm", Storage(
                name_nice = T("Staff"),
                #description = "Human Resources Management",
                restricted = True,
                module_type = 10,
            )),
        ("cms", Storage(
              name_nice = T("Content Management"),
              #description = "Content Management System",
              restricted = True,
              module_type = 10,
          )),
        ("doc", Storage(
                name_nice = T("Documents"),
                #description = "A library of digital resources, such as photos, documents and reports",
                restricted = True,
                module_type = 10,
            )),
        ("msg", Storage(
                name_nice = T("Messaging"),
                #description = "Sends & Receives Alerts via Email & SMS",
                restricted = True,
                # The user-visible functionality of this module isn't normally required. Rather it's main purpose is to be accessed from other modules.
                module_type = None,
            )),
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
                module_type = 1
            )),
        ("asset", Storage(
                name_nice = T("Assets"),
                #description = "Recording and Assigning Assets",
                restricted = True,
                module_type = 3,
            )),
        # Vehicle depends on Assets
        ("vehicle", Storage(
                name_nice = T("Vehicles"),
                #description = "Manage Vehicles",
                restricted = True,
                module_type = 10,
            )),
        # Very basic module: Needs work to be useful
        ("proc", Storage(
                name_nice = T("Procurement"),
                #description = "Ordering & Purchasing of Goods & Services",
                restricted = True,
                module_type = 10,
            )),
        ("req", Storage(
            name_nice = T("Requests"),
            #description = "Manage requests for supplies, assets, staff or other resources. Matches against Inventories where supplies are requested.",
            restricted = True,
            module_type = 2,
        )),
        #("cr", Storage(
        #        name_nice = T("Shelters"),
        #        #description = "Tracks the location, capacity and breakdown of victims in Shelters",
        #        restricted = True,
        #       module_type = 1,
        #    )),
    ])

# END =========================================================================
