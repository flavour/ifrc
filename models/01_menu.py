# -*- coding: utf-8 -*-

"""
    Global menus
"""

if auth.permission.format in ("html"):

    # =========================================================================
    # Import default menu structures and layouts
    #
    from eden.menus import *
    from eden.layouts import *

    # Create a Storage for menus
    menu = current.menu = Storage()

    # =========================================================================
    # Application main menu
    #
    menu.main = MM()(

        # Standard modules-menu
        #S3MainMenu.menu_modules(),

        # Custom modules-menu
        homepage("gis")(
            MM("Events", c="irs", f="ireport"),
        ),
        homepage("hrm", "org")(
            MM("Staff", c="hrm", f="human_resource", vars={"group":"staff"}),
            MM("Volunteers", c="hrm", f="human_resource", vars={"group":"volunteer"}),
            MM("Teams", c="hrm", f="group"),
            MM("Organisations", c="org", f="organisation"),
            MM("Offices", c="org", f="office"),
            MM("Job Roles", c="hrm", f="job_role"),
            #MM("Skill List", c="hrm", f="skill"),
            MM("Training Events", c="hrm", f="training_event"),
            MM("Training Courses", c="hrm", f="course"),
            #MM("Certificate List", c="hrm", f="certificate"),
        ),
        homepage("inv", "supply")(
            MM("Warehouses", c="inv", f="warehouse"),
            MM("Received Shipments", c="inv", f="recv"),
            MM("Sent Shipments", c="inv", f="send"),
            MM("Items", c="supply", f="item"),
            MM("Item Catalogues", c="supply", f="catalog"),
            MM("Item Categories", c="supply", f="item_category"),
        ),
        homepage("asset")(
            MM("Assets", c="asset", f="asset"),
            MM("Items", c="asset", f="item"),
        ),
        homepage("survey")(
            MM("Assessment Templates", c="survey", f="template"),
            MM("Disaster Assessments", c="survey", f="series"),
        ),
        homepage("project")(
            MM("Projects", c="project", f="project"),
            MM("Communities", c="project", f="activity"),
            MM("Reports", c="project", f="report"),
        )

        # Standard service menus
        #S3MainMenu.menu_help(right=True),
        #S3MainMenu.menu_auth(right=True),
        #S3MainMenu.menu_lang(right=True),
        #S3MainMenu.menu_admin(right=True),
        #S3MainMenu.menu_gis(right=True)
    )

    # Custom Language Menu
    menu_lang = ML("Language", right=True)
    for language in s3.l10n_languages.items():
        code, name = language
        menu_lang(
            ML(name, translate=False, lang_code=code, lang_name=name)
        )

    # Custom Personal Menu
    if not auth.is_logged_in():
        login_next = URL(args=request.args, vars=request.vars)
        if request.controller == "default" and \
           request.function == "user" and \
           "_next" in request.get_vars:
               login_next = request.get_vars["_next"]

        self_registration = deployment_settings.get_security_self_registration()

        menu.personal = MP()(
                            MP("Register", c="default", f="user",
                               m="register", check=self_registration),
                            MP("Sign In", c="default", f="user",
                               m="login", vars=dict(_next=login_next)),
                            MP("Lost Password", c="default", f="user",
                               m="retrieve_password"),
                            menu_lang
                        )
    else:
        menu.personal = MP()(
                            MP("Administration", c="admin", f="index",
                               check=s3_has_role(ADMIN)),
                            MP("Sign Out", c="default", f="user",
                               m="logout"),
                            MP("Change Password", c="default", f="user",
                               m="change_password"),
                            menu_lang,
                        )

    # =========================================================================
    # Custom controller menus
    #
    manager_mode = lambda i: session.s3.hrm.mode is None
    personal_mode = lambda i: session.s3.hrm.mode is not None
    is_org_admin = lambda i: session.s3.hrm.orgs and True or \
                             ADMIN in session.s3.roles

    staff = dict(group="staff")
    volunteers = dict(group="volunteer")

    s3_menu_dict = {

        # ---------------------------------------------------------------------
        # GIS Mapping
        "gis": None,

        # ---------------------------------------------------------------------
        # HRM Human Resources / ORG Organisation Registry (shared)
        "hrm": M()(
                    M("Staff", c="hrm", f=("human_resource", "person"),
                      check=manager_mode, vars=staff)(
                        M("New Staff Member", m="create",
                          vars=staff),
                        M("List All",
                          vars=staff),
                        M("Search", m="search",
                          vars=staff),
                        M("Report", m="report",
                          vars=Storage(group="staff",
                                       rows="course",
                                       cols="L1",
                                       fact="person_id",
                                       aggregate="count")),
                        M("Report Expiring Contracts",
                          vars=dict(group="staff", expiring=1)),
                        M("Import", m="import",
                          vars=staff, p="create"),
                        #M("Dashboard", f="index"),
                    ),
                    M("Volunteers", c="hrm", f=("human_resource", "person"),
                      check=manager_mode, vars=volunteers)(
                        M("New Volunteer", m="create",
                          vars=volunteers),
                        M("List All",
                          vars=volunteers),
                        M("Search", m="search",
                          vars=volunteers),
                        M("Report", m="report",
                          vars=Storage(group="volunteer",
                                       rows="course",
                                       cols="L1",
                                       fact="person_id",
                                       aggregate="count")),
                        M("Import", m="import",
                          vars=volunteers, p="create"),
                    ),
                    M("Teams", c="hrm", f="group",
                      check=manager_mode)(
                        M("New Team", m="create"),
                        M("List All"),
                    ),
                    M("Organizations", c="org", f="organisation",
                      check=manager_mode)(
                        M("New", m="create"),
                        M("List All"),
                        M("Search", m="search"),
                        #M("Import", m="import", p="create")
                    ),
                    M("Offices", c="org", f="office",
                      check=manager_mode)(
                        M("New", m="create"),
                        M("List All"),
                        M("Search", m="search"),
                        M("Import", m="import", p="create"),
                    ),
                    M("Job Role Catalog", c="hrm", f="job_role",
                      check=manager_mode)(
                        M("New Job Role", m="create"),
                        M("List All"),
                    ),
                    #M("Skill Catalog", f="skill",
                      #check=manager_mode)(
                        #M("New Skill", m="create"),
                        #M("List All"),
                        ##M("Skill Provisions", f="skill_provision"),
                    #),
                    M("Training Events", c="hrm", f="training_event",
                      check=manager_mode)(
                        M("New Training Event", m="create"),
                        M("List All"),
                        M("Search", m="search"),
                        M("Training Report", f="training", m="report",
                          vars=dict(rows="training_event_id$course_id",
                                    cols="month",
                                    fact="person_id",
                                    aggregate="count")),
                        M("Import Participant List", f="training", m="import"),
                    ),
                    M("Training Course Catalog", c="hrm", f="course",
                      check=manager_mode)(
                        M("New Training Course", m="create"),
                        M("List All"),
                        #M("Course Certificates", f="course_certificate"),
                    ),
                    #M("Certificate Catalog", c="hrm", f="certificate",
                      #check=manager_mode)(
                        #M("New Certificate", m="create"),
                        #M("List All"),
                        #M("Skill Equivalence", f="certificate_skill"),
                    #),
                    M("Profile", c="hrm", f="person",
                      check=personal_mode, vars=dict(mode="personal")),
                    # This provides the link to switch to the manager mode:
                    M("Human Resources", c="hrm", f="index",
                      check=[personal_mode, is_org_admin]),
                    # This provides the link to switch to the personal mode:
                    M("Personal Profile", c="hrm", f="person",
                      check=manager_mode, vars=dict(mode="personal"))
                ),

        # ---------------------------------------------------------------------
        # IRS / Incident Reporting
        "irs": M(c="irs")(
                    M("Incident Reports", f="ireport")(
                        M("New", m="create"),
                        M("List All"),
                        M("Open Incidents", vars={"open":1}),
                        M("Timeline", args="timeline"),
                        #M("Search", m="search")
                    ),
                    M("Incident Categories", f="icategory", restrict=[ADMIN])(
                        M("New", m="create"),
                        M("List All"),
                    ),
                    #M("Ushahidi " + T("Import"), f="ireport", restrict=[ADMIN],
                      #args="ushahidi")
                ),

    }
    s3_menu_dict["org"] = s3_menu_dict["hrm"]

    # =========================================================================
    # Compose the option menu
    #
    controller = request.controller
    if controller not in s3_menu_dict:
        # Fall back to standard menu for this controller
        menu.options = S3OptionsMenu(controller).menu
    else:
        # Use custom menu
        menu.options = s3_menu_dict[controller]

    current.menu.breadcrumbs = S3OptionsMenu.breadcrumbs

else:
    current.menu = Storage(main=None, options=None)

# END =========================================================================
