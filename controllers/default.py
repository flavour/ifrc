# -*- coding: utf-8 -*-

"""
    Default Controllers
"""

module = "default"

# -----------------------------------------------------------------------------
def call():
    "Call an XMLRPC, JSONRPC or RSS service"
    # If webservices don't use sessions, avoid cluttering up the storage
    #session.forget()
    return service()

# -----------------------------------------------------------------------------
def download():
    """ Download a file """

    # Load the Model
    tablename = request.args[0].split(".", 1)[0]
    s3mgr.load(tablename)

    return response.download(request, db)

# =============================================================================
def register_validation(form):
    """ Validate the fields in registration form """
    # Mobile Phone
    if "mobile" in form.vars and form.vars.mobile:
        regex = re.compile(single_phone_number_pattern)
        if not regex.match(form.vars.mobile):
            form.errors.mobile = T("Invalid phone number")
    elif deployment_settings.get_auth_registration_mobile_phone_mandatory():
        form.errors.mobile = T("Phone number is required")
    return

# -----------------------------------------------------------------------------
def register_onaccept(form):
    """ Tasks to be performed after a new user registers """
    # Add newly-registered users to Person Registry, add 'Authenticated' role
    # If Organisation is provided, then: add HRM record & add to 'Org_X_Access' role
    person = auth.s3_register(form)

    if deployment_settings.has_module("delphi"):
        # Add user as a participant of the default problem group
        utable = auth.settings.table_user
        ptable = s3db.pr_person
        ltable = s3db.pr_person_user
        query = (ptable.id == person) & \
                (ptable.pe_id == ltable.pe_id) & \
                (ltable.user_id == utable.id)
        user_id = db(query).select(utable.id, limitby=(0, 1)).first().id
        table = s3db.delphi_group
        query = (table.deleted != True)
        group = db(query).select(table.id,
                                 limitby=(0, 1)).first()
        if group:
            table = s3db.delphi_membership
            table.insert(group_id=group.id,
                         user_id=user_id,
                         status=3)

# -----------------------------------------------------------------------------
auth.settings.register_onvalidation = register_validation
auth.settings.register_onaccept = register_onaccept

_table_user = auth.settings.table_user
_table_user.first_name.label = T("First Name")
_table_user.first_name.comment = SPAN("*", _class="req")
_table_user.last_name.label = T("Last Name")
if deployment_settings.get_L10n_mandatory_lastname():
    _table_user.last_name.comment = SPAN("*", _class="req")
_table_user.email.label = T("E-mail")
_table_user.email.comment = SPAN("*", _class="req")
_table_user.password.comment = SPAN("*", _class="req")
_table_user.language.label = T("Language")
_table_user.language.comment = DIV(_class="tooltip",
                                   _title="%s|%s" % (T("Language"),
                                                     T("The language you wish the site to be displayed in.")))
_table_user.language.represent = lambda opt: s3_languages.get(opt, UNKNOWN_OPT)

# Photo widget
if not deployment_settings.get_auth_registration_requests_image():
    _table_user.image.readable = _table_user.image.writable = False
else:
    _table_user.image.comment = DIV(_class="stickytip",
                                     _title="%s|%s" % (T("Image"),
                                                       T("You can either use %(gravatar)s or else upload a picture here. The picture will be resized to 50x50.") % \
                                                        dict(gravatar = A("Gravatar",
                                                                          _target="top",
                                                                          _href="http://gravatar.com"))))

# Organisation widget for use in Registration Screen
# NB User Profile is only editable by Admin - using User Management
organisation_represent = s3db.org_organisation_represent
org_widget = IS_ONE_OF(db, "org_organisation.id",
                       organisation_represent,
                       orderby="org_organisation.name",
                       sort=True)
if deployment_settings.get_auth_registration_organisation_mandatory():
    _table_user.organisation_id.requires = org_widget
else:
    _table_user.organisation_id.requires = IS_NULL_OR(org_widget)

