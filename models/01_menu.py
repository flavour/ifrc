# -*- coding: utf-8 -*-

"""
    Global menus & breadcrumbs
"""

if auth.permission.format in ("html"):
    # =========================================================================
    # Language Menu (available in all screens)
    #s3.menu_lang = [ T("Language"), True, "#"]
    #_menu_lang = []
    #for language in s3.l10n_languages.keys():
    #    _menu_lang.append([s3.l10n_languages[language], False, language])
    #s3.menu_lang.append(_menu_lang)

    # -------------------------------------------------------------------------
    # Help Menu (available in all screens)
    #s3.menu_help = [ T("Help"), True, "#",
    #        [
    #            [T("Contact us"), False,
    #             URL(c="default", f="contact")],
    #            [T("About"), False, URL(c="default", f="about")],
    #        ]
    #    ]

    # -------------------------------------------------------------------------
    # Auth Menu (available in all screens)
    if not auth.is_logged_in():

        login_next = URL(args=request.args, vars=request.vars)
        if request.controller == "default" and \
           request.function == "user" and \
           "_next" in request.get_vars:
               login_next = request.get_vars["_next"]

        self_registration = deployment_settings.get_security_self_registration()

        if self_registration:
            s3.menu_auth = [[T("Register"),
                             URL(c="default", f="user/register")],
                            [T("Sign In"),
                             URL(c="default", f="user/login",
                                 vars=dict(_next=login_next))],
                            [T("Lost Password"),
                             URL(c="default", f="user/retrieve_password")]
                            ]
        else:
            s3.menu_auth = [[T("Sign In"),
                             URL(c="default", f="user/login",
                                 vars=dict(_next=login_next))],
                            [T("Lost Password"),
                             URL(c="default", f="user/retrieve_password")]
                            ]
    else:
        s3.menu_auth = [[T("Sign Out"), URL(c="default",
                                            f="user/logout")],
                        [T("Change Password"), URL(c="default",
                                                   f="user/change_password")],
                        ]


    # -------------------------------------------------------------------------
    # Menu for Admin module
    # (defined here as used in several different Controller files)
    admin_menu_messaging = [
                [T("Email Settings"), False,
                 URL(c="msg", f="email_settings", args=[1, "update"])],
                [T("SMS Settings"), False,
                 URL(c="msg", f="setting", args=[1, "update"])],
                [T("Twitter Settings"), False,
                 URL(c="msg", f="twitter_settings", args=[1, "update"])],
        ]
    admin_menu_options = [
        #[T("Settings"), False, URL(c="admin", f="settings"),
        #    admin_menu_messaging,
        #    # Hidden until useful again
        #    #[T("Edit Themes"), False, URL(c="admin", f="theme")]
        #],
        [T("User Management"), False, URL(c="admin", f="user"), [
            [T("Users"), False, URL(c="admin", f="user")],
            [T("Roles"), False, URL(c="admin", f="role")],
            [T("Organizations"), False, URL(c="admin", f="organisation")],
            #[T("Roles"), False, URL(c="admin", f="group")],
            #[T("Membership"), False, URL(c="admin", f="membership")],
        ]],
        [T("Database"), False, URL(c="appadmin", f="index"), [
            # @ToDo: UI for the current Import approach (S3CSV)
            [T("Import"), False, URL(c="admin", f="import_file")],
            #[T("Import"), False, URL(c="admin", f="import_data")],
            #[T("Export"), False, URL(c="admin", f="export_data")],
            #[T("Import Jobs"), False, URL(c="admin", f="import_job")],
            [T("Raw Database access"), False, URL(c="appadmin", f="index")]
        ]],
        # Hidden until ready for production
        [T("Synchronization"), False, URL(c="sync", f="index"), [
            [T("Settings"), False, aURL(p="update", c="sync", f="config",
                                        args=["1", "update"])],
            [T("Repositories"), False, URL(c="sync", f="repository")],
            [T("Log"), False, URL(c="sync", f="log")],
        ]],
        #[T("Edit Application"), False,
        # URL(a="admin", c="default", f="design", args=[request.application])],
        [T("Tickets"), False, URL(c="admin", f="errors")],
        [T("Portable App"), False, URL(c="admin", f="portable")],
    ]

    # -------------------------------------------------------------------------
    # Modules Menu (available in all Controllers)
    # NB This is hardcoded for IFRC
    s3.menu_modules = []
    # Home always 1st
    #_module = deployment_settings.modules["default"]
    #s3.menu_modules.append([_module.name_nice, False,
    #                        URL(c="default", f="index")])

    # Modules to hide due to insufficient permissions
    #hidden_modules = auth.permission.hidden_modules()

    # The Modules to display at the top level (in order)
    #for module_type in [1, 2, 3, 4, 5, 6]:
    #    for module in deployment_settings.modules:
    #        if module in hidden_modules:
    #            continue
    #        _module = deployment_settings.modules[module]
    #        if (_module.module_type == module_type):
    #            if not _module.access:
    #                s3.menu_modules.append([_module.name_nice, False,
    #                                        aURL(c=module, f="index")])
    #            else:
    #                authorised = False
    #                groups = re.split("\|", _module.access)[1:-1]
    #                for group in groups:
    #                    if s3_has_role(group):
    #                        authorised = True
    #                if authorised == True:
    #                    s3.menu_modules.append([_module.name_nice, False,
    #                                            URL(c=module, f="index")])

    # Modules to display off the 'more' menu
    #modules_submenu = []
    #for module in deployment_settings.modules:
    #    if module in hidden_modules:
    #        continue
    #    _module = deployment_settings.modules[module]
    #    if (_module.module_type == 10):
    #        if not _module.access:
    #            modules_submenu.append([_module.name_nice, False,
    #                                    aURL(c=module, f="index")])
    #        else:
    #            authorised = False
    #            groups = re.split("\|", _module.access)[1:-1]
    #            for group in groups:
    #                if s3_has_role(group):
    #                    authorised = True
    #            if authorised == True:
    #                modules_submenu.append([_module.name_nice, False,
    #                                        URL(c=module, f="index")])
    #if modules_submenu:
    #    # Only show the 'more' menu if there are entries in the list
    #    module_more_menu = ([T("more"), False, "#"])
    #    module_more_menu.append(modules_submenu)
    #    s3.menu_modules.append(module_more_menu)

    # Admin always last
    if s3_has_role(ADMIN):
        _module = deployment_settings.modules["admin"]
        s3.menu_admin = [_module.name_nice,
                         URL(c="admin", f="index"), [
                            # This menu isn't shown in IFRC Theme yet
                            #[T("Settings"), URL(c="admin", f="settings")],
                            [T("Users"), URL(c="admin", f="user")],
                            [T("Database"), URL(c="appadmin", f="index")],
                            [T("Import"), URL(c="admin", f="import_file")],
                            [T("Synchronization"), URL(c="sync", f="index")],
                            [T("Tickets"), URL(c="admin", f="errors")],
                         ]]
    #else:
    #    s3.menu_admin = []

    # -------------------------------------------------------------------------
    # Build overall menu out of components
    #response.menu = s3.menu_modules
    #response.menu.append(s3.menu_help)
    #response.menu.append(s3.menu_auth)
    response.menu = s3.menu_auth
    #if deployment_settings.get_gis_menu():
    #    # Do not localize this string.
    #    s3.gis_menu_placeholder = "GIS menu placeholder"
    #    # Add a placeholder for the regions menu, which cannot be constructed
    #    # until the gis_config table is available. Put it near the language menu.
    #    response.menu.append(s3.gis_menu_placeholder)
    if s3.menu_admin:
        response.menu.append(s3.menu_admin)
    # this check is handled by s3tools for personal menu,
    # language select isn't rendered like other menu items in ifrc
    #if deployment_settings.get_L10n_display_toolbar():
    #    response.menu.append(s3.menu_lang)

    # Menu helpers ============================================================
    def s3_menu(controller, postp=None, prep=None):
        """
            appends controller specific options to global menu
            picks up from 01_menu, called from controllers

            @postp - additional postprocessor,
                     assuming postp acts on response.menu_options
            @prep  - pre-processor
            @ToDo: FIXIT - alter here when you alter controller name
        """
        if controller in s3_menu_dict:

            if prep:
                prep()

            # menu
            menu_config = s3_menu_dict[controller]
            menu = menu_config["menu"]

            # role hooks
            if s3_has_role(AUTHENTICATED) and "on_auth" in menu_config:
                menu.extend(menu_config["on_auth"])

            if s3_has_role(ADMIN) and "on_admin" in menu_config:
                menu.extend(menu_config["on_admin"])

            if s3_has_role(EDITOR) and "on_editor" in menu_config:
                menu.extend(menu_config["on_editor"])

            # conditionals
            conditions = [x for x in menu_config if re.match(r"condition[0-9]+", x)]
            for condition in conditions:
                if menu_config[condition]():
                    menu.extend(menu_config["conditional%s" % condition[9:]])

            needle = request["wsgi"]["environ"]["PATH_INFO"]
            for i in xrange(len(menu)):
                if str(menu[i][2]) in needle:
                    menu[i][1] = True
                    if len(menu[i]) >= 4:
                        # if has submenus to it
                        for j in xrange(len(menu[i][3])):
                            if str(menu[i][3][j][2]) == needle:
                                menu[i][3][j][1] = True
                                break
                    break

            response.menu_options = menu

            if postp:
                postp()

    # =========================================================================
    # Role-dependent Menu options
    # =========================================================================
    if s3_has_role(ADMIN):
        pr_menu = [
                [T("Person"), False, aURL(f="person", args=None), [
                    [T("New"), False, aURL(p="create", f="person",
                                           args="create")],
                    [T("Search"), False, aURL(f="index")],
                    [T("List All"), False, aURL(f="person")],
                ]],
                [T("Groups"), False, aURL(f="group"), [
                    [T("New"), False, aURL(p="create", f="group",
                                           args="create")],
                    [T("List All"), False, aURL(f="group")],
                ]],
            ]
    else:
        pr_menu = []

    # =========================================================================
    # Settings-dependent Menu options
    # =========================================================================
    # CRUD strings for inv_recv
    # (outside condtional model load since need to be visible to menus)
    if deployment_settings.get_inv_shipment_name() == "order":
        ADD_RECV = T("Add Order")
        LIST_RECV = T("List Orders")
        s3.crud_strings["inv_recv"] = Storage(
            title_create = ADD_RECV,
            title_display = T("Order Details"),
            title_list = LIST_RECV,
            title_update = T("Edit Order"),
            title_search = T("Search Orders"),
            subtitle_create = ADD_RECV,
            subtitle_list = T("Orders"),
            label_list_button = LIST_RECV,
            label_create_button = ADD_RECV,
            label_delete_button = T("Delete Order"),
            msg_record_created = T("Order Created"),
            msg_record_modified = T("Order updated"),
            msg_record_deleted = T("Order canceled"),
            msg_list_empty = T("No Orders registered")
        )
    else:
        ADD_RECV = T("Receive Shipment")
        LIST_RECV = T("List Received Shipments")
        s3.crud_strings["inv_recv"] = Storage(
            title_create = ADD_RECV,
            title_display = T("Received Shipment Details"),
            title_list = LIST_RECV,
            title_update = T("Edit Received Shipment"),
            title_search = T("Search Received Shipments"),
            subtitle_create = ADD_RECV,
            subtitle_list = T("Received Shipments"),
            label_list_button = LIST_RECV,
            label_create_button = ADD_RECV,
            label_delete_button = T("Delete Received Shipment"),
            msg_record_created = T("Shipment Created"),
            msg_record_modified = T("Received Shipment updated"),
            msg_record_deleted = T("Received Shipment canceled"),
            msg_list_empty = T("No Received Shipments")
        )

    if deployment_settings.get_project_community_activity():
        list_activities_label = T("List All Communities")
        import_activities_label = T("Import Project Communities")
    else:
        list_activities_label = T("List All Activities")
        import_activities_label = T("Import Project Activities")

    if deployment_settings.get_project_drr():
        project_menu = {
            "menu": [
                [T("Projects"), False, aURL(f="project"),[
                    [T("Add New Project"), False, aURL(p="create", f="project", args="create")],
                    [T("List All Projects"), False, aURL(f="project")],
                    [list_activities_label, False, aURL(f="activity")],
                    [T("Search"), False, aURL(f="project", args="search")],
                ]],
                [T("Reports"), False, aURL(f="report"),[
                    [T("Who is doing What Where"), False, aURL(f="activity", args="report")],
                    [T("Beneficiaries"),
                     False, aURL(f="beneficiary",
                                 args="report",
                                 vars=Storage(rows="project_id",
                                              cols="bnf_type",
                                              fact="number",
                                              aggregate="sum"))],
                    [T("Funding"),
                     False, aURL(f="organisation",
                                 args="report",
                                 vars=Storage(rows="project_id",
                                              cols="organisation_id",
                                              fact="amount",
                                              aggregate="sum"))],
                ]],
                [T("Import"), False, aURL(f="index"),[
                    [T("Import Projects"), False, aURL(p="create", f="project",
                                                    args="import")],
                    [T("Import Project Organizations"), False, aURL(p="create", f="organisation",
                                                                    args="import")],
                    [import_activities_label, False, aURL(p="create", f="activity",
                                                                args="import")],
                ]],
                [T("Activity Types"), False, aURL(f="activity_type"),[
                    [T("Add New Activity Type"), False, aURL(p="create", f="activity_type", args="create")],
                    [T("List All Activity Types"), False, aURL(f="activity_type")],
                    #[T("Search"), False, aURL(f="activity_type", args="search")]
                ]],
                [T("Hazards"), False, aURL(f="hazard"),[
                    [T("Add New Hazard"), False, aURL(p="create", f="hazard", args="create")],
                    [T("List All Hazards"), False, aURL(f="hazard")],
                ]],
                [T("Project Themes"), False, aURL(f="theme"),[
                    [T("Add New Theme"), False, aURL(p="create", f="theme", args="create")],
                    [T("List All Themes"), False, aURL(f="theme")],
                ]],
                [T("Beneficiary Types"), False, aURL(f="beneficiary_type"),[
                    [T("Add New Type"), False, aURL(p="create", f="beneficiary_type", args="create")],
                    [T("List All Types"), False, aURL(f="beneficiary_type")],
                ]],
            ],

        }

    elif s3_has_role("STAFF"):
        project_menu = {
            "menu": [
                [T("Projects"), False, aURL(f="project"),[
                    #[T("Add New Project"), False, aURL(p="create", f="project", args="create")],
                    [T("List Projects"), False, aURL(f="project")],
                    [T("Open Tasks for Project"), False, aURL(f="project", vars={"tasks":1})],
                ]],
                #[T("Tasks"), False, aURL(f="task"),[
                    #[T("Add New Task"), False, aURL(p="create", f="task", args="create")],
                    #[T("List All Tasks"), False, aURL(f="task")],
                    #[T("Search"), False, aURL(f="task", args="search")],
                #]],
                [T("Daily Work"), False, aURL(f="time"),[
                    [T("All Tasks"), False, aURL(f="task", args="search")],
                    [T("My Logged Hours"), False, aURL(f="time", vars={"mine":1})],
                    [T("Last Week's Work"),
                    False, aURL(f="time",
                                args="report",
                                vars={"rows":"person_id",
                                    "cols":"day",
                                    "fact":"hours",
                                    "aggregate":"sum",
                                    "week":1})],
                    [T("My Open Tasks"), False, aURL(f="task", vars={"mine":1})],
                ]],
            ],
            "on_admin": [
                [T("Admin"), False, None,[
                    [T("Activity Types"), False, aURL(f="activity_type")],
                    [T("Organizations"), False, aURL(f="organisation")],
                    [T("Import Tasks"), False, aURL(p="create", f="task",
                                                    args="import")],
                ]],
                [T("Reports"), False, aURL(f="report"),[
                    [T("Activity Report"),
                    False, aURL(f="activity",
                                args="report",
                                vars=Storage(rows="project_id",
                                            cols="name",
                                            fact="time_actual",
                                            aggregate="sum"))],
                    [T("Project Time Report"),
                    False, aURL(f="time",
                                args="report",
                                vars=Storage(rows="project",
                                            cols="person_id",
                                            fact="hours",
                                            aggregate="sum"))],
                ]],
            ]
        }
    else:
        project_menu = {
            "menu": [
                [T("Projects"), False, aURL(f="project"),[
                    [T("List All Projects"), False, aURL(f="project")],
                ]],
            ],
        }

    # -------------------------------------------------------------------------
    org_menu = [T("Organizations"), False, aURL(c="org", f="organisation"), [
                    [T("New"), False, aURL(p="create", c="org", f="organisation",
                                           args="create")],
                    [T("List All"), False, aURL(c="org", f="organisation")],
                    [T("Search"), False, aURL(c="org", f="organisation",
                                              args="search")],
                    #[T("Import"), False, aURL(p="create", c="org", f="organisation",
                    #                          args="import")]
                ]]
    office_menu = [T("Offices"), False, aURL(c="org", f="office"), [
                    [T("New"), False, aURL(p="create", c="org", f="office",
                                           args="create")],
                    [T("List All"), False, aURL(c="org", f="office")],
                    [T("Search"), False, aURL(c="org", f="office",
                                              args="search")],
                    [T("Import"), False, aURL(p="create", c="org", f="office",
                                              args="import")]
                ]]

    hrm_menu = {
        "menu": [],

        # NOTE: session.s3.hrm.mode is set by menu pre-processor in controller
        #       so can't simply make an if/else here :/

        "condition1": lambda: session.s3.hrm.mode is not None,
        "conditional1": [
                [T("Profile"),
                 True, aURL(c="hrm",
                            f="person",
                            vars=dict(mode="personal"))
                ]],

        "condition2": lambda: (session.s3.hrm.mode is not None) and (session.s3.hrm.orgs or ADMIN in session.s3.roles),
        "conditional2": [[T("Human Resources"),
                          True, aURL(c="hrm",
                                     f="index")]],

        "condition3": lambda: session.s3.hrm.mode is None,
        "conditional3": [
            [T("Staff"), False, aURL(c="hrm",
                                     f="human_resource",
                                     vars=dict(group="staff")), [
                [T("New Staff Member"), False, aURL(p="create",
                                                    c="hrm",
                                                    f="human_resource",
                                                    args="create",
                                                    vars=dict(group="staff"))],
                [T("List All"), False, aURL(c="hrm",
                                            f="human_resource",
                                            vars=dict(group="staff"))],
                [T("Search"), False, aURL(c="hrm",
                                          f="human_resource",
                                          args="search",
                                          vars=dict(group="staff"))],
                [T("Report Expiring Contracts"), False, aURL(c="hrm",
                                                             f="human_resource",
                                                             vars=dict(group="staff",
                                                                       expiring=1))],
                [T("Import"), False, aURL(p="create",
                                          c="hrm",
                                          f="person",
                                          args=["import"],
                                          vars=dict(group="staff"))],
                #[T("Dashboard"), False, aURL(f="index")],
            ]],
            [T("Volunteers"), False, aURL(c="hrm",
                                          f="human_resource",
                                          vars=dict(group="volunteer")), [
                [T("New Volunteer"), False, aURL(p="create",
                                                 c="hrm",
                                                 f="human_resource",
                                                 args="create",
                                                 vars=dict(group="volunteer"))],
                [T("List All"), False, aURL(c="hrm",
                                            f="human_resource",
                                            vars=dict(group="volunteer"))],
                [T("Search"), False, aURL(c="hrm",
                                          f="human_resource",
                                          args="search",
                                          vars=dict(group="volunteer"))],
                [T("Import"), False, aURL(p="create",
                                          c="hrm",
                                          f="person",
                                          args=["import"],
                                          vars=dict(group="volunteer"))],
            ]],
            [T("Teams"), False, aURL(c="hrm",
                                     f="group"), [
                [T("New Team"), False, aURL(c="hrm",
                                            f="group",
                                            args="create")],
                [T("List All"), False, aURL(c="hrm",
                                            f="group")],
            ]],
            org_menu,
            office_menu,
            [T("Job Role Catalog"), False, aURL(c="hrm",
                                                f="job_role"), [
                [T("New Job Role"), False, aURL(c="hrm",
                                                f="job_role",
                                                args="create")],
                [T("List All"), False, aURL(c="hrm",
                                            f="job_role")],
            ]],
            #[T("Skill Catalog"), False, URL(c="hrm",
            #                                f="skill"), [
            #    [T("New Skill"), False, aURL(p="create",
            #                                 c="hrm",
            #                                 f="skill",
            #                                 args="create")],
            #    [T("List All"), False, aURL(f="skill")],
            #    #[T("Skill Provisions"), False, aURL(f="skill_provision")],
            #]],
            [T("Training Events"), False, URL(c="hrm",
                                              f="training_event"), [
                [T("New Training Event"), False, aURL(p="create",
                                                      c="hrm",
                                                      f="training_event",
                                                      args="create")],
                [T("List All"), False, aURL(c="hrm",
                                            f="training_event")],
                [T("Training Report"), False, aURL(c="hrm",
                                                   f="training",
                                                   args=["report"])],
                [T("Import Participant List"), False, aURL(p="create",
                                                           c="hrm",
                                                           f="training",
                                                           args=["import"])],
            ]],
            [T("Training Course Catalog"), False, URL(c="hrm",
                                                      f="course"), [
                [T("New Training Course"), False, aURL(p="create",
                                                       c="hrm",
                                                       f="course",
                                                       args="create")],
                [T("List All"), False, aURL(c="hrm",
                                            f="course")],
                #[T("Course Certificates"), False, aURL(c="hrm",
                #                                       f="course_certificate")],
            ]],
            # [T("Certificate Catalog"), False, URL(f="certificate"), [
                # [T("New Certificate"), False, aURL(p="create",
                                                   # f="certificate",
                                                   # args="create")],
                # [T("List All"), False, aURL(f="certificate")],
                # [T("Skill Equivalence"), False, aURL(f="certificate_skill")],
            # ]],
            # Add the "personal" section to the menu (right)
            [T("Personal Profile"), True, aURL(c="hrm",
                                               f="person",
                                               vars=dict(mode="personal"))]
        ],
    }

    # =========================================================================
    # Default Menu Configurations for Controllers
    # =========================================================================
    """
        Dict structure -
            Key - controller name
            Value - Dict
                - menu      : default menu options
                - on_admin  : extensions for ADMIN role
                - on_editor : extensions for EDITOR role
            @NOTE: subject to change depending on changes in S3Menu / requirements
    """
    s3_menu_dict = {

        # ASSET Controller
        # ---------------------------------------------------------------------
        "asset": {
            "menu": [
                #[T("Home"), False, aURL(c="asset", f="index")],
                [T("Assets"), False, aURL(c="asset", f="asset"),
                [
                    [T("New"), False, aURL(p="create", c="asset", f="asset",
                                           args="create")],
                    [T("List All"), False, aURL(c="asset", f="asset")],
                    [T("Search"), False, aURL(c="asset", f="asset",
                                              args="search")],
                    [T("Import"), False, aURL(p="create", c="asset", f="asset",
                                              args="import")],
                ]],
                [T("Items"), False, aURL(c="asset", f="item"),
                [
                    [T("New"), False, aURL(p="create", c="asset", f="item",
                                           args="create")],
                    [T("List All"), False, aURL(c="asset", f="item")],
                ]],
            ]
        },

        # CR / Shelter Registry Controller
        # ---------------------------------------------------------------------
        "cr": {
            "menu": [
                [ # @ToDo - Fix s3.crud_strings["cr_shelter"].subtitle_list
                T("Camps") if deployment_settings.get_ui_camp() else T("Shelters"), False, aURL(f="shelter"), [
                    [T("New"), False, aURL(p="create", f="shelter", args="create")],
                    [T("List All"), False, aURL(f="shelter")],
                    # @ToDo Search by type, services, location, available space
                    #[T("Search"), False, URL(f="shelter", args="search")],
                ]],
            ],

            "on_editor": [
                [
                    T("Camp Types and Services") if deployment_settings.get_ui_camp() \
                    else T("Shelter Types and Services"),
                    False, URL(f="#"),
                    [
                        [T("List / Add Services"), False, URL(f="shelter_service")],
                        [T("List / Add Types"), False, URL(f="shelter_type")],

                    ]
                ],
            ]
        },

        # DOC / Document Library
        # ---------------------------------------------------------------------
        "doc": {
            "menu": [
                [T("Documents"), False, aURL(f="document"),[
                    [T("New"), False, aURL(p="create", f="document",
                                           args="create")],
                    [T("List All"), False, aURL(f="document")],
                    #[T("Search"), False, aURL(f="ireport", args="search")]
                ]],
                [T("Photos"), False, aURL(f="image"),[
                    [T("New"), False, aURL(p="create", f="image",
                                           args="create")],
                    [T("List All"), False, aURL(f="image")],
                    #[T("Bulk Uploader"), False, aURL(f="bulk_upload")]
                    #[T("Search"), False, aURL(f="ireport", args="search")]
                ]]],
        },

        # EVENT / Event Module
        # ---------------------------------------------------------------------
        "event": {
            "menu": [
                        [T("Scenarios"), False, aURL(c="scenario", f="scenario"), [
                            [T("New Scenario"), False, aURL(p="create", c="scenario",
                                                            f="scenario",
                                                            args="create")],
                            [T("View All"), False, aURL(c="scenario", f="scenario")]
                        ]],
                        [T("Events"), False, aURL(c="event", f="event"), [
                            [T("New Event"), False, aURL(p="create", c="event", f="event",
                                                         args="create")],
                            [T("View All"), False, aURL(c="event", f="event")]
                        ]],
                    ]   \
                    if deployment_settings.has_module("scenario") else \
                    [
                        [T("Events"), False, aURL(c="event", f="event"), [
                            [T("New Event"), False, aURL(p="create", c="event", f="event",
                                                         args="create")],
                            [T("View All"), False, aURL(c="event", f="event")]
                        ]]
                    ],
        },

        # GIS / GIS Controllers
        # ---------------------------------------------------------------------
        "gis": {
            "menu": [
                #[T("Locations"), False, aURL(f="location"), [
                #    [T("New Location"), False, aURL(p="create", f="location",
                #                                    args="create")],
                #    [T("New Location Group"), False, aURL(p="create", f="location",
                #                                          args="create",
                #                                          vars={"group": 1})],
                #    [T("List All"), False, aURL(f="location")],
                #    [T("Search"), False, aURL(f="location", args="search")],
                #    [T("Import"), False, aURL(f="location", args="import")],
                #    #[T("Geocode"), False, aURL(f="geocode_manual")],
                #]],
                #[T("Fullscreen Map"), False, aURL(f="map_viewing_client")],
                ## Currently not got geocoding support
                ##[T("Bulk Uploader"), False, aURL(c="doc", f="bulk_upload")]
            ],

            #"condition1": lambda: not deployment_settings.get_security_map() or s3_has_role(MAP_ADMIN),
            #"conditional1": [[T("Service Catalogue"), False, URL(f="map_service_catalogue")]]
        },

        # HMS / Hospital Status Assessment and Request Management System
        # ---------------------------------------------------------------------
        "hms": {
            "menu": [
                [T("Hospitals"), False, aURL(f="hospital", args="search"), [
                    [T("New"), False, aURL(p="create", f="hospital",
                                           args="create")],
                    [T("Search"), False, aURL(f="hospital", args="search")],
                    [T("List All"), False, aURL(f="hospital")],
                    #["----", False, None],
                    #[T("Show Map"), False, URL(c="gis", f="map_viewing_client",
                                               #vars={"kml_feed" : "%s/hms/hospital.kml" %
                                                    #s3.base_url,
                                                    #"kml_name" : "Hospitals_"})],
                ]],
                [T("Help"), False, URL(f="index")]
            ],
        },

        # HRM
        # ---------------------------------------------------------------------
        "hrm": hrm_menu,

        # INV / Inventory
        # ---------------------------------------------------------------------
        "inv": {
            "menu": [
                    #[T("Home"), False, aURL(c="inv", f="index")],
                    [T("Warehouses"), False, aURL(c="inv", f="warehouse"), [
                        [T("New"), False, aURL(p="create", c="inv",
                                               f="warehouse",
                                               args="create")],
                        [T("List All"), False, aURL(c="inv", f="warehouse")],
                        [T("Search"), False, aURL(c="inv", f="warehouse",
                                                  args="search")],
                        [T("Import"), False, aURL(p="create", c="inv",
                                                  f="warehouse",
                                                  args=["import"])],
                    ]],
                    [T("Warehouse Stock"), False, aURL(c="inv", f="warehouse"), [
                        [T("Search Warehouse Stock"), False, aURL(c="inv",
                                                                  f="inv_item",
                                                                  args="search")],
                        [T("Report"), False, aURL(p="create", c="inv", f="inv_item",
                                                  args=["report"])],
                        [T("Import"), False, aURL(p="create", c="inv", f="inv_item",
                                                  args=["import"])],
                    ]],
                    [s3.crud_strings.inv_recv.subtitle_list, False, aURL(c="inv", f="recv"), [
                        [T("New"), False, aURL(p="create", c="inv",
                                               f="recv",
                                               args="create")],
                        [T("List All"), False, aURL(c="inv", f="recv")],
                        [s3.crud_strings.inv_recv.title_search, False, aURL(c="inv",
                                                                            f="recv",
                                                                            args="search")],
                    ]],
                    [T("Sent Shipments"), False, aURL(c="inv", f="send"), [
                        [T("New"), False, aURL(p="create", c="inv",
                                               f="send",
                                               args="create")],
                        [T("List All"), False, aURL(c="inv", f="send")],
                    ]],
                    [T("Items"), False, aURL(c="supply", f="item"), [
                        [T("New"), False, aURL(p="create", c="supply",
                                               f="item",
                                               args="create")],
                        [T("List All"), False, aURL(c="supply", f="item")],
                        [T("Search"), False, aURL(c="supply", f="catalog_item",
                                                  args="search")],
                    ]],

                    # Catalog Items moved to be next to the Item Categories
                    #[T("Catalog Items"), False, aURL(c="supply", f="catalog_item"), [
                    #    [T("New"), False, aURL(p="create", c="supply", f="catalog_item",
                    #                          args="create")],
                    #    [T("List All"), False, aURL(c="supply", f="catalog_item")],
                    #    [T("Search"), False, aURL(c="supply", f="catalog_item",
                    #                             args="search")],
                    ##]],
                    #
                    [T("Catalogs"), False, aURL(c="supply", f="catalog"), [
                        [T("New"), False, aURL(p="create", c="supply",
                                               f="catalog",
                                               args="create")],
                        [T("List All"), False, aURL(c="supply", f="catalog")],
                        #[T("Search"), False, aURL(c="supply", f="catalog",
                        #                         args="search")],
                    ]]
                ],

            "on_admin": [[T("Item Categories"), False, aURL(c="supply", f="item_category"), [
                    [T("New Item Category"), False, aURL(p="create",
                                                         c="supply",
                                                         f="item_category",
                                                         args="create")],
                    [T("List All"), False, aURL(c="supply", f="item_category")]
                ]]]
        },

        # IRS / Incident Report System
        # ---------------------------------------------------------------------
        "irs": {
            "menu": [
                [T("Events"), False, aURL(f="ireport"),[
                    [T("New"), False, aURL(p="create", f="ireport", args="create")],
                    [T("List All"), False, aURL(f="ireport")],
                    [T("Timeline"), False, aURL(f="ireport", args="timeline")],
                    #[T("Search"), False, aURL(f="ireport", args="search")]
                ]],
            ],

            "on_admin": [[T("Event Categories"), False, aURL(f="icategory"),[
                    [T("New"), False, aURL(p="create", f="icategory", args="create")],
                    [T("List All"), False, aURL(f="icategory")],
                ]],
                #["Ushahidi " + T("Import"), False, aURL(f="ireport", args="ushahidi")]
            ]
        },

        # SURVEY / Survey Controller
        # ---------------------------------------------------------------------
        "survey": {
            "menu": [
                [T("Assessment Templates"), False, aURL(f="template"), [
                    #[T("New"), False, aURL(p="create", f="template", args="create")],
                    [T("List All"), False, aURL(f="template")],
                ]],
                #[T("Section"), False, aURL(f="section"), [
                #    [T("New"), False, aURL(p="create", f="section", args="create")],
                #    [T("List All"), False, aURL(f="section")]]],
                [T("Event Assessments"), False, aURL(f="series"), [
                    [T("New"), False, aURL(p="create", f="series", args="create")],
                    [T("List All"), False, aURL(f="series")],
                ]],
                ],
            "on_admin": [
                [T("Administration"), False, aURL(f="complete"), [
                    #[T("New"), False, aURL(p="create", f="complete", args="create")],
                    #[T("List All"), False, aURL(f="complete")],
                    [T("Import Templates"),
                     False,
                     aURL(f="question_list",
                          args="import"
                         )
                    ],
                    [T("Import Template Layout"),
                     False,
                     aURL(f="formatter",
                          args="import"
                         )
                    ],
                    [T("Import Completed Responses"),
                     False,
                     aURL(f="complete",
                          args="import"
                         )
                    ]
                ]],
                ]
        },

        # MSG / Messaging Controller
        # ---------------------------------------------------------------------
        "msg": {
            "menu": [
                [T("Compose"), False, URL(c="msg", f="compose")],
                [T("Distribution groups"), False, aURL(f="group"), [
                    [T("List/Add"), False, aURL(f="group")],
                    [T("Group Memberships"), False, aURL(f="group_membership")],
                ]],
                [T("Log"), False, aURL(f="log")],
                [T("Outbox"), False, aURL(f="outbox")],
                #[T("Search Twitter Tags"), False, aURL(f="twitter_search"),[
                #    [T("Queries"), False, aURL(f="twitter_search")],
                #    [T("Results"), False, aURL(f="twitter_search_results")]
                #]],
                #["CAP", False, aURL(f="tbc")]
            ],

            "on_admin": [
                [T("Administration"), False, URL(f="#"), admin_menu_messaging],
            ]
        },

        # ORG / Organization Registry
        # ---------------------------------------------------------------------
        "org": hrm_menu,

        # PATIENT / Patient Tracking Module
        # ---------------------------------------------------------------------
        "patient": {
            "menu": [
                    [T("Patients"), False, URL(f="patient"), [
                        [T("New"), False, aURL(p="create", f="patient",
                                               args="create")],
                        [T("List All"), False, aURL(f="patient")],
                        [T("Search"), False, aURL(f="patient",
                                                  args="search")]
                    ]]],
        },

        # PR / VITA Person Registry
        # ---------------------------------------------------------------------
        "pr": {
            "menu": pr_menu
        },

        # PROC / Procurement
        # ---------------------------------------------------------------------
        "proc": {
            "menu": [
                [T("Home"), False, aURL(f="index")],
                [T("Procurement Plans"), False, aURL(f="plan"),[
                    [T("New"), False, aURL(p="create", f="plan", args="create")],
                    [T("List All"), False, aURL(f="plan")],
                    #[T("Search"), False, aURL(f="plan", args="search")]
                ]],
                [T("Suppliers"), False, aURL(f="supplier"),[
                    [T("New"), False, aURL(p="create", f="supplier", args="create")],
                    [T("List All"), False, aURL(f="supplier")],
                    #[T("Search"), False, aURL(f="supplier", args="search")]
                ]],
            ],

        },

        # PROJECT / Project Tracking & Management
        # ---------------------------------------------------------------------
        "project": project_menu,

        # REQ / Request Management
        # ---------------------------------------------------------------------
        "req": {
            "menu": [[T("Requests"), False, aURL(c="req", f="req"), [
                        [T("New"), False, aURL(p="create", c="req", f="req",
                                               args="create")],
                        [T("List All"), False, aURL(c="req", f="req")],
                        [T("List All Requested Items"), False, aURL(c="req", f="req_item")],
                        [T("List All Requested Skills"), False, aURL(c="req", f="req_skill")],
                        #[T("Search Requested Items"), False, aURL(c="req",
                        #                                          f="req_item",
                        #                                          args="search")],
                    ]],
                    [T("Commitments"), False, aURL(c="req", f="commit"), [
                        [T("List All"), False, aURL(c="req", f="commit")]
                    ]],
                ]
        },

        # SYNC
        # ---------------------------------------------------------------------
        "sync": {
            "menu": admin_menu_options
        },

        # VEHICLE
        # ---------------------------------------------------------------------
        "vehicle": {
            "menu": [
                #[T("Home"), False, aURL(c="vehicle", f="index")],
                [T("Vehicles"), False, aURL(c="vehicle", f="vehicle"),
                [
                    [T("New"), False, aURL(p="create", c="vehicle", f="vehicle",
                                           args="create")],
                    [T("List All"), False, aURL(c="vehicle", f="vehicle")],
                    [T("Search"), False, aURL(c="vehicle", f="vehicle",
                                              args="search")],
                ]],
            ]
        },

        # ADMIN
        # ---------------------------------------------------------------------
        "admin": {
            "menu": admin_menu_options
        },
        "appadmin": {
            "menu": admin_menu_options
        },

        "default": {
            "menu": [
                [T("Site"), False, aURL(c="default"),
                [
                    [T("Sign in"), True, aURL(c="default", f="user", args="login")],
                ]
            ]]
        }

    }

    # Duplicate menus - some controllers might re-use menu defined in certain models Eg. inv, supply
    s3_menu_dict["supply"] = s3_menu_dict["inv"]
    s3_menu_dict["scenario"] = s3_menu_dict["event"]

    # =========================================================================
    # Breadcrumbs
    # =========================================================================
    def get_menu_label_and_state(menu_dict, # yikes
                                 controller,
                                 function,
                                 args = None,
                                 vars = None
                                ):
        """ Support Breadcrumbs """

        # Look at the menu for this Controller
        menu_spec = menu_dict[controller]["menu"]
        if not menu_spec:
            try:
                # e.g. HRM
                menu_spec = menu_dict[controller]["conditional1"]
            except KeyError:
                # e.g. GIS
                pass
        # Go through each entry in turn to find a match
        # Main menu
        for menu_item in menu_spec:
            (label, active, url) = menu_item[:3]
            if url:
                url_parts = url.split("/")[1:]
                # Check we're in the correct function
                url_app, url_controller, url_function = url_parts[:3]
                if vars:
                    _url_args = url_parts[3:]
                    if _url_args:
                        url_args, url_vars = _url_args[len(_url_args) - 1].split("?")
                    elif "?" in url_function:
                        url_function, url_vars = url_function.split("?")
                        url_args = None
                    else:
                        url_vars = None
                        url_args = None
                elif args:
                    url_args = url_parts[3:]
                    url_vars = None
                else:
                    url_args = None
                    url_vars = None

                if url_function == function:
                    if not args or url_args == args:
                        if not vars or url_vars == vars:
                            # We found the correct menu entry
                            return label, active
            # Try the submenus
            try:
                submenus = menu_item[3]
            except IndexError:
                # No Submenus defined for this main menu
                pass
            else:
                for submenu_item in submenus:
                    if submenu_item:
                        (sub_label, sub_active, sub_url) = submenu_item[:3]
                        if sub_url:
                            sub_url_parts = sub_url.split("/")[1:]
                            # Check we're in the correct function
                            sub_url_app, sub_url_con, sub_url_func = sub_url_parts[:3]
                            if vars:
                                _sub_url_args = sub_url_parts[3:]
                                if _sub_url_args and "?" in _sub_url_args:
                                    sub_url_args, sub_url_vars = _sub_url_args[len(_sub_url_args) - 1].split("?")
                                elif "?" in sub_url_func:
                                    sub_url_func, sub_url_vars = sub_url_func.split("?")
                                    sub_url_args = None
                                else:
                                    sub_url_vars = None
                                    sub_url_args = None
                            elif args:
                                sub_url_args = sub_url_parts[3:]
                                sub_url_vars = None
                            else:
                                sub_url_args = None
                                sub_url_vars = None
                            if sub_url_func == function:
                                if not args or sub_url_args == args:
                                    if not vars or sub_url_vars == vars:
                                        # We found the correct menu entry
                                        return sub_label, sub_active

        return ("", False)

    # -------------------------------------------------------------------------
    def define_breadcrumbs():
        breadcrumbs = [(deployment_settings.modules["default"].name_nice, True,
                        "/%s" % request.application)]
        if request.controller != "default":
            try:
                controllerLabel = deployment_settings.modules[request.controller].name_nice
            except KeyError:
                controllerLabel = "."
            breadcrumbs.append(
                (controllerLabel,
                 True,
                 "/%s/%s" % (request.application, request.controller)
                )
            )
        if request.function != "index":
            breadcrumbs.append(
                (get_menu_label_and_state(s3_menu_dict,
                                          request.controller,
                                          request.function) + \
                 (URL(c=request.controller,
                      f=request.function),)
                )
            )
        if request.args(0):
            try:
                # Ignore this argument if it's the ID of a record
                int(request.args[0])
            except ValueError:
                breadcrumbs.append(
                    (get_menu_label_and_state(s3_menu_dict,
                                              request.controller,
                                              request.function,
                                              request.args,
                                              request.vars) + \
                     (URL(c=request.controller,
                          f=request.function,
                          args = request.args),)
                    )
                )
        return breadcrumbs

    breadcrumbs = define_breadcrumbs()

else:
    s3_menu = lambda *args, **vars: None
    s3.menu_lang = []
    s3.menu_help = []
    s3.menu_auth = []
    s3.menu_modules = []
    response.menu = []
    breadcrumbs = []

# END =========================================================================
