# -*- coding: utf-8 -*-

# Populate default roles and permissions

# Set deployment_settings.base.prepopulate to 0 in Production
# (to save 1x DAL hit every page).
pop_list = deployment_settings.get_base_prepopulate()
if pop_list == 0:
    pop_list = []
else:
    table = db[auth.settings.table_group_name]
    # The query used here takes 2/3 the time of .count().
    if db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        pop_list = []
    if not isinstance(pop_list, (list, tuple)):
        pop_list = [pop_list]
# Add core roles as long as at least one populate setting is on
if len(pop_list) > 0:

    import csv
    def import_role(filename, extraVars=None):
        def parseACL(_acl):
            permissions = _acl.split("|")
            aclValue = 0
            for permission in permissions:
                if permission == "READ":
                    aclValue = aclValue | acl.READ
                if permission == "CREATE":
                    aclValue = aclValue | acl.CREATE
                if permission == "UPDATE":
                    aclValue = aclValue | acl.UPDATE
                if permission == "DELETE":
                    aclValue = aclValue | acl.DELETE
                if permission == "ALL":
                    aclValue = aclValue | acl.ALL
            return aclValue

        # Check if the source file is accessible
        try:
            openFile = open(filename, "r")
        except IOError:
            return "Unable to open file %s" % csv
        acl = auth.permission
        reader = csv.DictReader(openFile)
        roles = {}
        acls = {}
        args = {}
        for row in reader:
            if row != None:
                role = row["role"]
                if "description" in row:
                    desc = row["description"]
                else:
                    desc = ""
                rules = {}
                extra_param = {}
                if "controller" in row and row["controller"]:
                    rules["c"] = row["controller"]
                if "function" in row and row["function"]:
                    rules["f"] = row["function"]
                if "table" in row and row["table"]:
                    rules["t"] = row["table"]
                if row["oacl"]:
                    rules["oacl"] = parseACL(row["oacl"])
                if row["uacl"]:
                    rules["uacl"] = parseACL(row["uacl"])
                if "org" in row and row["org"]:
                    rules["organisation"] = row["org"]
                if "facility" in row and row["facility"]:
                    rules["facility"] = row["facility"]
                if "hidden" in row and row["hidden"]:
                    extra_param["hidden"] = row["hidden"]
                if "system" in row and row["system"]:
                    extra_param["system"] = row["system"]
                if "protected" in row and row["protected"]:
                    extra_param["protected"] = row["protected"]
                if "uid" in row and row["uid"]:
                    extra_param["uid"] = row["uid"]
            if role in roles:
                acls[role].append(rules)
            else:
                roles[role] = [role,desc]
                acls[role] = [rules]
            if len(extra_param) > 0 and role not in args:
                args[role] = extra_param
        for rulelist in roles.values():
            if rulelist[0] in args:
                create_role(rulelist[0],
                            rulelist[1],
                            *acls[rulelist[0]],
                            **args[rulelist[0]])
            else:
                create_role(rulelist[0],
                            rulelist[1],
                            *acls[rulelist[0]])
    response.s3.import_role = import_role


    # Shortcuts
    acl = auth.permission
    sysroles = auth.S3_SYSTEM_ROLES
    create_role = auth.s3_create_role
    update_acls = auth.s3_update_acls

    default_uacl = deployment_settings.get_aaa_default_uacl()
    default_oacl = deployment_settings.get_aaa_default_oacl()

    # Do not remove or change order of these 5 definitions (System Roles):
    create_role("Administrator",
                "System Administrator - can access & make changes to any data",
                uid=sysroles.ADMIN,
                system=True, protected=True)
    authenticated = create_role("Authenticated",
                                "Authenticated - all logged-in users",
                                # Authenticated users can see the Map
                                dict(c="gis", uacl=acl.ALL, oacl=acl.ALL),
                                # Note the owning role for locations is set to Authenticated
                                # by default, so this controls the access that logged in
                                # users have. (In general, tables do not have a default
                                # owning role.)
                                dict(c="gis", f="location", uacl=acl.READ|acl.CREATE, oacl=acl.ALL),
                                # Authenticated users can only see/edit their own PR/HRM records
                                dict(c="pr", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                                dict(t="pr_person", uacl=acl.NONE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                                # But need to be able to add/edit addresses
                                dict(c="pr", f="person", uacl=acl.CREATE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                                dict(c="hrm", f="person", uacl=acl.CREATE, oacl=acl.READ|acl.CREATE|acl.UPDATE),
                                # Authenticated  users can see the Supply Catalogue
                                dict(c="supply", uacl=acl.READ, oacl=default_oacl),
                                uid=sysroles.AUTHENTICATED,
                                protected=True)
    # Authenticated users:
    # Have access to all Orgs, Hospitals, Shelters
    update_acls(authenticated,
                dict(c="org", uacl=acl.READ, oacl=default_oacl),
                # Since we specify a Table ACL for Anonymous, we also need 1 for Authenticated
                dict(t="org_organisation", uacl=acl.READ|acl.CREATE, oacl=default_oacl),
                #dict(c="hms", uacl=acl.READ|acl.CREATE, oacl=default_oacl),
                #dict(c="cr", uacl=acl.READ|acl.CREATE, oacl=default_oacl),
                )

    # If we don't have OrgAuth active, then Authenticated users:
    # Have access to all Orgs, Sites & the Inventory & Requests thereof
    update_acls(authenticated,
                # Should every user be able to see their Org's Assets?
                #dict(c="asset", uacl=acl.READ, oacl=default_oacl),
                # Should every user be able to see their Org's Projects?
                #dict(c="project", uacl=acl.READ, oacl=default_oacl),
                #dict(c="inv", uacl=acl.READ, oacl=default_oacl),
                #dict(c="req", uacl=acl.READ|acl.CREATE|acl.UPDATE, oacl=default_oacl),
                # Allow authenticated users to view the Certificate Catalog
                dict(t="hrm_certificate", uacl=acl.READ),
                # HRM access is controlled to just HR Staff, except for:
                # Access to your own record & to be able to search for Skills
                # requires security policy 4+
                dict(c="hrm", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                dict(c="hrm", f="staff", uacl=acl.NONE, oacl=acl.NONE),
                dict(c="hrm", f="volunteer", uacl=acl.NONE, oacl=acl.NONE),
                dict(c="hrm", f="person", uacl=acl.NONE, oacl=acl.READ|acl.UPDATE),
                dict(c="hrm", f="skill", uacl=acl.READ, oacl=acl.READ),
                )

    create_role("Anonymous",
                "Unauthenticated users",

                # Defaults for Trunk
                #dict(c="org", uacl=acl.READ, oacl=default_oacl),
                #dict(c="project", uacl=acl.READ, oacl=default_oacl),
                #dict(c="cr", uacl=acl.READ, oacl=default_oacl),
                #dict(c="hms", uacl=acl.READ, oacl=default_oacl),
                #dict(c="inv", uacl=acl.READ, oacl=default_oacl),
                #dict(c="supply", uacl=acl.READ, oacl=default_oacl),
                #dict(c="delphi", uacl=acl.READ, oacl=default_oacl),

                # Allow unauthenticated users to view the list of organisations
                # so they can select an organisation when registering
                dict(t="org_organisation", uacl=acl.READ, organisation="all"),
                # Allow unauthenticated users to view the Map
                #dict(c="gis", uacl=acl.READ, oacl=default_oacl),
                # Allow unauthenticated users to cache Map feeds
                #dict(c="gis", f="cache_feed", uacl=acl.ALL, oacl=default_oacl),
                # Allow unauthenticated users to view feature queries
                #dict(c="gis", f="feature_query", uacl=acl.NONE, oacl=default_oacl),
                uid=sysroles.ANONYMOUS,
                protected=True)

    # Primarily for Security Policy 2
    create_role("Editor",
                "Editor - can access & make changes to any unprotected data",
                uid=sysroles.EDITOR,
                system=True, protected=True)
    # MapAdmin
    create_role("MapAdmin",
                "MapAdmin - allowed access to edit the MapService Catalogue",
                dict(c="gis", uacl=acl.ALL, oacl=acl.ALL),
                dict(c="gis", f="location", uacl=acl.ALL, oacl=acl.ALL),
                uid=sysroles.MAP_ADMIN,
                system=True, protected=True)

    # Enable shortcuts (needed by default.py)
    auth.get_system_roles()
    system_roles = session.s3.system_roles
    ADMIN = system_roles.ADMIN
    AUTHENTICATED = system_roles.AUTHENTICATED
    ANONYMOUS = system_roles.ANONYMOUS
    EDITOR = system_roles.EDITOR
    MAP_ADMIN = system_roles.MAP_ADMIN

    # Roles that apply just to Orgs
    create_role("OrgAdmin",
                "Can see/edit all records belonging to this Organisation & all it's Facilities. Can also manage all the Access Permissions for this Organisation.",
                dict(c="org", uacl=acl.ALL),
                dict(c="org", f="office", uacl=acl.ALL),
                dict(c="org", f="organisation", uacl=acl.ALL),
                dict(c="hrm", uacl=acl.ALL),
                dict(c="hrm", f="human_resource", uacl=acl.ALL),
                dict(c="hrm", f="person", uacl=acl.ALL),
                dict(t="pr_person", uacl=acl.ALL),
                dict(c="hrm", f="job_role", uacl=acl.ALL),
                dict(c="hrm", f="skill", uacl=acl.ALL),
                dict(c="hrm", f="course", uacl=acl.ALL),
                dict(c="hrm", f="certificate", uacl=acl.ALL),
                dict(c="inv", uacl=acl.ALL),
                dict(c="inv", f="warehouse", uacl=acl.ALL),
                dict(c="inv", f="inv_item", uacl=acl.ALL),
                dict(c="inv", f="send", uacl=acl.ALL),
                dict(c="inv", f="recv", uacl=acl.ALL),
                dict(c="supply", f="item", uacl=acl.ALL),
                dict(c="supply", f="catalog_item", uacl=acl.ALL),
                dict(c="supply", f="item_category", uacl=acl.ALL)
                )
    # Roles that apply just to Facilities
    create_role("SiteAdmin",
                "Can see/edit all records belonging to this Facility. Can also manage all the Access Permissions for this Facility.",
                dict(c="org", f="office", uacl=acl.ALL),
                dict(c="hrm", uacl=acl.ALL),
                dict(c="hrm", f="human_resource", uacl=acl.ALL),
                dict(c="hrm", f="person", uacl=acl.ALL),
                dict(t="pr_person", uacl=acl.ALL),
                dict(c="hrm", f="job_role", uacl=acl.ALL),
                dict(c="hrm", f="skill", uacl=acl.ALL),
                dict(c="hrm", f="course", uacl=acl.ALL),
                dict(c="hrm", f="certificate", uacl=acl.ALL),
                dict(c="inv", uacl=acl.ALL),
                dict(c="inv", f="warehouse", uacl=acl.ALL),
                dict(c="inv", f="inv_item", uacl=acl.ALL),
                dict(c="inv", f="send", uacl=acl.ALL),
                dict(c="inv", f="recv", uacl=acl.ALL),
                dict(c="supply", f="item", uacl=acl.ALL),
                dict(c="supply", f="catalog_item", uacl=acl.ALL),
                dict(c="supply", f="item_category", uacl=acl.ALL)
                )
    # Roles that apply to both Orgs & Facilities
    create_role("HR Manager",
                "Can see/edit all HR records belonging to this Organisation & all it's Facilities. Can also manage all the Access Permissions to HR records for this Organisation.",
                dict(c="hrm", uacl=acl.ALL),
                dict(c="hrm", f="human_resource", uacl=acl.ALL),
                dict(c="hrm", f="person", uacl=acl.ALL),
                dict(t="pr_person", uacl=acl.ALL),
                dict(c="hrm", f="job_role", uacl=acl.ALL),
                dict(c="hrm", f="skill", uacl=acl.ALL),
                dict(c="hrm", f="course", uacl=acl.ALL),
                dict(c="hrm", f="training", uacl=acl.ALL),
                dict(c="hrm", f="certificate", uacl=acl.ALL),
                )
    create_role("HR Editor",
                "Can see/edit all HR records belonging to this Organisation & all it's Facilities. Cannot control access permissions.",
                dict(c="hrm", uacl=acl.ALL),
                dict(c="hrm", f="human_resource", uacl=acl.ALL),
                dict(c="hrm", f="person", uacl=acl.ALL),
                dict(t="pr_person", uacl=acl.ALL),
                dict(c="hrm", f="job_role", uacl=acl.ALL),
                dict(c="hrm", f="skill", uacl=acl.ALL),
                dict(c="hrm", f="course", uacl=acl.ALL),
                dict(c="hrm", f="training", uacl=acl.ALL),
                dict(c="hrm", f="certificate", uacl=acl.ALL),
                )
    create_role("HR Reader",
                "Can see all HR records belonging to this Organisation & all it's Facilities. Cannot edit any records or control access permissions.",
                dict(c="hrm", uacl=acl.READ),
                dict(c="hrm", f="human_resource", uacl=acl.READ),
                dict(c="hrm", f="person", uacl=acl.READ),
                dict(t="pr_person", uacl=acl.READ),
                dict(c="hrm", f="job_role", uacl=acl.READ),
                dict(c="hrm", f="skill", uacl=acl.READ),
                dict(c="hrm", f="course", uacl=acl.READ),
                dict(c="hrm", f="training", uacl=acl.READ),
                dict(c="hrm", f="certificate", uacl=acl.READ),
                )
    create_role("Logs Manager",
                "Can see/edit all Logistics records belonging to this Organisation & all it's Facilities. Can also manage all the Access Permissions to Logistics records for this Organisation.",
                dict(c="inv", uacl=acl.ALL),
                dict(c="inv", f="warehouse", uacl=acl.ALL),
                dict(c="inv", f="inv_item", uacl=acl.ALL),
                dict(c="inv", f="send", uacl=acl.ALL),
                dict(c="inv", f="recv", uacl=acl.ALL),
                dict(c="supply", f="item", uacl=acl.ALL),
                dict(c="supply", f="catalog_item", uacl=acl.ALL),
                dict(c="supply", f="item_category", uacl=acl.ALL),
                )
    create_role("Logs Editor",
                "Can see/edit all Logistics records belonging to this Organisation & all it's Facilities. Cannot control access permissions.",
                dict(c="inv", uacl=acl.ALL),
                dict(c="inv", f="warehouse", uacl=acl.ALL),
                dict(c="inv", f="inv_item", uacl=acl.ALL),
                dict(c="inv", f="send", uacl=acl.ALL),
                dict(c="inv", f="recv", uacl=acl.ALL),
                # Logs Editors can create new Items
                dict(c="supply", f="item", uacl=acl.ALL),
                # But not Edit the Catalogs or the Categories
                dict(c="supply", f="catalog_item", uacl=acl.READ|acl.CREATE, oacl=acl.READ),
                dict(c="supply", f="item_category", uacl=acl.READ|acl.CREATE, oacl=acl.READ),
                )
    create_role("Logs Reader",
                "Can see all Logistics records belonging to this Organisation & all it's Facilities. Cannot edit any records or control access permissions.",
                dict(c="inv", uacl=acl.READ, oacl=acl.READ),
                dict(c="inv", f="warehouse", uacl=acl.READ),
                dict(c="inv", f="inv_item", uacl=acl.READ),
                dict(c="inv", f="send", uacl=acl.READ),
                dict(c="inv", f="recv", uacl=acl.READ),
                dict(c="supply", f="item", uacl=acl.READ),
                dict(c="supply", f="catalog_item", uacl=acl.READ),
                dict(c="supply", f="item_category", uacl=acl.READ),
                )
    create_role("Assets Editor",
                "Can see/edit all Asset records belonging to this Organisation & all it's Facilities. Cannot control access permissions.",
                dict(c="asset", uacl=acl.ALL),
                )
    create_role("Assets Reader",
                "Can see all Asset records belonging to this Organisation & all it's Facilities. Cannot edit any records or control access permissions.",
                dict(c="asset", uacl=acl.READ, oacl=acl.READ),
                )
    create_role("Projects Editor",
                "Can see/edit all Project records belonging to this Organisation & all it's Facilities. Cannot control access permissions.",
                dict(c="project", uacl=acl.ALL),
                )
    create_role("Projects Reader",
                "Can see all Project records belonging to this Organisation & all it's Facilities. Cannot edit any records or control access permissions.",
                dict(c="poject", uacl=acl.READ, oacl=acl.READ),
                )
# END =========================================================================