# For the User Profile:
_table_user.utc_offset.comment = DIV(_class="tooltip",
                                     _title="%s|%s" % (auth.messages.label_utc_offset,
                                                       auth.messages.help_utc_offset))
_table_user.organisation_id.represent = organisation_represent
_table_user.organisation_id.comment = DIV(_class="tooltip",
                                          _title="%s|%s|%s" % (T("Organization"),
                                                               T("The default Organization for whom you are acting."),
                                                               T("This setting can only be controlled by the Administrator.")))

org_site_represent = s3db.org_site_represent
_table_user.site_id.represent = org_site_represent
_table_user.site_id.comment = DIV(_class="tooltip",
                                  _title="%s|%s|%s" % (T("Facility"),
                                                       T("The default Facility for which you are acting."),
                                                       T("This setting can only be controlled by the Administrator.")))

# =============================================================================
def index():
    """ Main Home Page """

    title = deployment_settings.get_system_name()
    response.title = title

    script = """
$('.marker').mouseover(function() {
    $(this).children('.marker-window').show();
})
$('.marker').mouseout(function() {
    $(this).children('.marker-window').hide();
})"""
    response.s3.jquery_ready.append(script)

    dashboard = UL(LI(A(H2("STAFF & VOLUNTEERS"),
                        P("Add new and manage existing human resources."),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_staff.png"]),
                            _alt="Staff and Volunteers"),
                      _href=URL(c="hrm", f="index"))),
                   LI(A(H2("WAREHOUSES"),
                        P("Stocks and relief items."),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_warehouse.png"]),
                            _alt="Warehouses"),
                      _href=URL(c="inv", f="index"))),
                   LI(A(H2("ASSETS"),
                        P("Manage office inventories and assets."),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_assets.png"]),
                            _alt="Assests"),
                      _href=URL(c="asset", f="index"))),
                   LI(A(H2("ASSESSMENTS"),
                        P(T("Design, deploy & analyze surveys.")),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_assessments.png"]),
                            _alt="Assessments"),
                      _href=URL(c="survey", f="index"))),
                   LI(A(H2("PROJECTS"),
                        P("Tracking and analysis of Projects and Activities."),
                        IMG(_src=URL(c="static", f="img",
                                     args=["ifrc", "graphic_tools.png"]),
                            _alt="Tools"),
                      _href=URL(c="project", f="index"))),
                   _id="dashboard")

    markers = [
        Storage(name = "Afghan Red Crescent Society",
                direction = "right",
                top = 104,
                left = 260),
        Storage(name = "Australian Red Cross",
                direction = "right",
                top = 334,
                left = 458),
        Storage(name = "Bangladesh Red Crescent Society",
                direction = "right",
                top = 136,
                left = 312),
        Storage(name = "Brunei Darussalam Red Crescent Society",
                direction = "right",
                top = 196,
                left = 385),
        Storage(name = "Cambodian Red Cross Society",
                direction = "right",
                top = 173,
                left = 358),
        Storage(name = "Cook Islands Red Cross",
                direction = "right",
                top = 279,
                left = 625),
        Storage(name = "Fiji Red Cross Society",
                direction = "right",
                top = 266,
                left = 565),
        Storage(name = "Hong Kong Red Cross Society",
                direction = "right",
                top = 140,
                left = 381),
        Storage(name = "Indian Red Cross Society",
                direction = "right",
                top = 124,
                left = 275),
        Storage(name = "Indonesian Red Cross Society",
                direction = "right",
                top = 225,
                left = 362),
        Storage(name = "Japanese Red Cross Society",
                direction = "right",
                top = 90,
                left = 444),
        Storage(name = "Kiribati Red Cross Society",
                direction = "left",
                top = 205,
                left = 540),
        Storage(name = "Lao Red Cross Society",
                direction = "right",
                top = 152,
                left = 351),
        Storage(name = "Malaysian Red Crescent Society",
                direction = "right",
                top = 198,
                left = 352),
        Storage(name = "Maldivian Red Crescent",
                direction = "right",
                top = 196,
                left = 266),
        Storage(name = "Marshall Islands Red Cross Society",
                direction = "left",
                top = 192,
                left = 537),
        Storage(name = "Micronesia Red Cross Society",
                direction = "left",
                top = 192,
                left = 510),
        Storage(name = "Mongolian Red Cross Society",
                direction = "right",
                top = 52,
                left = 356),
        Storage(name = "Myanmar Red Cross Society",
                direction = "right",
                top = 158,
                left = 334),
        Storage(name = "Nepal Red Cross Society",
                direction = "right",
                top = 127,
                left = 295),
        Storage(name = "New Zealand Red Cross",
                direction = "right",
                top = 353,
                left = 538),
        Storage(name = "Pakistan Red Crescent Society",
                direction = "right",
                top = 110,
                left = 266),
        Storage(name = "Palau Red Cross Society",
                direction = "right",
                top = 189,
                left = 444),
        Storage(name = "Papua New Guinea Red Cross Society",
                direction = "right",
                top = 237,
                left = 483),
        Storage(name = "Philippine National Red Cross",
                direction = "right",
                top = 163,
                left = 403),
        Storage(name = "Red Cross of Viet Nam",
                direction = "right",
                top = 144,
                left = 357),
        Storage(name = "Red Cross Society of China",
                direction = "right",
                top = 78,
                left = 382),
        Storage(name = "Red Cross Society of the Democratic People's Republic of Korea",
                direction = "right",
                top = 79,
                left = 405),
        Storage(name = "Republic of Korea National Red Cross",
                direction = "right",
                top = 83,
                left = 408),
        Storage(name = "Samoa Red Cross Society",
                direction = "left",
                top = 250,
                left = 595),
        Storage(name = "Singapore Red Cross Society",
                direction = "right",
                top = 205,
                left = 360),
        Storage(name = "Solomon Islands Red Cross",
                direction = "right",
                top = 237,
                left = 514),
        Storage(name = "Sri Lanka Red Cross Society",
                direction = "right",
                top = 189,
                left = 290),
        Storage(name = "Thai Red Cross Society",
                direction = "right",
                top = 165,
                left = 345),
        Storage(name = "Timor-Leste Red Cross Society",
                direction = "right",
                top = 235,
                left = 417),
        Storage(name = "Tonga Red Cross Society",
                direction = "right",
                top = 279,
                left = 539),
        Storage(name = "Tuvalu Red Cross Society",
                direction = "right",
                top = 235,
                left = 566),
        Storage(name = "Vanuatu Red Cross Society",
                direction = "right",
                top = 264,
                left = 536),
        ]

    map = DIV(A("Go to Functional Map",
                _href=URL(c="gis", f="index"),
                _class="map-click"),
              _id="map-home")

    for marker in markers:
        map.append(DIV(A(_href=URL(c="org", f="organisation", args="read",
                                   vars={"organisation.name": marker.name})),
                           DIV(SPAN(marker.name),
                               SPAN(_class="marker-plus"),
                               _class="marker-window %s" % marker.direction),
                           _class="marker",
                           _style="top:%ipx;left:%ipx;" % (marker.top,
                                                           marker.left)))
    map.append(DIV(SPAN("Click anywhere on the map for full functionality"),
                   _class="map-tip"))

    current.menu.breadcrumbs = None

    return dict(dashboard=dashboard,
                map=map)

