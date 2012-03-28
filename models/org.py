# -*- coding: utf-8 -*-

"""
    Organization Registry
"""

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

    #stable = s3db.org_site
    #siteorgs = db(stable.owned_by_facility.belongs(roles)).select(stable.organisation_id)
    #for org in siteorgs:
        #if org.organisation_id not in orgs:
            #orgs.append(org.organisation_id)

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
