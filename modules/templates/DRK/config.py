# -*- coding: utf-8 -*-

import datetime

from collections import OrderedDict

from gluon import current, SPAN
from gluon.storage import Storage

from s3 import S3Method

# Limit after which a checked-out resident is reported overdue (days)
ABSENCE_LIMIT = 5

def config(settings):
    """
        DRK ("Village") Template:

        Case Management, Refugee Reception Center, German Red Cross
    """

    T = current.T

    settings.base.system_name = "Village"
    settings.base.system_name_short = "Village"

    # PrePopulate data
    settings.base.prepopulate += ("DRK", "default/users", "DRK/Demo")

    # Theme (folder to use for views/layout.html)
    settings.base.theme = "DRK"

    # Authentication settings
    # Should users be allowed to register themselves?
    settings.security.self_registration = False
    # Do new users need to verify their email address?
    #settings.auth.registration_requires_verification = True
    # Do new users need to be approved by an administrator prior to being able to login?
    #settings.auth.registration_requires_approval = True
    settings.auth.registration_requests_organisation = True
    settings.auth.registration_link_user_to = {"staff": T("Staff"),
                                               "volunteer": T("Volunteer"),
                                               }
    #settings.auth.registration_link_user_to_default = "staff"

    # Approval emails get sent to all admins
    settings.mail.approver = "ADMIN"

    # Restrict the Location Selector to just certain countries
    # NB This can also be over-ridden for specific contexts later
    # e.g. Activities filtered to those of parent Project
    settings.gis.countries = ("DE",)
    # Uncomment to display the Map Legend as a floating DIV
    settings.gis.legend = "float"
    # Uncomment to Disable the Postcode selector in the LocationSelector
    #settings.gis.postcode_selector = False # @ToDo: Vary by country (include in the gis_config!)
    # Uncomment to show the Print control:
    # http://eden.sahanafoundation.org/wiki/UserGuidelines/Admin/MapPrinting
    #settings.gis.print_button = True

    # Settings suitable for Housing Units
    # - move into customise fn if also supporting other polygons
    settings.gis.precision = 5
    settings.gis.simplify_tolerance = 0
    settings.gis.bbox_min_size = 0.001
    #settings.gis.bbox_offset = 0.007

    # L10n settings
    # Languages used in the deployment (used for Language Toolbar & GIS Locations)
    # http://www.loc.gov/standards/iso639-2/php/code_list.php
    settings.L10n.languages = OrderedDict([
       ("en", "English"),
       ("de", "Deutsch"),
    ])
    # Default language for Language Toolbar (& GIS Locations in future)
    settings.L10n.default_language = "de"
    # Uncomment to Hide the language toolbar
    #settings.L10n.display_toolbar = False
    # Default timezone for users
    #settings.L10n.utc_offset = "+0100"
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
    settings.fin.currencies = {
        "EUR" : "Euros",
    #    "GBP" : "Great British Pounds",
    #    "USD" : "United States Dollars",
    }
    settings.fin.currency_default = "EUR"

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
    settings.security.policy = 5 # Controller, Function & Table ACLs

    # Version details on About-page require login
    settings.security.version_info_requires_login = True

    # -------------------------------------------------------------------------
    # CMS Module Settings
    #
    settings.cms.hide_index = True

    # -------------------------------------------------------------------------
    # Inventory Module Settings
    #
    settings.inv.facility_label = "Facility"
    settings.inv.facility_manage_staff = False

    # -------------------------------------------------------------------------
    # Organisations Module Settings
    #
    settings.org.default_organisation = "Deutsches Rotes Kreuz"
    settings.org.default_site = "BEA Benjamin Franklin Village"

    # -------------------------------------------------------------------------
    # Persons Module Settings
    #
    settings.pr.hide_third_gender = False
    settings.pr.separate_name_fields = 2
    settings.pr.name_format= "%(last_name)s, %(first_name)s"

    # -------------------------------------------------------------------------
    # Project Module Settings
    #
    settings.project.mode_task = True
    settings.project.sectors = False

    # NB should not add or remove options, but just comment/uncomment
    settings.project.task_status_opts = {#1: T("Draft"),
                                         2: T("New"),
                                         3: T("Assigned"),
                                         #4: T("Feedback"),
                                         #5: T("Blocked"),
                                         6: T("On Hold"),
                                         7: T("Canceled"),
                                         #8: T("Duplicate"),
                                         #9: T("Ready"),
                                         #10: T("Verified"),
                                         #11: T("Reopened"),
                                         12: T("Completed"),
                                         }

    settings.project.task_time = False

    # -------------------------------------------------------------------------
    # Requests Module Settings
    #
    settings.req.req_type = ("Stock",)
    settings.req.use_commit = False
    settings.req.recurring = False

    # -------------------------------------------------------------------------
    # Shelter Module Settings
    #
    #settings.cr.day_and_night = False
    settings.cr.shelter_population_dynamic = True
    settings.cr.shelter_housing_unit_management = True
    settings.cr.check_out_is_final = False

    # -------------------------------------------------------------------------
    def profile_header(r):
        """
            Profile Header for Shelter Profile page
        """

        from gluon.html import DIV, H2, H3, P, TABLE, TR, TD, A, XML, URL, HR

        db = current.db
        s3db = current.s3db

        rtable = s3db.cr_shelter_registration
        utable = s3db.cr_shelter_unit
        ctable = s3db.dvr_case
        stable = s3db.dvr_case_status

        record = r.record
        if not record:
            return ""

        shelter_id = record.id

        # Count number of shelter registrations for this shelter,
        # grouped by transitory-status of the housing unit
        left = utable.on(utable.id == rtable.shelter_unit_id)
        query = (rtable.shelter_id == shelter_id) & \
                (rtable.deleted != True)
        count = rtable.id.count()
        rows = db(query).select(utable.transitory,
                                count,
                                groupby = utable.transitory,
                                left = left,
                                )
        transitory = 0
        regular = 0
        for row in rows:
            if row[utable.transitory]:
                transitory += row[count]
            else:
                regular += row[count]
        total = transitory + regular

        # Children
        from dateutil.relativedelta import relativedelta
        EIGHTEEN = r.utcnow - relativedelta(years=18)
        ptable = s3db.pr_person
        query = (ptable.date_of_birth > EIGHTEEN) & \
                (ptable.id == rtable.person_id) & \
                (rtable.shelter_id == shelter_id)
        count = ptable.id.count()
        row = db(query).select(count).first()
        children = row[count]

        CHILDREN = TR(TD(T("How many Children")),
                         TD(children),
                         )

        # Families on-site
        gtable = s3db.pr_group
        mtable = s3db.pr_group_membership
        join = [mtable.on((mtable.group_id == gtable.id) & \
                          (mtable.deleted != True)),
                rtable.on((rtable.person_id == mtable.person_id) & \
                          (rtable.shelter_id == shelter_id) & \
                          (rtable.deleted != True)),
                ]
        query = (gtable.group_type == 7) & \
                (gtable.deleted != True)

        rows = db(query).select(gtable.id,
                                having = (mtable.id.count() > 1),
                                groupby = gtable.id,
                                join = join,
                                )
        families = len(rows)
        FAMILIES = TR(TD(T("How many Families")),
                         TD(families),
                         )

        # Transitory housing unit is called "PX" at BFV Mannheim
        # @todo: generalize, lookup transitory unit name(s) from db
        TRANSITORY = TR(TD(T("How many in PX")),
                        TD(transitory),
                        )
        REGULAR = TR(TD(T("How many in BEA (except in PX)")),
                     TD(regular),
                     )
        TOTAL = TR(TD(T("How many in BEA (total)")),
                   TD(total),
                   )

        # Get the IDs of open case statuses
        query = (stable.is_closed == False) & (stable.deleted != True)
        rows = db(query).select(stable.id)
        OPEN = set(row.id for row in rows)

        # Count number of external persons
        ftable = s3db.dvr_case_flag
        ltable = s3db.dvr_case_flag_case
        left = [ltable.on((ltable.flag_id == ftable.id) & \
                          (ltable.deleted != True)),
                ctable.on((ctable.person_id == ltable.person_id) & \
                          (ctable.status_id.belongs(OPEN)) & \
                          ((ctable.archived == False) | (ctable.archived == None)) & \
                          (ctable.deleted != True)),
                rtable.on((rtable.person_id == ltable.person_id) & \
                          (rtable.deleted != True)),
                ]
        query = (ftable.is_external == True) & \
                (ftable.deleted != True) & \
                (ltable.id != None) & \
                (ctable.id != None) & \
                (rtable.shelter_id == shelter_id)
        count = ctable.id.count()
        rows = db(query).select(count, left=left)
        external = rows.first()[count] if rows else 0

        EXTERNAL = TR(TD(T("How many external (Hospital / Police)")),
                      TD(external),
                      )

        # Get the number of free places in the BEA
        free = record.available_capacity_day
        FREE = TR(TD(T("How many free places")),
                  TD(free),
                  )

        # Announcements
        from s3db.cms import S3CMS
        resource_content = S3CMS.resource_content
        announce = resource_content("cr", "shelter", shelter_id,
                                    hide_if_empty=True,
                                    )

        # Weather (uses fake weather module/resource)
        table = s3db.cms_post
        ltable = db.cms_post_module
        query = (ltable.module == "weather") & \
                (ltable.resource == "weather") & \
                (ltable.record == shelter_id) & \
                (ltable.post_id == table.id) & \
                (table.deleted != True)
        _item = db(query).select(table.id,
                                 table.body,
                                 limitby=(0, 1)).first()
        auth = current.auth
        ADMIN = auth.get_system_roles().ADMIN
        ADMIN = auth.s3_has_role(ADMIN)
        if ADMIN:
            url_vars = {"module": "weather",
                        "resource": "weather",
                        "record": shelter_id,
                        # Custom redirect after CMS edit
                        # (required for fake module/resource)
                        "url": URL(c = "cr",
                                   f = "shelter",
                                   args = [shelter_id, "profile"],
                                   ),
                        }
            EDIT_WEATHER = T("Edit Weather Widget")
            if _item:
                item = DIV(XML(_item.body),
                           A(EDIT_WEATHER,
                             _href=URL(c="cms", f="post",
                                       args = [_item.id, "update"],
                                       vars = url_vars,
                                       ),
                             _class="action-btn cms-edit",
                             ))
            else:
                item = A(EDIT_WEATHER,
                         _href=URL(c="cms", f="post",
                                   args = "create",
                                   vars = url_vars,
                                   ),
                         _class="action-btn cms-edit",
                         )
        elif _item:
            item = XML(_item.body)
        else:
            item = ""

        weather = DIV(item, _id="cms_weather", _class="cms_content")

        # Generate profile header HTML
        output = DIV(H2(record.name),
                     P(record.comments or ""),
                     H3(T("Announcements")) if announce else "",
                     announce,
                     HR(),
                     # Current population overview
                     TABLE(TR(TD(TABLE(TOTAL,
                                    CHILDREN,
                                    FAMILIES,
                                    TRANSITORY,
                                    REGULAR,
                                    EXTERNAL,
                                    FREE
                                    ),
                                 ),
                              TD(weather,
                                 _class="show-for-large-up",
                                 ),
                              ),
                           ),
                     # Action button for check-in/out
                     A("%s / %s" % (T("Check-In"), T("Check-Out")),
                       _href=r.url(method="check-in"),
                       _class="action-btn dashboard-action",
                       ),
                     _class="profile-header",
                     )

        return output

    settings.ui.profile_header = profile_header

    # -------------------------------------------------------------------------
    def show_flag_instructions(site_id, person_id, action=None):
        """
            Show advise/instructions for checkpoint staff if
            such flags are set for this persons

            @param site_id: the site ID (currently unused)
            @param person_id: the person record ID
        """

        s3db = current.s3db

        flag_info = current.s3db.dvr_get_flag_instructions(person_id,
                                                           action = action,
                                                           )

        from gluon import DIV, H4, P

        info = DIV(_class="checkpoint-advise")
        append = info.append

        for flagname, instructions in flag_info["info"]:
            append(DIV(H4(T(flagname)),
                       P(instructions),
                       _class="checkpoint-instructions",
                       ))

        from s3 import S3CustomController, s3_fullname
        S3CustomController._view("DRK", "advise.html")

        output = {"person": DIV(s3_fullname(person_id),
                                _class="checkpoint-person",
                                ),
                  "info": info,
                  }

        return output

    # -------------------------------------------------------------------------
    def site_check_in(site_id, person_id):
        """
            When a person is checked-in to a Shelter then update the Shelter Registration
            (We assume they are checked-in during initial registration)
        """

        from s3 import s3_str

        s3db = current.s3db
        db = current.db

        warnings = []
        wappend = warnings.append

        # Check the case status
        ctable = s3db.dvr_case
        cstable = s3db.dvr_case_status
        query = (ctable.person_id == person_id) & \
                (cstable.id == ctable.status_id)
        status = db(query).select(cstable.is_closed,
                                  limitby = (0, 1),
                                  ).first()

        if status and status.is_closed:
            wappend(T("Not currently a resident"))

        # Check if we have any case flag to deny check-in or to show advise
        ftable = s3db.dvr_case_flag
        ltable = s3db.dvr_case_flag_case
        query = (ltable.person_id == person_id) & \
                (ltable.deleted != True) & \
                (ftable.id == ltable.flag_id) & \
                (ftable.deleted != True)
        flags = db(query).select(ftable.advise_at_check_in,
                                 ftable.instructions,
                                 ftable.deny_check_in,
                                 )
        callback = None
        deny_check_in = False
        for flag in flags:
            if flag.deny_check_in:
                deny_check_in = True
            if flag.advise_at_check_in:
                callback = show_flag_instructions

        if not deny_check_in:

            # Find the Registration
            stable = s3db.cr_shelter
            rtable = s3db.cr_shelter_registration

            query = (stable.site_id == site_id) & \
                    (stable.id == rtable.shelter_id) & \
                    (rtable.person_id == person_id) & \
                    (rtable.deleted != True)
            registration = db(query).select(rtable.id,
                                            rtable.registration_status,
                                            limitby=(0, 1),
                                            ).first()
            if not registration:
                error = T("Registration not found")
                return error, ", ".join(s3_str(w) for w in warnings)

            error = None

            if registration.registration_status == 2:
                wappend(T("Client was already checked-in"))

            # Update the Shelter Registration
            registration.update_record(check_in_date = current.request.utcnow,
                                       registration_status = 2,
                                       )
            onaccept = s3db.get_config("cr_shelter_registration", "onaccept")
            if onaccept:
                onaccept(registration)

        else:
            # @todo: log as case event anyway?
            error = T("Check-in denied")

        return error, ", ".join(s3_str(w) for w in warnings), callback

    # -------------------------------------------------------------------------
    def site_check_out(site_id, person_id):
        """
            When a person is checked-out from a Shelter then update the Shelter Registration
        """

        s3db = current.s3db
        db = current.db

        # Check if we have any case flag to deny check-in or to show advise
        ftable = s3db.dvr_case_flag
        ltable = s3db.dvr_case_flag_case
        query = (ltable.person_id == person_id) & \
                (ltable.deleted != True) & \
                (ftable.id == ltable.flag_id) & \
                (ftable.deleted != True)
        flags = db(query).select(ftable.advise_at_check_out,
                                 ftable.instructions,
                                 ftable.deny_check_out,
                                 )
        callback = None
        deny_check_out = False
        for flag in flags:
            if flag.deny_check_out:
                deny_check_out = True
            if flag.advise_at_check_out:
                callback = show_flag_instructions

        warning = None
        if not deny_check_out:

            # Find the Registration
            stable = s3db.cr_shelter
            rtable = s3db.cr_shelter_registration
            query = (stable.site_id == site_id) & \
                    (stable.id == rtable.shelter_id) & \
                    (rtable.person_id == person_id) & \
                    (rtable.deleted != True)
            registration = db(query).select(rtable.id,
                                            rtable.registration_status,
                                            limitby=(0, 1),
                                            ).first()
            if not registration:
                error = T("Registration not found")
                return error, warning

            error = None
            if registration.registration_status == 3:
                warning = T("Client was already checked-out")

            # Update the Shelter Registration
            registration.update_record(check_out_date = current.request.utcnow,
                                       registration_status = 3,
                                       )
            onaccept = s3db.get_config("cr_shelter_registration", "onaccept")
            if onaccept:
                onaccept(registration)

        else:
            # @todo: log as case event anyway?
            error = T("Check-out denied")

        return error, warning, callback

    # -------------------------------------------------------------------------
    def org_site_check(site_id):
        """ Custom tasks for scheduled site checks """

        # Update transferability
        from controllers import update_transferability
        result = update_transferability(site_id=site_id)

        # Log the result
        msg = "Update Transferability: " \
              "%s transferable cases found for site %s" % (result, site_id)
        current.log.info(msg)

        # Check whether we have a site activity report for yesterday
        YESTERDAY = current.request.utcnow.date() - datetime.timedelta(1)
        rtable = current.s3db.dvr_site_activity
        query = (rtable.date == YESTERDAY) & \
                (rtable.site_id == site_id) & \
                (rtable.deleted != True)
        row = current.db(query).select(rtable.id, limitby=(0, 1)).first()
        if not row:
            # Create one
            report = DRKSiteActivityReport(date = YESTERDAY,
                                           site_id = site_id,
                                           )
            # Temporarily override authorization,
            # otherwise the report would be empty
            auth = current.auth
            auth.override = True
            try:
                record_id = report.store()
            except:
                record_id = None
            auth.override = False
            if record_id:
                current.log.info("Residents Report created, record ID=%s" % record_id)
            else:
                current.log.error("Could not create Residents Report")

    settings.org.site_check = org_site_check

    # -------------------------------------------------------------------------
    def customise_auth_user_resource(r, tablename):

        current.db.auth_user.organisation_id.default = settings.get_org_default_organisation()

    settings.customise_auth_user_resource = customise_auth_user_resource

    # -------------------------------------------------------------------------
    def customise_cr_shelter_controller(**attr):

        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            if r.method == "check-in":
                # Configure check-in methods
                current.s3db.configure("cr_shelter",
                                       site_check_in = site_check_in,
                                       site_check_out = site_check_out,
                                       )
            else:
                has_role = current.auth.s3_has_role
                if has_role("SECURITY") and not has_role("ADMIN"):
                    # Security can't do anything else but check-in
                    current.auth.permission.fail()

                if r.method == "profile":
                    # Add PoI layer to the Map
                    s3db = current.s3db
                    ftable = s3db.gis_layer_feature
                    query = (ftable.controller == "gis") & \
                            (ftable.function == "poi")
                    layer = current.db(query).select(ftable.layer_id,
                                                     limitby=(0, 1)
                                                     ).first()
                    try:
                        layer_id = layer.layer_id
                    except:
                        # No suitable prepop found
                        pass
                    else:
                        pois = dict(active = True,
                                    layer_id = layer_id,
                                    name = current.T("Buildings"),
                                    id = "profile-header-%s-%s" % ("gis_poi", r.id),
                                    )
                        profile_layers = s3db.get_config("cr_shelter", "profile_layers")
                        profile_layers += (pois,)
                        s3db.configure("cr_shelter",
                                       profile_layers = profile_layers,
                                       )

            if r.component_name == "shelter_unit":
                # Expose "transitory" flag for housing units
                utable = current.s3db.cr_shelter_unit
                field = utable.transitory
                field.readable = field.writable = True
                list_fields = ["name",
                               "transitory",
                               "capacity_day",
                               "population_day",
                               "available_capacity_day",
                               ]
                r.component.configure(list_fields=list_fields)

            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            # Hide side menu and rheader for check-in
            if r.method == "check-in":
                current.menu.options = None
                output["rheader"] = ""

            return output
        s3.postp = custom_postp

        return attr

    settings.customise_cr_shelter_controller = customise_cr_shelter_controller

    # -------------------------------------------------------------------------
    def customise_cr_shelter_registration_resource(r, tablename):

        table = current.s3db.cr_shelter_registration
        field = table.shelter_unit_id

        # Filter to available housing units
        from gluon import IS_EMPTY_OR
        from s3 import IS_ONE_OF
        field.requires = IS_EMPTY_OR(IS_ONE_OF(current.db, "cr_shelter_unit.id",
                                               field.represent,
                                               filterby = "status",
                                               filter_opts = (1,),
                                               orderby="shelter_id",
                                               ))

    settings.customise_cr_shelter_registration_resource = customise_cr_shelter_registration_resource

    # -------------------------------------------------------------------------
    def customise_cr_shelter_registration_controller(**attr):
        """
            Shelter Registration controller is just used
            by the Quartiermanager role.
        """

        s3 = current.response.s3

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):
            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            if r.method == "assign":

                # Prep runs before split into create/update (Create should never happen in Village)
                table = r.table
                shelter_id = drk_default_shelter()
                if shelter_id:
                    # Only 1 Shelter
                    f = table.shelter_id
                    f.default = shelter_id
                    f.writable = False # f.readable kept as True for cr_shelter_registration_onvalidation
                    f.comment = None

                # Only edit for this Person
                f = table.person_id
                f.default = r.get_vars["person_id"]
                f.writable = False
                f.comment = None
                # Registration status hidden
                f = table.registration_status
                f.readable = False
                f.writable = False
                # Check-in dates hidden
                f = table.check_in_date
                f.readable = False
                f.writable = False
                f = table.check_out_date
                f.readable = False
                f.writable = False

                # Go back to the list of residents after assigning
                from gluon import URL
                current.s3db.configure("cr_shelter_registration",
                                       create_next = URL(c="dvr", f="person"),
                                       update_next = URL(c="dvr", f="person"),
                                       )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_cr_shelter_registration_controller = customise_cr_shelter_registration_controller

    # -------------------------------------------------------------------------
    # DVR Module Settings and Customizations
    #
    # Uncomment this to enable features to manage transferability of cases
    settings.dvr.manage_transferability = True
    # Uncomment this to enable household size in cases, set to "auto" for automatic counting
    settings.dvr.household_size = "auto"
    # Uncomment this to expose flags to mark appointment types as mandatory
    settings.dvr.mandatory_appointments = True
    # Uncomment this to have appointments with personal presence update last_seen_on
    settings.dvr.appointments_update_last_seen_on = True
    # Uncomment this to have allowance payments update last_seen_on
    settings.dvr.payments_update_last_seen_on = True
    # Uncomment this to automatically update the case status when appointments are completed
    settings.dvr.appointments_update_case_status = True
    # Uncomment this to automatically close appointments when registering certain case events
    settings.dvr.case_events_close_appointments = True
    # Uncomment this to allow cases to belong to multiple case groups ("households")
    #settings.dvr.multiple_case_groups = True
    # Configure a regular expression pattern for ID Codes (QR Codes)
    settings.dvr.id_code_pattern = "(?P<label>[^,]*),(?P<family>[^,]*),(?P<last_name>[^,]*),(?P<first_name>[^,]*),(?P<date_of_birth>[^,]*),.*"

    # -------------------------------------------------------------------------
    def customise_dvr_home():
        """ Redirect dvr/index to dvr/person?closed=0 """

        from gluon import URL
        from s3 import s3_redirect_default

        s3_redirect_default(URL(f="person", vars={"closed": "0"}))

    settings.customise_dvr_home = customise_dvr_home

    # -------------------------------------------------------------------------
    def customise_pr_person_controller(**attr):

        db = current.db
        s3db = current.s3db
        s3 = current.response.s3

        has_role = current.auth.s3_has_role
        is_admin = has_role(current.auth.get_system_roles().ADMIN)
        QUARTIERMANAGER = not is_admin and \
                          not any(has_role(role) for role in ("ADMINISTRATION",
                                                              "ADMIN_HEAD",
                                                              )) and \
                          has_role("QUARTIER")

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            if QUARTIERMANAGER:
                # Enforce closed=0
                r.vars["closed"] = r.get_vars["closed"] = "0"

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            archived = r.get_vars.get("archived")
            if archived in ("1", "true", "yes"):
                crud_strings = s3.crud_strings["pr_person"]
                crud_strings["title_list"] = T("Invalid Cases")

            controller = r.controller
            resource = r.resource

            if controller == "security":
                # Restricted view for Security staff
                if r.component:
                    redirect(r.url(method=""))

                # Filter to persons who have a case registered
                from s3 import FS
                resource.add_filter(FS("dvr_case.id") != None)

                current.menu.options = None
                # Only Show Security Notes
                ntable = s3db.dvr_note_type
                note_type = db(ntable.name == "Security").select(ntable.id,
                                                                 limitby=(0, 1),
                                                                 ).first()
                try:
                    note_type_id = note_type.id
                except:
                    current.log.error("Prepop not done - deny access to dvr_note component")
                    note_type_id = None
                    atable = s3db.dvr_note
                    atable.date.readable = atable.date.writable = False
                    atable.note.readable = atable.note.writable = False
                from s3 import S3SQLCustomForm, S3SQLInlineComponent
                crud_form = S3SQLCustomForm(
                                (T("ID"), "pe_label"),
                                "last_name",
                                "first_name",
                                "date_of_birth",
                                #"gender",
                                "person_details.nationality",
                                "cr_shelter_registration.shelter_unit_id",
                                S3SQLInlineComponent(
                                        "case_note",
                                        fields = [(T("Date"), "date"),
                                                  "note",
                                                  ],
                                        filterby = {"field": "note_type_id",
                                                    "options": note_type_id,
                                                    },
                                        label = T("Security Notes"),
                                        ),
                                )

                list_fields = [(T("ID"), "pe_label"),
                               "last_name",
                               "first_name",
                               "date_of_birth",
                               #"gender",
                               "person_details.nationality",
                               "shelter_registration.shelter_unit_id",
                               ]


                if r.method == "profile":
                    from gluon.html import DIV, H2, P, TABLE, TR, TD, A
                    from s3 import s3_fullname
                    person_id = r.id
                    record = r.record
                    table = r.table
                    dtable = s3db.pr_person_details
                    details = db(dtable.person_id == person_id).select(dtable.nationality,
                                                                       limitby=(0, 1)
                                                                       ).first()
                    try:
                        nationality = details.nationality
                    except:
                        nationality = None
                    rtable = s3db.cr_shelter_registration
                    reg = db(rtable.person_id == person_id).select(rtable.shelter_unit_id,
                                                                   limitby=(0, 1)
                                                                   ).first()
                    try:
                        shelter_unit_id = reg.shelter_unit_id
                    except:
                        shelter_unit_id = None
                    profile_header = DIV(H2(s3_fullname(record)),
                                         TABLE(TR(TD(T("ID")),
                                                  TD(record.pe_label)
                                                  ),
                                               TR(TD(table.last_name.label),
                                                  TD(record.last_name)
                                                  ),
                                               TR(TD(table.first_name.label),
                                                  TD(record.first_name)
                                                  ),
                                               TR(TD(table.date_of_birth.label),
                                                  TD(record.date_of_birth)
                                                  ),
                                               TR(TD(dtable.nationality.label),
                                                  TD(nationality)
                                                  ),
                                               TR(TD(rtable.shelter_unit_id.label),
                                                  TD(shelter_unit_id)
                                                  ),
                                               ),
                                         _class="profile-header",
                                         )
                    notes_widget = dict(label = "Security Notes",
                                        label_create = "Add Note",
                                        type = "datatable",
                                        tablename = "dvr_note",
                                        filter = ((FS("note_type_id$name") == "Security") & \
                                                  (FS("person_id") == person_id)),
                                        #icon = "report",
                                        create_controller = "dvr",
                                        create_function = "note",
                                        )
                    profile_widgets = [notes_widget]
                else:
                    profile_header = None
                    profile_widgets = None

                resource.configure(crud_form = crud_form,
                                   list_fields = list_fields,
                                   profile_header = profile_header,
                                   profile_widgets = profile_widgets,
                                   )

            elif controller == "dvr":

                from gluon import Field, IS_EMPTY_OR, IS_IN_SET, IS_NOT_EMPTY

                configure = resource.configure
                table = r.table
                ctable = s3db.dvr_case

                # Used in both list_fields and rheader
                table.absence = Field.Method("absence", drk_absence)

                if r.representation in ("html", "iframe", "aadata"):
                    # Delivers HTML, so restrict to GUI:
                    absence_field = (T("Checked-out"), "absence")
                    configure(extra_fields = ["shelter_registration.registration_status",
                                              "shelter_registration.check_out_date",
                                              ],
                              )
                else:
                    absence_field = None

                # Enable origin and destination site fields
                field = ctable.origin_site_id
                field.readable = field.writable = True
                field = ctable.destination_site_id
                field.readable = field.writable = True

                # Expose expiration dates
                field = ctable.valid_until
                field.label = T("BÜMA valid until")
                field.readable = field.writable = True
                field = ctable.stay_permit_until
                field.readable = field.writable = True

                # List modes
                check_overdue = False
                show_family_transferable = False

                # Labels
                FAMILY_TRANSFERABLE = T("Family Transferable")

                if not r.record:
                    overdue = r.get_vars.get("overdue")
                    if overdue:
                        # Filter case list for overdue check-in
                        from s3 import FS

                        reg_status = FS("shelter_registration.registration_status")
                        checkout_date = FS("shelter_registration.check_out_date")

                        checked_out = (reg_status == 3)
                        # Must catch None explicitly because it is neither
                        # equal nor unequal with anything according to SQL rules
                        not_checked_out = ((reg_status == None) | (reg_status != 3))

                        # Due date for check-in
                        due_date = r.utcnow - \
                                    datetime.timedelta(days=ABSENCE_LIMIT)

                        if overdue == "1":
                            query = checked_out & \
                                    ((checkout_date < due_date) | (checkout_date == None))
                        else:
                            query = not_checked_out | \
                                    checked_out & (checkout_date >= due_date)
                        resource.add_filter(query)
                        check_overdue = True

                    show_family_transferable = r.get_vars.get("show_family_transferable")
                    if show_family_transferable == "1":
                        show_family_transferable = True

                if not r.component:

                    # Additional component "EasyOpt Number"
                    s3db.add_components("pr_person",
                                        pr_person_tag = {"name": "eo_number",
                                                         "joinby": "person_id",
                                                         "filterby": "tag",
                                                         "filterfor": ("EONUMBER",),
                                                         "multiple": False,
                                                         },
                                        )

                    # Set default shelter for shelter registration
                    shelter_id = drk_default_shelter()
                    if shelter_id:
                        rtable = s3db.cr_shelter_registration
                        field = rtable.shelter_id
                        field.default = shelter_id
                        field.readable = field.writable = False

                        # Filter housing units to units of this shelter
                        field = rtable.shelter_unit_id
                        dbset = db(s3db.cr_shelter_unit.shelter_id == shelter_id)
                        from s3 import IS_ONE_OF
                        field.requires = IS_EMPTY_OR(IS_ONE_OF(dbset,
                                            "cr_shelter_unit.id",
                                            field.represent,
                                            # Only available units:
                                            filterby = "status",
                                            filter_opts = (1,),
                                            sort=True,
                                            ))

                    default_site = settings.get_org_default_site()
                    default_organisation = settings.get_org_default_organisation()

                    if default_organisation and not default_site:

                        # Limit sites to default_organisation
                        field = ctable.site_id
                        requires = field.requires
                        if requires:
                            if isinstance(requires, IS_EMPTY_OR):
                                requires = requires.other
                            if hasattr(requires, "dbset"):
                                stable = s3db.org_site
                                query = (stable.organisation_id == default_organisation)
                                requires.dbset = db(query)

                    configure = resource.configure
                    if r.interactive and r.method != "import":

                        # Registration status effective dates not manually updateable
                        if r.id:
                            rtable = s3db.cr_shelter_registration
                            field = rtable.check_in_date
                            field.writable = False
                            field.label = T("Last Check-in")
                            field = rtable.check_out_date
                            field.writable = False
                            field.label = T("Last Check-out")

                        # Make marital status mandatory, remove "other"
                        dtable = s3db.pr_person_details
                        field = dtable.marital_status
                        options = dict(s3db.pr_marital_status_opts)
                        del options[9] # Remove "other"
                        field.requires = IS_IN_SET(options, zero=None)

                        # Make gender mandatory, remove "unknown"
                        field = table.gender
                        field.default = None
                        from s3 import IS_PERSON_GENDER
                        options = dict(s3db.pr_gender_opts)
                        del options[1] # Remove "unknown"
                        field.requires = IS_PERSON_GENDER(options, sort = True)

                        # Last name is required
                        field = table.last_name
                        field.requires = IS_NOT_EMPTY()

                        # Check whether the shelter registration shall be cancelled
                        cancel = False
                        if r.http == "POST":
                            post_vars = r.post_vars
                            archived = post_vars.get("sub_dvr_case_archived")
                            status_id = post_vars.get("sub_dvr_case_status_id")
                            if archived:
                                cancel = True
                            if not cancel and status_id:
                                stable = s3db.dvr_case_status
                                status = db(stable.id == status_id).select(stable.is_closed,
                                                                           limitby = (0, 1),
                                                                           ).first()
                                try:
                                    if status.is_closed:
                                        cancel = True
                                except:
                                    pass

                        if cancel:
                            # Ignore registration data in form if the registration
                            # is to be cancelled - otherwise a new registration is
                            # created by the subform-processing right after
                            # dvr_case_onaccept deletes the current one:
                            reg_shelter = None
                            reg_status = None
                            reg_unit_id = None
                            reg_check_in_date = None
                            reg_check_out_date = None
                        else:
                            reg_shelter = "cr_shelter_registration.shelter_id"
                            reg_status = (T("Presence"),
                                          "cr_shelter_registration.registration_status",
                                          )
                            reg_unit_id = "cr_shelter_registration.shelter_unit_id"
                            reg_check_in_date = "cr_shelter_registration.check_in_date"
                            reg_check_out_date = "cr_shelter_registration.check_out_date"

                        # Custom CRUD form
                        from s3 import S3SQLCustomForm, S3SQLInlineComponent, S3SQLInlineLink
                        crud_form = S3SQLCustomForm(

                                    # Case Details ----------------------------
                                    (T("Case Status"), "dvr_case.status_id"),
                                    S3SQLInlineLink("case_flag",
                                                    label = T("Flags"),
                                                    field = "flag_id",
                                                    help_field = "comments",
                                                    cols = 4,
                                                    ),

                                    # Person Details --------------------------
                                    (T("ID"), "pe_label"),
                                    "last_name",
                                    "first_name",
                                    "person_details.nationality",
                                    "date_of_birth",
                                    "gender",
                                    "person_details.marital_status",

                                    # Process Data ----------------------------
                                    # Will always default & be hidden
                                    "dvr_case.organisation_id",
                                    # Will always default & be hidden
                                    "dvr_case.site_id",
                                    (T("BFV Arrival"), "dvr_case.date"),
                                    "dvr_case.origin_site_id",
                                    "dvr_case.destination_site_id",
                                    S3SQLInlineComponent(
                                            "eo_number",
                                            fields = [("", "value"),
                                                      ],
                                            filterby = {"field": "tag",
                                                        "options": "EONUMBER",
                                                        },
                                            label = T("EasyOpt Number"),
                                            multiple = False,
                                            name = "eo_number",
                                            ),
                                    "dvr_case.valid_until",
                                    "dvr_case.stay_permit_until",

                                    # Shelter Data ----------------------------
                                    # Will always default & be hidden
                                    #"cr_shelter_registration.site_id",
                                    reg_shelter,
                                    # @ ToDo: Automate this from the Case Status?
                                    reg_unit_id,
                                    reg_status,
                                    reg_check_in_date,
                                    reg_check_out_date,

                                    # Other Details ---------------------------
                                    "person_details.occupation",
                                    S3SQLInlineComponent(
                                            "contact",
                                            fields = [("", "value"),
                                                        ],
                                            filterby = {"field": "contact_method",
                                                        "options": "SMS",
                                                        },
                                            label = T("Mobile Phone"),
                                            multiple = False,
                                            name = "phone",
                                            ),
                                    "person_details.literacy",
                                    S3SQLInlineComponent(
                                            "case_language",
                                            fields = ["language",
                                                      "quality",
                                                      "comments",
                                                      ],
                                            label = T("Language / Communication Mode"),
                                            ),
                                    "dvr_case.comments",

                                    # Archived-flag ---------------------------
                                    (T("Invalid"), "dvr_case.archived"),
                                    )

                        configure(crud_form = crud_form,
                                  )

                        # Reconfigure filter widgets
                        filter_widgets = resource.get_config("filter_widgets")
                        if filter_widgets:

                            from s3 import S3DateFilter, \
                                           S3OptionsFilter, \
                                           S3TextFilter
                            extend_text_filter = True
                            for fw in filter_widgets:
                                # No filter default for case status
                                if fw.field == "dvr_case.status_id":
                                    fw.opts.default = None
                                # Text filter includes EasyOpt Number and Case Comments
                                if extend_text_filter and isinstance(fw, S3TextFilter):
                                    fw.field.extend(("eo_number.value",
                                                     "dvr_case.comments",
                                                     ))
                                    fw.opts.comment = T("You can search by name, ID, EasyOpt number and comments")
                                    extend_text_filter = False

                            # Add filter for date of birth
                            dob_filter = S3DateFilter("date_of_birth")
                            #dob_filter.operator = ["eq"]
                            filter_widgets.insert(1, dob_filter)

                            # Add filter for family transferability
                            if show_family_transferable:
                                ft_filter = S3OptionsFilter("dvr_case.household_transferable",
                                                            label = FAMILY_TRANSFERABLE,
                                                            options = {True: T("Yes"),
                                                                       False: T("No"),
                                                                       },
                                                            cols = 2,
                                                            hidden = True,
                                                            )
                                filter_widgets.append(ft_filter)

                            # Add filter for registration date
                            reg_filter = S3DateFilter("dvr_case.date",
                                                      hidden = True,
                                                      )
                            filter_widgets.append(reg_filter)

                            # Add filter for registration status
                            reg_filter = S3OptionsFilter("shelter_registration.registration_status",
                                                         label = T("Presence"),
                                                         options = s3db.cr_shelter_registration_status_opts,
                                                         hidden = True,
                                                         cols = 3,
                                                         )
                            filter_widgets.append(reg_filter)

                            # Add filter for IDs
                            id_filter = S3TextFilter(["pe_label"],
                                                     label = T("IDs"),
                                                     match_any = True,
                                                     hidden = True,
                                                     comment = T("Search for multiple IDs (separated by blanks)"),
                                                     )
                            filter_widgets.append(id_filter)

                    # Custom list fields (must be outside of r.interactive)
                    list_fields = [(T("ID"), "pe_label"),
                                   (T("EasyOpt No."), "eo_number.value"),
                                   "last_name",
                                   "first_name",
                                   "date_of_birth",
                                   "gender",
                                   "person_details.nationality",
                                   "dvr_case.date",
                                   "dvr_case.status_id",
                                   (T("Shelter"), "shelter_registration.shelter_unit_id"),
                                   ]

                    # Add fields for managing transferability
                    if settings.get_dvr_manage_transferability() and not check_overdue:
                        transf_fields = ["dvr_case.transferable",
                                         (T("Size of Family"), "dvr_case.household_size"),
                                         ]
                        if show_family_transferable:
                            transf_fields.append((FAMILY_TRANSFERABLE,
                                                  "dvr_case.household_transferable"))
                        list_fields[-1:-1] = transf_fields

                    # Days of absence (virtual field)
                    if absence_field:
                        list_fields.append(absence_field)

                    if r.representation == "xls":
                        # Extra list_fields for XLS export

                        # Add appointment dates
                        atypes = ["GU",
                                  "X-Ray",
                                  "Reported Transferable",
                                  "Transfer",
                                  "Sent to RP",
                                  ]
                        COMPLETED = 4
                        afields = []
                        attable = s3db.dvr_case_appointment_type
                        query = attable.name.belongs(atypes)
                        rows = db(query).select(attable.id,
                                                attable.name,
                                                )
                        add_components = s3db.add_components
                        for row in rows:
                            type_id = row.id
                            name = "appointment%s" % type_id
                            hook = {"name": name,
                                    "joinby": "person_id",
                                    "filterby": {"type_id": type_id,
                                                 "status": COMPLETED,
                                                 },
                                    }
                            add_components("pr_person",
                                           dvr_case_appointment = hook,
                                           )
                            afields.append((T(row.name), "%s.date" % name))

                        list_fields.extend(afields)

                        # Add family key
                        s3db.add_components("pr_person",
                                            pr_group = {"name": "family",
                                                        "link": "pr_group_membership",
                                                        "joinby": "person_id",
                                                        "key": "group_id",
                                                        "filterby": {"group_type": 7},
                                                        },
                                            )

                        list_fields += [# Current check-in/check-out status
                                        (T("Registration Status"),
                                         "shelter_registration.registration_status",
                                         ),
                                        # Last Check-in date
                                        "shelter_registration.check_in_date",
                                        # Last Check-out date
                                        "shelter_registration.check_out_date",
                                        # Person UUID
                                        ("UUID", "uuid"),
                                        # Family Record ID
                                        (T("Family ID"), "family.id"),
                                        ]
                    configure(list_fields = list_fields)

            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if QUARTIERMANAGER:
                # Add Action Button to assign Housing Unit to the Resident
                from gluon import URL
                #from s3 import S3CRUD, s3_str
                from s3 import s3_str
                #S3CRUD.action_buttons(r)
                s3.actions = [dict(label=s3_str(T("Assign Shelter")),
                                    _class="action-btn",
                                    url=URL(c="cr",
                                            f="shelter_registration",
                                            args=["assign"],
                                            vars={"person_id": "[id]"},
                                            )),
                               ]

            return output
        s3.postp = custom_postp

        # Custom rheader tabs
        if current.request.controller == "dvr":
            attr = dict(attr)
            attr["rheader"] = drk_dvr_rheader

        return attr

    settings.customise_pr_person_controller = customise_pr_person_controller

    # -------------------------------------------------------------------------
    def customise_pr_group_membership_controller(**attr):

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

            ROLE = T("Role")

            resource = r.resource
            if r.controller == "dvr":

                # Set default shelter
                shelter_id = drk_default_shelter()
                if shelter_id:
                    rtable = s3db.cr_shelter_registration
                    field = rtable.shelter_id
                    field.default = shelter_id

                if r.interactive:
                    table = resource.table

                    from gluon import IS_EMPTY_OR
                    from s3 import IS_ADD_PERSON_WIDGET2, S3AddPersonWidget2, IS_ONE_OF

                    field = table.person_id
                    field.represent = s3db.pr_PersonRepresent(show_link=True)
                    field.requires = IS_ADD_PERSON_WIDGET2()
                    field.widget = S3AddPersonWidget2(controller="dvr")

                    field = table.role_id
                    field.readable = field.writable = True
                    field.label = ROLE
                    field.comment = None
                    field.requires = IS_EMPTY_OR(
                                        IS_ONE_OF(current.db, "pr_group_member_role.id",
                                                field.represent,
                                                filterby = "group_type",
                                                filter_opts = (7,),
                                                ))

                    field = table.group_head
                    field.label = T("Head of Family")

                    # Custom CRUD strings for this perspective
                    s3.crud_strings["pr_group_membership"] = Storage(
                        label_create = T("Add Family Member"),
                        title_display = T("Family Member Details"),
                        title_list = T("Family Members"),
                        title_update = T("Edit Family Member"),
                        label_list_button = T("List Family Members"),
                        label_delete_button = T("Remove Family Member"),
                        msg_record_created = T("Family Member added"),
                        msg_record_modified = T("Family Member updated"),
                        msg_record_deleted = T("Family Member removed"),
                        msg_list_empty = T("No Family Members currently registered")
                        )

                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id",
                               "person_id$date_of_birth",
                               "person_id$gender",
                               "group_head",
                               (ROLE, "role_id"),
                               (T("Case Status"), "person_id$dvr_case.status_id"),
                               "person_id$dvr_case.transferable",
                               ]
                # Retain group_id in list_fields if added in standard prep
                lfields = resource.get_config("list_fields")
                if "group_id" in lfields:
                    list_fields.insert(0, "group_id")
                resource.configure(filter_widgets = None,
                                   list_fields = list_fields,
                                   )
            return result
        s3.prep = custom_prep

        attr["rheader"] = drk_dvr_rheader

        return attr

    settings.customise_pr_group_membership_controller = customise_pr_group_membership_controller

    # -------------------------------------------------------------------------
    def dvr_case_onaccept(form):
        """
            If case is archived or closed then remove shelter_registration,
            otherwise ensure that a shelter_registration exists for any
            open and valid case
        """

        db = current.db
        s3db = current.s3db

        form_vars = form.vars
        archived = form_vars.archived
        person_id = form_vars.person_id

        # Inline shelter registration?
        inline = "sub_shelter_registration_registration_status" in \
                 current.request.post_vars

        cancel = False

        if archived:
            cancel = True

        else:
            status_id = form_vars.status_id
            if status_id:

                stable = s3db.dvr_case_status
                status = db(stable.id == status_id).select(stable.is_closed,
                                                           limitby = (0, 1)
                                                           ).first()
                try:
                    if status.is_closed:
                        cancel = True
                except:
                    current.log.error("Status %s not found" % status_id)
                    return

        rtable = s3db.cr_shelter_registration
        query = (rtable.person_id == person_id)

        if cancel:
            reg = db(query).select(rtable.id, limitby=(0, 1)).first()
            if reg:
                resource = s3db.resource("cr_shelter_registration",
                                         id = reg.id,
                                         )
                resource.delete()

        elif not inline:
            # We're called without inline shelter registration, so
            # make sure there is a shelter registration if the case
            # is valid and open:
            reg = db(query).select(rtable.id, limitby=(0, 1)).first()
            if not reg:
                if rtable.shelter_id.default is not None:
                    # Create default shelter registration
                    rtable.insert(person_id=person_id)
                else:
                    current.response.warning = T("Person could not be registered to a shelter, please complete case manually")

    # -------------------------------------------------------------------------
    def customise_dvr_case_resource(r, tablename):

        s3db = current.s3db

        config = {}
        get_config = s3db.get_config

        for method in ("create", "update", None):

            setting = "%s_onaccept" % method if method else "onaccept"
            default = get_config(tablename, setting)
            if not default:
                if method is None and len(config) < 2:
                    onaccept = dvr_case_onaccept
                else:
                    continue
            elif not isinstance(default, list):
                onaccept = [default, dvr_case_onaccept]
            else:
                onaccept = default
                if all(cb != dvr_case_onaccept for cb in onaccept):
                    onaccept.append(dvr_case_onaccept)
            config[setting] = onaccept

        s3db.configure(tablename, **config)

    settings.customise_dvr_case_resource = customise_dvr_case_resource

    # -------------------------------------------------------------------------
    def dvr_note_onaccept(form):
        """
            Set owned_by_group
        """

        db = current.db
        s3db = current.s3db
        form_vars = form.vars
        table = s3db.dvr_note_type
        types = db(table.name.belongs(("Medical", "Security"))).select(table.id,
                                                                       table.name).as_dict(key="name")
        try:
            MEDICAL = types["Medical"]["id"]
        except:
            current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note_type")
            return
        SECURITY = types["Security"]["id"]
        note_type_id = form_vars.note_type_id
        if note_type_id == str(MEDICAL):
            table = s3db.dvr_note
            gtable = db.auth_group
            role = db(gtable.uuid == "MEDICAL").select(gtable.id,
                                                       limitby=(0, 1)
                                                       ).first()
            try:
                group_id = role.id
            except:
                current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note")
                return
            db(table.id == form_vars.id).update(owned_by_group=group_id)
        elif note_type_id == str(SECURITY):
            table = s3db.dvr_note
            gtable = db.auth_group
            role = db(gtable.uuid == "SECURITY").select(gtable.id,
                                                        limitby=(0, 1)
                                                        ).first()
            try:
                group_id = role.id
            except:
                current.log.error("Prepop not completed...cannot assign owned_by_group to dvr_note")
                return
            db(table.id == form_vars.id).update(owned_by_group=group_id)

    # -------------------------------------------------------------------------
    def customise_dvr_note_resource(r, tablename):

        s3db = current.s3db
        #default_onaccept = s3db.get_config(tablename, "onaccept")
        #if default_onaccept:
        #    onaccept = [default_onaccept,
        #                dvr_case_activity_onaccept,
        #                ]
        #else:
        #    onaccept = dvr_case_activity_onaccept
        #s3db.configure(tablename,
        #               onaccept = onaccept,
        #               )

        has_role = current.auth.s3_has_role
        if has_role("SECURITY") and not has_role("ADMIN"):
            # Just see Security Notes
            table = s3db.dvr_note_type
            security = current.db(table.name == "Security").select(table.id,
                                                                   limitby=(0, 1)
                                                                   ).first()
            try:
                SECURITY = security.id
            except:
                current.log.error("Prepop not completed...cannot filter dvr_note_type")
                raise

            field = s3db[tablename].note_type_id
            field.default = SECURITY
            field.readable = field.writable = False
            from s3 import FS
            if r.tablename  == tablename:
                r.resource.add_filter(FS("note_type_id") == SECURITY)
            else:
                r.resource.add_component_filter("case_note", FS("note_type_id") == SECURITY)
                # Look through components
                #components = r.resource.components
                #for c in components:
                #    if c == tablename:
                #        components[c].add_filter(FS("note_type_id") == SECURITY)
                #        break
        elif not has_role("HEAD_OF_ADMIN"):
            # Remove Medical from list of options
            db = current.db
            table = s3db.dvr_note_type
            medical = db(table.name == "Medical").select(table.id,
                                                         limitby=(0, 1)
                                                         ).first()
            try:
                MEDICAL = medical.id
            except:
                current.log.error("Prepop not completed...cannot filter dvr_note_type")
                raise

            field = s3db[tablename].note_type_id
            from s3 import FS, IS_ONE_OF
            the_set = db(table.id != MEDICAL)
            field.requires = IS_ONE_OF(the_set, "dvr_note_type.id",
                                       field.represent)
            # Cannot see Medical Notes
            if r.tablename == tablename:
                r.resource.add_filter(FS("note_type_id") != MEDICAL)
            else:
                r.resource.add_component_filter("case_note", FS("note_type_id") != MEDICAL)
                # Look through components
                #components = r.resource.components
                #for c in components:
                #    if c == tablename:
                #        components[c].add_filter(FS("note_type_id") != MEDICAL)
                #        break

    settings.customise_dvr_note_resource = customise_dvr_note_resource

    # -------------------------------------------------------------------------
    def customise_dvr_case_activity_controller(**attr):

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

            # Filter to active cases
            if not r.record:
                from s3 import FS
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                filter_widgets = resource.get_config("filter_widgets")
                if filter_widgets:
                    s3db.add_components("pr_person",
                                        pr_person_tag = {"name": "eo_number",
                                                         "joinby": "person_id",
                                                         "filterby": "tag",
                                                         "filterfor": ("EONUMBER",),
                                                         "multiple": False,
                                                         },
                                        )
                    from s3 import S3TextFilter
                    for fw in filter_widgets:
                        if isinstance(fw, S3TextFilter):
                            fw.field.append("person_id$eo_number.value")
                            break

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id$first_name",
                               "person_id$last_name",
                               "need_id",
                               "need_details",
                               "emergency",
                               "referral_details",
                               "followup",
                               "followup_date",
                               "completed",
                               ]

                r.resource.configure(list_fields = list_fields,
                                    )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_dvr_case_activity_controller = customise_dvr_case_activity_controller

    # -------------------------------------------------------------------------
    def customise_dvr_case_appointment_controller(**attr):

        s3 = current.response.s3
        s3db = current.s3db

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            # Filter to active cases
            if not r.record:
                from s3 import FS
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                if r.interactive and not r.id:
                    # Add EO Number as component so it can be filtered by
                    s3db.add_components("pr_person",
                                        pr_person_tag = {"name": "eo_number",
                                                         "joinby": "person_id",
                                                         "filterby": "tag",
                                                         "filterfor": ("EONUMBER",),
                                                         "multiple": False,
                                                         },
                                        )

                    # Custom filter widgets
                    from s3 import S3TextFilter, S3OptionsFilter, S3DateFilter, s3_get_filter_opts
                    filter_widgets = [
                        S3TextFilter(["person_id$pe_label",
                                      "person_id$first_name",
                                      "person_id$last_name",
                                      "person_id$eo_number.value",
                                      ],
                                      label = T("Search"),
                                      ),
                        S3OptionsFilter("type_id",
                                        options = s3_get_filter_opts("dvr_case_appointment_type",
                                                                     translate = True,
                                                                     ),
                                        cols = 3,
                                        ),
                        S3OptionsFilter("status",
                                        options = s3db.dvr_appointment_status_opts,
                                        default = 2,
                                        ),
                        S3DateFilter("date",
                                     ),
                        S3OptionsFilter("person_id$dvr_case.status_id$is_closed",
                                        cols = 2,
                                        default = False,
                                        #hidden = True,
                                        label = T("Case Closed"),
                                        options = {True: T("Yes"),
                                                   False: T("No"),
                                                   },
                                        ),
                        S3TextFilter(["person_id$pe_label"],
                                     label = T("IDs"),
                                     match_any = True,
                                     hidden = True,
                                     comment = T("Search for multiple IDs (separated by blanks)"),
                                     ),
                        ]

                    resource.configure(filter_widgets = filter_widgets)

                # Default filter today's and tomorrow's appointments
                from s3 import s3_set_default_filter
                now = r.utcnow
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow = today + datetime.timedelta(days=1)
                s3_set_default_filter("~.date",
                                      {"ge": today, "le": tomorrow},
                                      tablename = "dvr_case_appointment",
                                      )

                # Field Visibility
                table = resource.table
                field = table.case_id
                field.readable = field.writable = False

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id$first_name",
                               "person_id$last_name",
                               "type_id",
                               "date",
                               "status",
                               "comments",
                               ]

                if r.representation == "xls":
                    # Include Person UUID
                    list_fields.append(("UUID", "person_id$uuid"))

                resource.configure(list_fields = list_fields,
                                   insertable = False,
                                   deletable = False,
                                   update_next = r.url(method=""),
                                   )

            return result
        s3.prep = custom_prep

        return attr

    settings.customise_dvr_case_appointment_controller = customise_dvr_case_appointment_controller

    # -------------------------------------------------------------------------
    def customise_dvr_allowance_controller(**attr):

        s3 = current.response.s3
        s3db = current.s3db

        # Custom prep
        standard_prep = s3.prep
        def custom_prep(r):

            # Call standard prep
            if callable(standard_prep):
                result = standard_prep(r)
            else:
                result = True

            resource = r.resource

            # Filter to active cases
            if not r.record:
                from s3 import FS
                query = (FS("person_id$dvr_case.archived") == False) | \
                        (FS("person_id$dvr_case.archived") == None)
                resource.add_filter(query)

            if not r.component:

                if r.interactive and not r.id:
                    # Custom filter widgets
                    from s3 import S3TextFilter, \
                                   S3OptionsFilter, \
                                   S3DateFilter

                    filter_widgets = [
                        S3TextFilter(["person_id$pe_label",
                                      "person_id$first_name",
                                      "person_id$middle_name",
                                      "person_id$last_name",
                                      ],
                                      label = T("Search"),
                                      ),
                        S3OptionsFilter("status",
                                        default = 1,
                                        cols = 4,
                                        options = s3db.dvr_allowance_status_opts,
                                        ),
                        S3DateFilter("date"),
                        S3DateFilter("paid_on"),
                        S3DateFilter("entitlement_period",
                                     hidden = True,
                                     )
                        ]
                    resource.configure(filter_widgets = filter_widgets)

                # Field Visibility
                table = resource.table
                field = table.case_id
                field.readable = field.writable = False

                # Custom list fields
                list_fields = [(T("ID"), "person_id$pe_label"),
                               "person_id",
                               "entitlement_period",
                               "date",
                               "currency",
                               "amount",
                               "status",
                               "paid_on",
                               "comments",
                               ]
                if r.representation == "xls":
                    list_fields.append(("UUID", "person_id$uuid"))

                resource.configure(list_fields = list_fields,
                                   insertable = False,
                                   deletable = False,
                                   updatable = False,
                                   )

            return result
        s3.prep = custom_prep

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if r.method == "register":
                from s3 import S3CustomController
                S3CustomController._view("DRK", "register_case_event.html")
            return output
        s3.postp = custom_postp

        return attr

    settings.customise_dvr_allowance_controller = customise_dvr_allowance_controller

    # -------------------------------------------------------------------------
    def customise_dvr_case_event_controller(**attr):

        s3 = current.response.s3

        # Custom postp
        standard_postp = s3.postp
        def custom_postp(r, output):
            # Call standard postp
            if callable(standard_postp):
                output = standard_postp(r, output)

            if r.method == "register":
                from s3 import S3CustomController
                S3CustomController._view("DRK", "register_case_event.html")
            return output
        s3.postp = custom_postp

        return attr

    settings.customise_dvr_case_event_controller = customise_dvr_case_event_controller

    # -------------------------------------------------------------------------
    def customise_dvr_site_activity_resource(r, tablename):

        s3db = current.s3db

        s3db.set_method("dvr", "site_activity",
                        method = "create",
                        action = DRKCreateSiteActivityReport,
                        )
        s3db.configure("dvr_site_activity",
                       listadd = False,
                       addbtn = True,
                       )

        crud_strings = current.response.s3.crud_strings
        crud_strings["dvr_site_activity"] = Storage(
            label_create = T("Create Residents Report"),
            title_display = T("Residents Report"),
            title_list = T("Residents Reports"),
            title_update = T("Edit Residents Report"),
            label_list_button = T("List Residents Reports"),
            label_delete_button = T("Delete Residents Report"),
            msg_record_created = T("Residents Report created"),
            msg_record_modified = T("Residents Report updated"),
            msg_record_deleted = T("Residents Report deleted"),
            msg_list_empty = T("No Residents Reports found"),
        )

    settings.customise_dvr_site_activity_resource = customise_dvr_site_activity_resource

    # -------------------------------------------------------------------------
    def customise_org_facility_resource(r, tablename):

        s3db = current.s3db

        # Hide "code" field (not needed)
        table = s3db.org_facility
        field = table.code
        field.readable = field.writable = False

        # Location selector just needs country + address
        from s3 import S3LocationSelector
        field = table.location_id
        field.widget = S3LocationSelector(levels = ["L0"],
                                          show_address=True,
                                          show_map = False,
                                          )

        # Custom list fields
        list_fields = ["name",
                       "site_facility_type.facility_type_id",
                       "organisation_id",
                       "location_id",
                       "contact",
                       "phone1",
                       "phone2",
                       "email",
                       "website",
                       "comments",
                       ]

        # Custom filter widgets
        from s3 import S3TextFilter, S3OptionsFilter, s3_get_filter_opts
        filter_widgets = [S3TextFilter(["name",
                                        "organisation_id$name",
                                        "organisation_id$acronym",
                                        "comments",
                                        ],
                                        label = T("Search"),
                                       ),
                          S3OptionsFilter("site_facility_type.facility_type_id",
                                          options = s3_get_filter_opts("org_facility_type",
                                                                       translate = True,
                                                                       ),
                                          ),
                          S3OptionsFilter("organisation_id",
                                          ),
                          ]

        s3db.configure("org_facility",
                       filter_widgets = filter_widgets,
                       list_fields = list_fields,
                       )

    settings.customise_org_facility_resource = customise_org_facility_resource

    # -------------------------------------------------------------------------
    def customise_org_facility_controller(**attr):

        # Allow selection of all countries
        current.deployment_settings.gis.countries = []

        # Custom rheader+tabs
        if current.request.controller == "org":
            attr = dict(attr)
            attr["rheader"] = drk_org_rheader

        return attr

    settings.customise_org_facility_controller = customise_org_facility_controller

    # -------------------------------------------------------------------------
    def customise_project_task_resource(r, tablename):
        """
            Restrict list of assignees to just Staff/Volunteers
        """

        db = current.db
        s3db = current.s3db
        htable = s3db.hrm_human_resource
        ptable = s3db.pr_person
        query = (htable.deleted == False) & \
                (htable.person_id == ptable.id)
        hrs = db(query).select(ptable.pe_id)
        hrs = [hr.pe_id for hr in hrs]

        from gluon import IS_EMPTY_OR
        from s3 import IS_ONE_OF
        s3db.project_task.pe_id.requires = IS_EMPTY_OR(
            IS_ONE_OF(db, "pr_pentity.pe_id",
                      s3db.pr_PersonEntityRepresent(show_label = False,
                                                    show_type = False),
                      sort=True,
                      filterby = "pe_id",
                      filter_opts = hrs,
                      ))

    settings.customise_project_task_resource = customise_project_task_resource

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
        ("vol", Storage(
           name_nice = T("Volunteers"),
           #description = "Human Resources Management",
           restricted = True,
           module_type = 2,
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
        #("hms", Storage(
        #    name_nice = T("Hospitals"),
        #    #description = "Helps to monitor status of hospitals",
        #    restricted = True,
        #    module_type = 10
        #)),
        ("dvr", Storage(
          name_nice = T("Residents"),
          #description = "Allow affected individuals & households to register to receive compensation and distributions",
          restricted = True,
          module_type = 10,
        )),
        ("event", Storage(
           name_nice = T("Events"),
           #description = "Activate Events (e.g. from Scenario templates) for allocation of appropriate Resources (Human, Assets & Facilities).",
           restricted = True,
           module_type = 10,
        )),
        ("security", Storage(
           name_nice = T("Security"),
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

# =============================================================================
def drk_default_shelter():
    """
        Lazy getter for the default shelter_id
    """

    s3 = current.response.s3
    shelter_id = s3.drk_default_shelter

    if not shelter_id:
        default_site = current.deployment_settings.get_org_default_site()

        # Get the shelter_id for default site
        if default_site:
            stable = current.s3db.cr_shelter
            query = (stable.site_id == default_site)
            shelter = current.db(query).select(stable.id,
                                            limitby=(0, 1),
                                            ).first()
            if shelter:
                shelter_id = shelter.id

        s3.drk_default_shelter = shelter_id

    return shelter_id

# =============================================================================
def drk_absence(row):
    """
        Field method to display duration of absence in
        dvr/person list view and rheader

        @param row: the Row
    """

    if hasattr(row, "cr_shelter_registration"):
        registration = row.cr_shelter_registration
    else:
        registration = None

    result = current.messages["NONE"]

    if registration is None or \
       not hasattr(registration, "registration_status") or \
       not hasattr(registration, "check_out_date"):
        # must reload
        db = current.db
        s3db = current.s3db

        person = row.pr_person if hasattr(row, "pr_person") else row
        person_id = person.id
        if not person_id:
            return result
        table = s3db.cr_shelter_registration
        query = (table.person_id == person_id) & \
                (table.deleted != True)
        registration = db(query).select(table.registration_status,
                                        table.check_out_date,
                                        limitby = (0, 1),
                                        ).first()

    if registration and \
       registration.registration_status == 3:

        T = current.T

        check_out_date = registration.check_out_date
        if check_out_date:

            delta = (current.request.utcnow - check_out_date).total_seconds()
            if delta < 0:
                delta = 0
            days = int(delta / 86400)

            if days < 1:
                result = "<1 %s" % T("Day")
            elif days == 1:
                result = "1 %s" % T("Day")
            else:
                result = "%s %s" % (days, T("Days"))

            if days >= ABSENCE_LIMIT:
                result = SPAN(result, _class="overdue")

        else:
            result = SPAN(T("Date unknown"), _class="overdue")

    return result

# =============================================================================
def drk_dvr_rheader(r, tabs=[]):
    """ DVR custom resource headers """

    if r.representation != "html":
        # Resource headers only used in interactive views
        return None

    from s3 import s3_rheader_resource, \
                   S3ResourceHeader, \
                   s3_fullname, \
                   s3_yes_no_represent

    tablename, record = s3_rheader_resource(r)
    if tablename != r.tablename:
        resource = current.s3db.resource(tablename, id=record.id)
    else:
        resource = r.resource

    rheader = None
    rheader_fields = []

    if record:
        T = current.T

        if tablename == "pr_person":

            # "Case Archived" hint
            hint = lambda record: SPAN(T("Invalid Case"),
                                       _class="invalid-case",
                                       )

            if current.request.controller == "security":

                # No rheader except archived-hint
                case = resource.select(["dvr_case.archived"], as_rows=True)
                if case and case[0]["dvr_case.archived"]:
                    rheader_fields = [[(None, hint)]]
                    tabs = None
                else:
                    return None

            else:

                if not tabs:
                    tabs = [(T("Basic Details"), None),
                            (T("Family Members"), "group_membership/"),
                            (T("Activities"), "case_activity"),
                            (T("Appointments"), "case_appointment"),
                            (T("Allowance"), "allowance"),
                            (T("Presence"), "shelter_registration_history"),
                            (T("Events"), "case_event"),
                            (T("Notes"), "case_note"),
                            ]

                case = resource.select(["dvr_case.status_id",
                                        "dvr_case.archived",
                                        "dvr_case.household_size",
                                        "dvr_case.transferable",
                                        "dvr_case.last_seen_on",
                                        "first_name",
                                        "last_name",
                                        "shelter_registration.shelter_unit_id",
                                        ],
                                        represent = True,
                                        raw_data = True,
                                        ).rows

                if case:
                    # Extract case data
                    case = case[0]
                    archived = case["_row"]["dvr_case.archived"]
                    case_status = lambda row: case["dvr_case.status_id"]
                    household_size = lambda row: case["dvr_case.household_size"]
                    last_seen_on = lambda row: case["dvr_case.last_seen_on"]
                    name = lambda row: s3_fullname(row)
                    shelter = lambda row: case["cr_shelter_registration.shelter_unit_id"]
                    transferable = lambda row: case["dvr_case.transferable"]
                else:
                    # Target record exists, but doesn't match filters
                    return None

                rheader_fields = [[(T("ID"), "pe_label"),
                                   (T("Case Status"), case_status),
                                   (T("Shelter"), shelter),
                                   ],
                                  [(T("Name"), name),
                                   (T("Transferable"), transferable),
                                   (T("Checked-out"), "absence"),
                                   ],
                                  ["date_of_birth",
                                   (T("Size of Family"), household_size),
                                   (T("Last seen on"), last_seen_on),
                                   ],
                                  ]

                if archived:
                    rheader_fields.insert(0, [(None, hint)])

        elif tablename == "dvr_case":

            if not tabs:
                tabs = [(T("Basic Details"), None),
                        (T("Activities"), "case_activity"),
                        ]

            rheader_fields = [["reference"],
                              ["status_id"],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )

    return rheader

# =============================================================================
def drk_org_rheader(r, tabs=[]):
    """ ORG custom resource headers """

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

        if tablename == "org_facility":

            if not tabs:
                tabs = [(T("Basic Details"), None),
                        ]

            rheader_fields = [["name", "email"],
                              ["organisation_id", "phone1"],
                              ["location_id", "phone2"],
                              ]

        rheader = S3ResourceHeader(rheader_fields, tabs)(r,
                                                         table=resource.table,
                                                         record=record,
                                                         )
    return rheader

# =============================================================================
class DRKCreateSiteActivityReport(S3Method):
    """ Custom method to create a dvr_site_activity entry """

    def apply_method(self, r, **attr):
        """
            Entry point for REST controller

            @param r: the S3Request
            @param attr: dict of controller parameters
        """

        if r.representation in ("html", "iframe"):
            if r.http in ("GET", "POST"):
                output = self.create_form(r, **attr)
            else:
                r.error(405, current.ERROR.BAD_METHOD)
        else:
            r.error(415, current.ERROR.BAD_FORMAT)

        return output

    # -------------------------------------------------------------------------
    def create_form(self, r, **attr):
        """
            Generate and process the form

            @param r: the S3Request
            @param attr: dict of controller parameters
        """

        # User must be permitted to create site activity reports
        authorised = self._permitted(method="create")
        if not authorised:
            r.unauthorised()

        s3db = current.s3db

        T = current.T
        response = current.response
        settings = current.deployment_settings

        # Page title
        output = {"title": T("Create Residents Report")}

        # Form fields
        table = s3db.dvr_site_activity
        formfields = [table.site_id,
                      table.date,
                      ]

        # Form buttons
        from gluon import INPUT, A, SQLFORM
        submit_btn = INPUT(_class = "tiny primary button",
                           _name = "submit",
                           _type = "submit",
                           _value = T("Create Report"),
                           )
        cancel_btn = A(T("Cancel"),
                       _href = r.url(id=None, method=""),
                       _class = "action-lnk",
                       )
        buttons = [submit_btn, cancel_btn]

        # Generate the form and add it to the output
        resourcename = r.resource.name
        formstyle = settings.get_ui_formstyle()
        form = SQLFORM.factory(record = None,
                               showid = False,
                               formstyle = formstyle,
                               table_name = resourcename,
                               buttons = buttons,
                               *formfields)
        output["form"] = form

        # Process the form
        formname = "%s/manage" % resourcename
        if form.accepts(r.post_vars,
                        current.session,
                        formname = formname,
                        onvalidation = self.validate,
                        keepvalues = False,
                        hideerror = False,
                        ):

            from s3 import S3PermissionError, s3_store_last_record_id

            formvars = form.vars
            report = DRKSiteActivityReport(site_id = formvars.site_id,
                                           date = formvars.date,
                                           )
            try:
                record_id = report.store()
            except S3PermissionError:
                # Redirect to list view rather than index page
                current.auth.permission.homepage = r.url(id=None, method="")
                r.unauthorised()

            r.resource.lastid = str(record_id)
            s3_store_last_record_id("dvr_site_activity", record_id)

            current.response.confirmation = T("Report created")
            self.next = r.url(id=record_id, method="read")

        response.view = self._view(r, "create.html")

        return output

    # -------------------------------------------------------------------------
    def validate(self, form):
        """
            Validate the form

            @param form: the FORM
        """

        T = current.T
        formvars = form.vars

        if "site_id" in formvars:
            site_id = formvars.site_id
        else:
            # Fall back to default site
            site_id = current.deployment_settings.get_org_default_site()
        if not site_id:
            form.errors["site_id"] = T("No site specified")
        formvars.site_id = site_id

        if "date" in formvars:
            date = formvars.date
        else:
            # Fall back to today
            date = current.request.utcnow.date()
        formvars.date = date

# =============================================================================
class DRKSiteActivityReport(object):
    """
        Helper class to produce site activity reports ("Residents Report")
    """

    def __init__(self, site_id=None, date=None):
        """
            Constructor

            @param site_id: the site ID (defaults to default site)
            @param date: the date of the report (defaults to today)
        """

        if site_id is None:
            site_id = current.deployment_settings.get_org_default_site()
        self.site_id = site_id

        if date is None:
            date = current.request.utcnow.date()
        self.date = date

    # -------------------------------------------------------------------------
    def extract(self):
        """
            Extract the data for this report
        """

        db = current.db
        s3db = current.s3db

        T = current.T

        site_id = self.site_id
        date = self.date

        # Identify the relevant cases
        ctable = s3db.dvr_case
        query = (ctable.site_id == site_id) & \
                ((ctable.date == None) | (ctable.date <= date)) & \
                ((ctable.closed_on == None) | (ctable.closed_on >= date)) & \
                (ctable.archived != True) & \
                (ctable.deleted != True)
        rows = db(query).select(ctable.id,
                                ctable.person_id,
                                ctable.date,
                                ctable.closed_on,
                                )

        # Count them
        old_total, ins, outs = 0, 0, 0
        person_ids = set()
        for row in rows:
            person_ids.add(row.person_id)
            if not row.date or row.date < date:
                old_total += 1
            else:
                ins += 1
            if row.closed_on and row.closed_on == date:
                outs += 1
        result = {"old_total": old_total,
                  "new_total": old_total - outs + ins,
                  "ins": ins,
                  "outs": outs,
                  }

        # Add completed appointments as pr_person components
        atypes = {"BAMF": None,
                  "GU": None,
                  "Transfer": None,
                  "X-Ray": None,
                  }
        COMPLETED = 4
        attable = s3db.dvr_case_appointment_type
        query = attable.name.belongs(atypes.keys())
        rows = db(query).select(attable.id,
                                attable.name,
                                )
        add_components = s3db.add_components
        hooks = []
        for row in rows:
            type_id = row.id
            name = row.name
            atypes[name] = alias = "appointment%s" % type_id
            hook = {"name": alias,
                    "joinby": "person_id",
                    "filterby": {"type_id": type_id,
                                 "status": COMPLETED,
                                 },
                    }
            hooks.append(hook)
        s3db.add_components("pr_person", dvr_case_appointment = hooks)
        date_completed = lambda t: (T("%(event)s on") % {"event": T(t)},
                                    "%s.date" % atypes[t],
                                    )

        # Filtered component for paid allowances
        PAID = 2
        add_components("pr_person",
                       dvr_allowance = {"name": "payment",
                                        "joinby": "person_id",
                                        "filterby": {"status": PAID},
                                        },
                       )

        # Represent paid_on as date
        atable = s3db.dvr_allowance
        from s3 import S3DateTime
        atable.paid_on.represent = lambda dt: \
                                   S3DateTime.date_represent(dt,
                                                             utc=True,
                                                             )

        # Filtered component for family
        s3db.add_components("pr_person",
                            pr_group = {"name": "family",
                                        "link": "pr_group_membership",
                                        "joinby": "person_id",
                                        "key": "group_id",
                                        "filterby": {"group_type": 7},
                                        },
                            )

        # Get family roles
        gtable = s3db.pr_group
        mtable = s3db.pr_group_membership
        join = gtable.on(gtable.id == mtable.group_id)
        query = (mtable.person_id.belongs(person_ids)) & \
                (mtable.deleted != True) & \
                (gtable.group_type == 7)
        rows = db(query).select(mtable.person_id,
                                mtable.group_head,
                                mtable.role_id,
                                join = join,
                                )

        # Bulk represent all possible family roles (to avoid repeated lookups)
        represent = mtable.role_id.represent
        rtable = s3db.pr_group_member_role
        if hasattr(represent, "bulk"):
            query = (rtable.group_type == 7) & (rtable.deleted != True)
            roles = db(query).select(rtable.id)
            role_ids = [role.id for role in roles]
            represent.bulk(role_ids)

        # Create a dict of {person_id: role}
        roles = {}
        HEAD_OF_FAMILY = T("Head of Family")
        for row in rows:
            person_id = row.person_id
            role = row.role_id
            if person_id in roles:
                continue
            if (row.group_head):
                roles[person_id] = HEAD_OF_FAMILY
            elif role:
                roles[person_id] = represent(role)

        # Field method to determine the family role
        def family_role(row, roles=roles):
            person_id = row["pr_person.id"]
            return roles.get(person_id, "")

        # Dummy virtual fields to produce empty columns
        from s3dal import Field
        ptable = s3db.pr_person
        empty = lambda row: ""
        if not hasattr(ptable, "xray_place"):
            ptable.xray_place = Field.Method("xray_place", empty)
        if not hasattr(ptable, "family_role"):
            ptable.family_role = Field.Method("family_role", family_role)

        # List fields for the report
        list_fields = ["family.id",
                       (T("ID"), "pe_label"),
                       (T("Name"), "last_name"),
                       "first_name",
                       "date_of_birth",
                       "gender",
                       "person_details.nationality",
                       (T("Family Role"), "family_role"),
                       (T("Room No."), "shelter_registration.shelter_unit_id"),
                       "case_flag_case.flag_id",
                       "dvr_case.comments",
                       date_completed("GU"),
                       date_completed("X-Ray"),
                       (T("X-Ray Place"), "xray_place"),
                       date_completed("BAMF"),
                       (T("BÜMA valid until"), "dvr_case.valid_until"),
                       "dvr_case.stay_permit_until",
                       (T("Allowance Payments"), "payment.paid_on"),
                       (T("Admitted on"), "dvr_case.date"),
                       "dvr_case.origin_site_id",
                       date_completed("Transfer"),
                       #"dvr_case.closed_on",
                       "dvr_case.status_id",
                       "dvr_case.destination_site_id",
                       ]

        from s3 import FS
        query = FS("id").belongs(person_ids)
        resource = s3db.resource("pr_person", filter = query)

        data = resource.select(list_fields,
                               represent = True,
                               raw_data = True,
                               # Keep families together, eldest member first
                               orderby = ["pr_family_group.id",
                                          "pr_person.date_of_birth",
                                          ],
                               )

        # Generate headers, labels, types for XLS report
        rfields = data.rfields
        columns = []
        headers = {}
        types = {}
        for rfield in rfields:
            colname = rfield.colname
            if colname in ("dvr_case_flag_case.flag_id",
                           "pr_family_group.id",
                           ):
                continue
            columns.append(colname)
            headers[colname] = rfield.label
            types[colname] = rfield.ftype

        # Post-process rows
        rows = []
        from s3 import s3_str
        for row in data.rows:

            flags = "dvr_case_flag_case.flag_id"
            comments = "dvr_case.comments"

            raw = row["_row"]
            if raw[flags]:
                items = ["%s: %s" % (T("Advice"), s3_str(row[flags]))]
                if raw[comments]:
                    items.insert(0, raw[comments])
                row[comments] = ", ".join(items)
            rows.append(row)

        # Add XLS report data to result
        report = {"columns": columns,
                  "headers": headers,
                  "types": types,
                  "rows": rows,
                  }
        result["report"] = report

        return result

    # -------------------------------------------------------------------------
    def store(self, authorised=None):
        """
            Store this report in dvr_site_activity
        """

        db = current.db
        s3db = current.s3db
        auth = current.auth
        settings = current.deployment_settings

        # Table name and table
        tablename = "dvr_site_activity"
        table = s3db.table(tablename)
        if not table:
            return None

        # Get the current site activity record
        query = (table.date == self.date) & \
                (table.site_id == self.site_id) & \
                (table.deleted != True)
        row = db(query).select(table.id,
                               limitby = (0, 1),
                               orderby = ~table.created_on,
                               ).first()

        # Check permission
        if authorised is None:
            has_permission = current.auth.s3_has_permission
            if row:
                authorised = has_permission("update", tablename, record_id=row.id)
            else:
                authorised = has_permission("create", tablename)
        if not authorised:
            from s3 import S3PermissionError
            raise S3PermissionError

        # Extract the data
        data = self.extract()

        # Custom header for Excel Export (disabled for now)
        settings.base.xls_title_row = lambda sheet: self.summary(sheet, data)

        # Export as XLS
        title = current.T("Resident List")
        from s3.s3export import S3Exporter
        exporter = S3Exporter().xls
        report = exporter(data["report"],
                          title = title,
                          as_stream = True,
                          )

        # Construct the filename
        filename = "%s_%s_%s.xls" % (title, self.site_id, str(self.date))

        # Store the report
        report_ = table.report.store(report, filename)
        record = {"site_id": self.site_id,
                  "old_total": data["old_total"],
                  "new_total": data["new_total"],
                  "cases_new": data["ins"],
                  "cases_closed": data["outs"],
                  "date": self.date,
                  "report": report_,
                  }

        # Customize resource
        from s3 import S3Request
        r = S3Request("dvr", "site_activity",
                      current.request,
                      args = [],
                      get_vars = {},
                      )
        r.customise_resource("dvr_site_activity")

        if row:
            # Trigger auto-delete of the previous file
            row.update_record(report=None)
            # Update it
            success = row.update_record(**record)
            if success:
                s3db.onaccept(table, record, method="create")
                result = row.id
            else:
                result = None
        else:
            # Create a new one
            record_id = table.insert(**record)
            if record_id:
                record["id"] = record_id
                s3db.update_super(table, record)
                auth.s3_set_record_owner(table, record_id)
                auth.s3_make_session_owner(table, record_id)
                s3db.onaccept(table, record, method="create")
                result = record_id
            else:
                result = None

        return result

    # -------------------------------------------------------------------------
    def summary(self, sheet, data=None):
        """
            Header for the Excel sheet

            @param sheet: the sheet
            @param data: the data dict from extract()

            @return: the number of rows in the header
        """

        length = 3

        if sheet is not None and data is not None:

            T = current.T
            from s3 import S3DateTime, s3_unicode
            output = (("Date", S3DateTime.date_represent(self.date, utc=True)),
                      ("Previous Total", data["old_total"]),
                      ("Admissions", data["ins"]),
                      ("Departures", data["outs"]),
                      ("Current Total", data["new_total"]),
                      )

            import xlwt
            label_style = xlwt.XFStyle()
            label_style.font.bold = True

            col_index = 3
            for label, value in output:
                label_ = s3_unicode(T(label))
                value_ = s3_unicode(value)

                # Adjust column width
                width = max(len(label_), len(value_))
                sheet.col(col_index).width = max(width * 310, 2000)

                # Write the label
                current_row = sheet.row(0)
                current_row.write(col_index, label_, label_style)

                # Write the data
                current_row = sheet.row(1)
                current_row.write(col_index, value_)
                col_index += 1

        return length

# END =========================================================================