# -----------------------------------------------------------------------------
def organisation():
    """
        Function to handle pagination for the org list on the homepage
    """

    table = db.org_organisation
    table.id.label = T("Organization")
    table.id.represent = organisation_represent

    response.s3.dataTable_sPaginationType = "two_button"
    response.s3.dataTable_sDom = "rtip" #"frtip" - filter broken
    response.s3.dataTable_iDisplayLength = 25

    s3mgr.configure("org_organisation",
                    listadd = False,
                    addbtn = True,
                    super_entity = db.pr_pentity,
                    linkto = "/%s/org/organisation/%s" % (request.application,
                                                          "%s"),
                    list_fields = ["id",])

    return s3_rest_controller("org", "organisation")
# -----------------------------------------------------------------------------
def site():
    """
        @todo: Avoid redirect
    """
    s3mgr.load("org_site")
    if len(request.args):
        site_id = request.args[0]
        site_r = db.org_site[site_id]
        tablename = site_r.instance_type
        table = s3db.table(tablename)
        if table:
            query = (table.site_id == site_id)
            id = db(query).select(db[tablename].id,
                                  limitby = (0, 1)).first().id
            cf = tablename.split("_", 1)
            redirect(URL(c = cf[0],
                         f = cf[1],
                         args = [id]))
    raise HTTP(404)

