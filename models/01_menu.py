# -*- coding: utf-8 -*-

"""
    Global menus
"""

if auth.permission.format in ("html"):

    # =========================================================================
    # Application main menu
    # -> To customize, replace the standard components by the desired items
    # -> Put right-hand menu options in reverse order!
    #
    menu.main = MM()(

        # Standard modules-menu
        #S3MainMenu.menu_modules(),

        # Custom modules-menu
        homepage("gis")(
        ),
        homepage("hrm", "org", name=T("Staff"))(
            MM("Staff", c="hrm", f="staff"),
            MM("Teams", c="hrm", f="group"),
            MM("Organizations", c="org", f="organisation"),
            MM("Offices", c="org", f="office"),
            MM("Job Roles", c="hrm", f="job_role"),
            #MM("Skill List", c="hrm", f="skill"),
            MM("Training Events", c="hrm", f="training_event"),
            MM("Training Courses", c="hrm", f="course"),
            MM("Certificate List", c="hrm", f="certificate"),
        ),
        homepage("hrm", name=T("Volunteers"))(
            MM("Volunteers", c="hrm", f="volunteer"),
            MM("Teams", c="hrm", f="group"),
            MM("Job Roles", c="hrm", f="job_role"),
            #MM("Skill List", c="hrm", f="skill"),
            MM("Training Events", c="hrm", f="training_event"),
            MM("Training Courses", c="hrm", f="course"),
            #MM("Certificate List", c="hrm", f="certificate"),
        ),
        homepage("member")(
            MM("Members", c="member", f="membership"),
        ),
        homepage("inv", "supply", "req")(
            MM("Warehouses", c="inv", f="warehouse"),
            MM("Received Shipments", c="inv", f="recv"),
            MM("Sent Shipments", c="inv", f="send"),
            MM("Items", c="supply", f="item"),
            MM("Item Catalogues", c="supply", f="catalog"),
            MM("Item Categories", c="supply", f="item_category"),
            M("Requests", c="req", f="req")(),
            #M("Commitments", f="commit")(),
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
        ),
        #homepage("event", "irs")(
        #    MM("Events", c="event", f="event"),
        #    MM("Incident Reports", c="irs", f="ireport"),
        #)

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

        current.menu.personal = MP()(
                            MP("Register", c="default", f="user",
                               m="register", check=self_registration),
                            MP("Login", c="default", f="user",
                               m="login", vars=dict(_next=login_next)),
                            MP("Lost Password", c="default", f="user",
                               m="retrieve_password"),
                            menu_lang
                        )
    else:
        current.menu.personal = MP()(
                            MP("Administration", c="admin", f="index",
                               check=s3_has_role(ADMIN)),
                            MP("Logout", c="default", f="user",
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
        #"gis": None,

        # ---------------------------------------------------------------------
        # HRM Human Resources / ORG Organisation Registry (shared)
        "hrm": M()(
                    M("Staff", c="hrm", f=("staff", "person"),
                      check=manager_mode)(
                        M("New Staff Member", m="create"),
                        M("List All"),
                        M("Search", m="search"),
                        M("Report", m="report",
                          vars=Storage(rows="course",
                                       cols="L1",
                                       fact="person_id",
                                       aggregate="count")),
                        M("Report Expiring Contracts",
                          vars=dict(expiring=1)),
                        M("Import", f="person", m="import",
                          vars=staff, p="create"),
                    ),
                    M("Volunteers", c="hrm", f=("volunteer", "person"),
                      check=manager_mode)(
                        M("New Volunteer", m="create"),
                        M("List All"),
                        M("Search", m="search"),
                        M("Report", m="report",
                          vars=Storage(rows="course",
                                       cols="L1",
                                       fact="person_id",
                                       aggregate="count")),
                        M("Import", f="person", m="import",
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
                        M("List All Training Events"),
                        M("Search Training Events", m="search"),
                        M("Search Training Participants", f="training",
                          m="search"),
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
                        M("Course Certificates", f="course_certificate"),
                    ),
                    M("Certificate Catalog", c="hrm", f="certificate",
                      check=manager_mode)(
                        M("New Certificate", m="create"),
                        M("List All"),
                        #M("Skill Equivalence", f="certificate_skill"),
                    ),
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
        # Event / IRS Incident Reports (shared)
        "irs": M()(
                    M("Events", c="event", f="event")(
                        M("New", m="create"),
                        M("List All"),
                    ),
                    M("Incident Reports", c="irs", f="ireport")(
                        M("New", m="create"),
                        M("List All"),
                        M("Open Incidents", vars={"open":1}),
                        M("Timeline", args="timeline"),
                        M("Search", m="search"),
                        M("Report", m="report",
                          vars=dict(rows="L1",
                                    cols="category",
                                    fact="datetime",
                                    aggregate="count"))
                    ),
                    M("Incident Categories", c="irs", f="icategory", check=s3_has_role(ADMIN))(
                        M("New", m="create"),
                        M("List All"),
                    ),
                ),
    }
    s3_menu_dict["org"] = s3_menu_dict["hrm"]
    s3_menu_dict["event"] = s3_menu_dict["irs"]

# END =========================================================================
