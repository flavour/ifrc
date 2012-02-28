# -*- coding: utf-8 -*-

"""
    Organization Registry
"""

# -----------------------------------------------------------------------------
# Defined in the Model for use from Multiple Controllers for unified menus
#
def org_organisation_controller():
    """ RESTful CRUD controller """

    # T = current.T
    # db = current.db
    # gis = current.gis
    s3 = current.response.s3
    manager = current.manager

    tablename = "org_office"
    table = s3db[tablename]

    # Pre-process
    def prep(r):
        if r.interactive:
            r.table.country.default = gis.get_default_country("code")
            if r.component_name == "human_resource" and r.component_id:
                # Workaround until widget is fixed:
                hr_table = db.hrm_human_resource
                hr_table.person_id.widget = None
                hr_table.person_id.writable = False
            elif r.component_name == "office" and \
               r.method and r.method != "read":
                # Don't want to see in Create forms
                # inc list_create (list_fields over-rides)
                table = r.component.table
                s3.address_hide(table)
                # Process Base Location
                #manager.configure(table._tablename,
                #                  onaccept=s3.address_onaccept)
            elif r.component_name == "task" and \
                 r.method != "update" and r.method != "read":
                    # Create or ListCreate
                    r.component.table.organisation_id.default = r.id
                    r.component.table.status.writable = False
                    r.component.table.status.readable = False
            elif r.component_name == "project" and r.link:
                # Hide/show host role after project selection in embed-widget
                tn = r.link.tablename
                manager.configure(tn,
                                  post_process="hide_host_role($('#%s').val());")
                script = "s3.hide_host_role.js"
                s3.scripts.append( "%s/%s" % (s3.script_dir, script))
        return True
    s3.prep = prep

    rheader = s3db.org_rheader
    output = s3_rest_controller("org", "organisation",
                                native=False, rheader=rheader)
    return output