# -----------------------------------------------------------------------------
def message():
    #if "verify_email_sent" in request.args:
    title = T("Account Registered - Please Check Your Email")
    message = T( "%(system_name)s has sent an email to %(email)s to verify your email address.\nPlease check your email to verify this address. If you do not receive this email please check you junk email or spam filters." )\
                 % {"system_name": deployment_settings.get_system_name(),
                    "email": request.vars.email}
    image = "email_icon.png"
    return dict(title = title,
                message = message,
                image_src = "/%s/static/img/%s" % (request.application, image)
                )

# -----------------------------------------------------------------------------
def rapid():
    """ Set/remove rapid data entry flag """

    val = request.vars.get("val", True)
    if val == "0":
        val = False
    else:
        val = True
    session.s3.rapid_data_entry = val

    response.view = "xml.html"
    return dict(item=str(session.s3.rapid_data_entry))

# -----------------------------------------------------------------------------
def user_profile_onaccept(form):
    """ Update the UI locale from user profile """

    if form.vars.language:
        session.s3.language = form.vars.language
    return

# -----------------------------------------------------------------------------
def user():
    """ Auth functions based on arg. See gluon/tools.py """

    auth.settings.on_failed_authorization = URL(f="error")

    if request.args and request.args(0) == "login_next":
        # Can redirect the user to another page on first login for workflow (set in 00_settings.py)
        # Note the timestamp of last login through the browser
        if auth.is_logged_in():
            db(db.auth_user.id == auth.user.id).update(timestmp = request.utcnow)

    _table_user = auth.settings.table_user
    if request.args and request.args(0) == "profile":
        #_table_user.organisation.writable = False
        _table_user.utc_offset.readable = True
        _table_user.utc_offset.writable = True

    auth.settings.profile_onaccept = user_profile_onaccept

    login_form = register_form = None
    if request.args and request.args(0) == "login":
        auth.messages.submit_button = T("Login")
        form = auth()
        login_form = form
        if s3.crud.submit_style:
            form[0][-1][1][0]["_class"] = s3.crud.submit_style
    elif request.args and request.args(0) == "register":
        if deployment_settings.get_terms_of_service():
            auth.messages.submit_button = T("I accept. Create my account.")
        else:
            auth.messages.submit_button = T("Register")
        # Default the profile language to the one currently active
        _table_user.language.default = T.accepted_language
        form = auth()
        register_form = form
        # Add client-side validation
        s3_register_validation()
    else:
        form = auth()

    if request.args and request.args(0) == "profile" and \
       deployment_settings.get_auth_openid():
        form = DIV(form, openid_login_form.list_user_openids())

    self_registration = deployment_settings.get_security_self_registration()

    # Use Custom Ext views
    # Best to not use an Ext form for login: can't save username/password in browser & can't hit 'Enter' to submit!
    #if request.args(0) == "login":
    #    response.title = T("Login")
    #    response.view = "auth/login.html"

    return dict(form=form,
                login_form=login_form,
                register_form=register_form,
                self_registration=self_registration)

# -----------------------------------------------------------------------------
def source():
    """ RESTful CRUD controller """
    return s3_rest_controller("s3", "source")

# -----------------------------------------------------------------------------
# About Sahana
def apath(path=""):
    """ Application path """
    import os
    from gluon.fileutils import up
    opath = up(request.folder)
    #TODO: This path manipulation is very OS specific.
    while path[:3] == "../": opath, path=up(opath), path[3:]
    return os.path.join(opath,path).replace("\\", "/")

def about():
    """
        The About page provides details on the software dependencies and
        versions available to this instance of Sahana Eden.

        @ToDo: Avoid relying on Command Line tools which may not be in path
               - pull back info from Python modules instead?
    """
    import sys
    import subprocess
    import string
    python_version = sys.version
    web2py_version = open(apath("../VERSION"), "r").read()[8:]
    sahana_version = open(os.path.join(request.folder, "VERSION"), "r").read()
    # Database
    sqlite_version = None
    mysql_version = None
    mysqldb_version = None
    pgsql_version = None
    psycopg_version = None
    if db_string[0].find("sqlite") != -1:
        try:
            import sqlite3
            #sqlite_version = (subprocess.Popen(["sqlite3", "-version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()
            sqlite_version = sqlite3.version
        except:
            sqlite_version = T("Unknown")
    elif db_string[0].find("mysql") != -1:
        try:
            mysql_version = (subprocess.Popen(["mysql", "--version"], stdout=subprocess.PIPE).communicate()[0]).rstrip()[10:]
        except:
            mysql_version = T("Unknown")
        try:
            import MySQLdb
            mysqldb_version = MySQLdb.__revision__
        except:
            mysqldb_version = T("Not installed or incorrectly configured.")
    else:
        # Postgres
        try:
            pgsql_reply = (subprocess.Popen(["psql", "--version"], stdout=subprocess.PIPE).communicate()[0])
            pgsql_version = string.split(pgsql_reply)[2]
        except:
            pgsql_version = T("Unknown")
        try:
            import psycopg2
            psycopg_version = psycopg2.__version__
        except:
            psycopg_version = T("Not installed or incorrectly configured.")
    # Libraries
    try:
        import reportlab
        reportlab_version = reportlab.Version
    except:
        reportlab_version = T("Not installed or incorrectly configured.")
    try:
        import xlwt
        xlwt_version = xlwt.__VERSION__
    except:
        xlwt_version = T("Not installed or incorrectly configured.")
    return dict(
                python_version=python_version,
                sahana_version=sahana_version,
                web2py_version=web2py_version,
                sqlite_version=sqlite_version,
                mysql_version=mysql_version,
                mysqldb_version=mysqldb_version,
                pgsql_version=pgsql_version,
                psycopg_version=psycopg_version,
                reportlab_version=reportlab_version,
                xlwt_version=xlwt_version
                )

# -----------------------------------------------------------------------------
def help():
    """ Custom View """
    response.title = T("Help")
    return dict()

# -----------------------------------------------------------------------------
def privacy():
    """ Custom View """
    response.title = T("Privacy")
    return dict()

# -----------------------------------------------------------------------------
def contact():
    """
        Give the user options to contact the site admins.
        Either:
            An internal Support Requests database
        or:
            Custom View
    """
    if auth.is_logged_in() and deployment_settings.get_options_support_requests():
        # Provide an internal Support Requests ticketing system.
        prefix = "support"
        resourcename = "req"
        tablename = "%s_%s" % (prefix, resourcename)
        table = s3db[tablename]

        # Pre-processor
        def prep(r):
            if r.interactive:
                # Only Admins should be able to update ticket status
                status = table.status
                actions = table.actions
                if not auth.s3_has_role(ADMIN):
                    status.writable = False
                    actions.writable = False
                if r.method != "update":
                    status.readable = False
                    status.writable = False
                    actions.readable = False
                    actions.writable = False
            return True
        response.s3.prep = prep

        output = s3_rest_controller(prefix, resourcename)
        return output
    else:
        # Default: Simple Custom View
        response.title = T("Contact us")
        return dict()


# END =========================================================================