# -----------------------------------------------------------------------------
def org_office_controller():
    """ RESTful CRUD controller """

    # gis = current.gis
    # request = current.request
    # session = current.session
    s3 = current.response.s3
    manager = current.manager
    settings = current.deployment_settings

    tablename = "org_office"
    table = s3db[tablename]

    # Load Models to add tabs
    if settings.has_module("inv"):
        manager.load("inv_inv_item")
    elif settings.has_module("req"):
        # (gets loaded by Inv if available)
        manager.load("req_req")

    if isinstance(request.vars.organisation_id, list):
        request.vars.organisation_id = request.vars.organisation_id[0]

    office_search = s3base.S3Search(
        advanced=(s3base.S3SearchSimpleWidget(
                    name="office_search_text",
                    label=T("Search"),
                    comment=T("Search for office by text."),
                    field=["name", "comments", "email"]
                  ),
                  s3base.S3SearchOptionsWidget(
                    name="office_search_org",
                    label=T("Organization"),
                    comment=T("Search for office by organization."),
                    field=["organisation_id"],
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationHierarchyWidget(
                    name="office_search_location",
                    comment=T("Search for office by location."),
                    represent ="%(name)s",
                    cols = 3
                  ),
                  s3base.S3SearchLocationWidget(
                    name="office_search_map",
                    label=T("Map"),
                  ),
        ))
    manager.configure(tablename,
                      search_method = office_search)

    # Pre-processor
    def prep(r):
        table = r.table
        if r.representation == "popup":
            organisation = r.vars.organisation_id or \
                           session.s3.organisation_id or ""
            if organisation:
                table.organisation_id.default = organisation

        elif r.representation == "plain":
            # Map popups want less clutter
            table.obsolete.readable = False
            if r.record.type == 5:
                s3.crud_strings[tablename].title_display = T("Warehouse Details")

        if r.record and deployment_settings.has_module("hrm"):
            # Cascade the organisation_id from the office to the staff
            hrm_table = db.hrm_human_resource
            hrm_table.organisation_id.default = r.record.organisation_id
            hrm_table.organisation_id.writable = False

        if r.interactive or r.representation == "aadata":
            if not r.component and deployment_settings.has_module("inv"):
                # Filter out Warehouses, since they have a dedicated controller
                response.s3.filter = (table.type != 5) | \
                                     (table.type == None)

        if r.interactive:
            if settings.has_module("inv"):
                # Don't include Warehouses in the type dropdown
                s3.org_office_type_opts.pop(5)
                table.type.requires = IS_NULL_OR(IS_IN_SET(s3.org_office_type_opts))

            if r.record and r.record.type == 5: # 5 = Warehouse
                s3.crud_strings[tablename] = s3.org_warehouse_crud_strings

            if r.method == "create":
                table.obsolete.readable = table.obsolete.writable = False
                if r.vars.organisation_id and r.vars.organisation_id != "None":
                    table.organisation_id.default = r.vars.organisation_id

            if r.method and r.method != "read":
                # Don't want to see in Create forms
                # inc list_create (list_fields over-rides)
                table.obsolete.writable = False
                table.obsolete.readable = False
                s3.address_hide(table)

            if r.component:
                if r.component.name == "inv_item" or \
                   r.component.name == "recv" or \
                   r.component.name == "send":
                    # Filter out items which are already in this inventory
                    s3db.inv_prep(r)
                elif r.component.name == "human_resource":
                    # Filter out people which are already staff for this office
                    s3_filter_staff(r)
                    # Cascade the organisation_id from the hospital to the staff
                    hrm_table.organisation_id.default = r.record.organisation_id
                    hrm_table.organisation_id.writable = False

                elif r.component.name == "req":
                    if r.method != "update" and r.method != "read":
                        # Hide fields which don't make sense in a Create form
                        # inc list_create (list_fields over-rides)
                        s3db.req_create_form_mods()

        return True
    s3.prep = prep

    rheader = s3db.org_rheader

    return s3_rest_controller("org", "office", rheader=rheader)

# =============================================================================
# Used by both HRM & Org Controllers
def org_filter():
    """
        Find the Organisation(s) this user is entitled to view
        i.e. they have the organisation access role or a site access role

        @ToDo: Support Delegations!
    """

    if s3_has_role("HR_READ") or s3_has_role("HR_EDIT") or s3_has_role("HR_ADMIN"):
        # Continue to check Orgs
        pass
    else:
        # No HR Role so don't check Orgs
        session.s3.hrm.orgs = None
        return

    roles = session.s3.roles or []
    table = s3db.org_organisation
    orgs = db(table.owned_by_organisation.belongs(roles)).select(table.id)
    orgs = [org.id for org in orgs]

    stable = s3db.org_site
    siteorgs = db(stable.owned_by_facility.belongs(roles)).select(stable.organisation_id)
    for org in siteorgs:
        if org.organisation_id not in orgs:
            orgs.append(org.organisation_id)

    if orgs:
        session.s3.hrm.orgs = orgs
    else:
        session.s3.hrm.orgs = None

# -----------------------------------------------------------------------------
@auth.requires_login()
def hr_menu_prep():
    """ Application Menu """

    # Module Name
    try:
        module_name = deployment_settings.modules[module].name_nice
    except:
        module_name = T("Human Resources Management")
    response.title = module_name

    # Automatically choose an organisation
    if session.s3.hrm.orgs is None:
        org_filter()

    # Set mode
    roles = session.s3.roles or []
    if session.s3.hrm.mode != "personal" and \
       (ADMIN in roles or session.s3.hrm.orgs):
        session.s3.hrm.mode = None
    else:
        session.s3.hrm.mode = "personal"

# -----------------------------------------------------------------------------
hrm_dashboard = UL(LI(A(H2("STAFF & VOLUNTEERS"),
                        UL(LI(A("Manage Staff & Volunteer Data",
                                _href=URL(f="human_resource"))),
                           LI(A("Manage Teams Data",
                                _href=URL(f="group")))),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_staff_wide.png"]),
                            _alt="Staff and Volunteers"),
                      _href=URL(c="hrm", f="index"))),
                   LI(A(H2("OFFICES"),
                        UL(LI(A("Manage Offices Data",
                                _href=URL(c="org", f="office"))),
                           LI(A("Manage Organisations Data",
                                _href=URL(c="org", f="organisation")))),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_office.png"]),
                            _alt="Offices"),
                      _href=URL(c="org", f="index"))),
                   LI(A(H2("CATALOGUES"),
                        UL(#LI(A("Certificates",
                           #     _href=URL(f="certificate"))),
                           LI(A("Training Courses",
                                _href=URL(f="course"))),
                           #LI(A("Skills",
                           #     _href=URL(f="skill"))),
                           LI(A("Job Roles",
                                _href=URL(f="job_role")))),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_catalogue.png"]),
                            _alt="Catalogues"),
                      _href=URL(c="hrm", f="index"))),
                   _id="sub-dashboard")

# END =========================================================================
