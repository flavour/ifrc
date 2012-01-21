# -*- coding: utf-8 -*-

# 1st-run initialisation
# designed to be called from Crontab's @reboot
# however this isn't reliable (doesn't work on Win32 Service) so still in models for now...

# Deployments can change settings live via appadmin
if populate > 0:

    # Allow debug
    import sys

    # Load all Models to ensure all DB tables present
    s3db.load_all_models()

    # Add core data as long as at least one populate setting is on

    # Scheduled Tasks
    if deployment_settings.has_module("msg"):
        # Send Messages from Outbox
        # SMS every minute
        s3task.schedule_task("process_outbox",
                             vars={"contact_method":"SMS"},
                             period=60,  # seconds
                             timeout=60, # seconds
                             repeats=0   # unlimited
                            )
        # Emails every 5 minutes
        s3task.schedule_task("process_outbox",
                             vars={"contact_method":"EMAIL"},
                             period=300,  # seconds
                             timeout=300, # seconds
                             repeats=0    # unlimited
                            )

    # Person Registry
    tablename = "pr_person"
    table = db[tablename]
    # Should work for our 3 supported databases: sqlite, MySQL & PostgreSQL
    field = "first_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))
    field = "middle_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))
    field = "last_name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % (field, tablename, field))

    # Synchronisation
    table = db.sync_config
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
       table.insert()

    # Incident Reporting System
    if deployment_settings.has_module("irs"):
        # Categories visible to ends-users by default
        table = db.irs_icategory
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert(code = "flood")
            table.insert(code = "geophysical.landslide")
            table.insert(code = "roadway.bridgeClosure")
            table.insert(code = "roadway.roadwayClosure")
            table.insert(code = "other.buildingCollapsed")
            table.insert(code = "other.peopleTrapped")
            table.insert(code = "other.powerFailure")

    # Messaging Module
    if deployment_settings.has_module("msg"):
        table = db.msg_email_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert(
                inbound_mail_server = "imap.gmail.com",
                inbound_mail_type = "imap",
                inbound_mail_ssl = True,
                inbound_mail_port = 993,
                inbound_mail_username = "username",
                inbound_mail_password = "password",
                inbound_mail_delete = False,
                #outbound_mail_server = "mail:25",
                #outbound_mail_from = "demo@sahanafoundation.org",
            )
        # Need entries for the Settings/1/Update URLs to work
        table = db.msg_setting
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( outgoing_sms_handler = "WEB_API" )
        table = db.msg_modem_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( modem_baud = 115200 )
        table = db.msg_api_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( to_variable = "to" )
        table = db.msg_smtp_to_sms_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( address="changeme" )
        table = db.msg_tropo_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( token_messaging = "" )
        table = db.msg_twitter_settings
        if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
            table.insert( pin = "" )

    # GIS Module
    table = db.gis_marker
    # Can't do sub-folders :/
    # need a script to read in the list of default markers from the filesystem, copy/rename & populate the DB 1 by 1
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # We want to start at ID 1, but postgres won't let us truncate() & not needed anyway this is only run on 1st_run.
        #table.truncate()
        # "marker_red" is the default marker. If you remove it or change its
        # name, also change S3Config.get_gis_default_marker().
        marker_red = table.insert(
            name = "marker_red",
            height = 34,
            width = 20,
            image = "gis_marker.image.marker_red.png"
        )
        marker_yellow = table.insert(
            name = "marker_yellow",
            height = 34,
            width = 20,
            image = "gis_marker.image.marker_yellow.png"
        )
        marker_amber = table.insert(
            name = "marker_amber",
            height = 34,
            width = 20,
            image = "gis_marker.image.marker_amber.png"
        )
        marker_green = table.insert(
            name = "marker_green",
            height = 34,
            width = 20,
            image = "gis_marker.image.marker_green.png"
        )
        assessment = table.insert(
            name = "assessment",
            height = 27,
            width = 16,
            image = "gis_marker.image.Assessment.png"
        )
        asset = table.insert(
            name = "asset",
            height = 27,
            width = 16,
            image = "gis_marker.image.Asset.png"
        )
        person = table.insert(
            name = "person",
            height = 50,
            width = 50,
            image = "gis_marker.image.Civil_Disturbance_Theme.png"
        )
        school = table.insert(
            name = "school",
            height = 33,
            width = 44,
            image = "gis_marker.image.Edu_Schools_S1.png"
        )
        food = table.insert(
            name = "food",
            height = 40,
            width = 40,
            image = "gis_marker.image.Emergency_Food_Distribution_Centers_S1.png"
        )
        office = table.insert(
            name = "office",
            height = 27,
            width = 16,
            image = "gis_marker.image.Office.png"
        )
        shelter = table.insert(
            name = "shelter",
            height = 40,
            width = 40,
            image = "gis_marker.image.Emergency_Shelters_S1.png"
        )
        activity = table.insert(
            name = "activity",
            height = 40,
            width = 40,
            image = "gis_marker.image.Emergency_Teams_S1.png"
        )
        hospital = table.insert(
            name = "hospital",
            height = 40,
            width = 40,
            image = "gis_marker.image.E_Med_Hospital_S1.png"
        )
        table.insert(
            name = "earthquake",
            height = 50,
            width = 50,
            image = "gis_marker.image.Geo_Earth_Quake_Epicenter.png"
        )
        table.insert(
            name = "volcano",
            height = 50,
            width = 50,
            image = "gis_marker.image.Geo_Volcanic_Threat.png"
        )
        table.insert(
            name = "flood",
            height = 50,
            width = 50,
            image = "gis_marker.image.Hydro_Meteor_Flood.png"
        )
        table.insert(
            name = "tsunami",
            height = 50,
            width = 50,
            image = "gis_marker.image.Hydro_Meteor_Tsunami_ch.png"
        )
        project = table.insert(
            name = "project",
            height = 27,
            width = 16,
            image = "gis_marker.image.Project.png"
        )
        incident = table.insert(
            name = "incident",
            height = 27,
            width = 16,
            image = "gis_marker.image.Incident.png"
        )
        church = table.insert(
            name = "church",
            height = 33,
            width = 44,
            image = "gis_marker.image.Public_Venue_Church_S1.png"
        )
        table.insert(
            name = "mosque",
            height = 33,
            width = 44,
            image = "gis_marker.image.Public_Venue_Mosque_S1.png"
        )
        table.insert(
            name = "temple",
            height = 33,
            width = 44,
            image = "gis_marker.image.Public_Venue_Temple_S1.png"
        )
        phone = table.insert(
            name = "phone",
            height = 10,
            width = 5,
            image = "gis_marker.image.SMS_Message_Phone.png"
        )
        table.insert(
            name = "orphanage",
            height = 33,
            width = 44,
            image = "gis_marker.image.Special_Needs_Child_Day_Care_S1.png"
        )
        airport = table.insert(
            name = "airport",
            height = 33,
            width = 44,
            image = "gis_marker.image.Trans_Airport_S1.png"
        )
        bridge = table.insert(
            name = "bridge",
            height = 33,
            width = 44,
            image = "gis_marker.image.Trans_Bridge_S1.png"
        )
        table.insert(
            name = "helicopter",
            height = 33,
            width = 44,
            image = "gis_marker.image.Trans_Helicopter_Landing_Site_S1.png"
        )
        port = table.insert(
            name = "port",
            height = 33,
            width = 44,
            image = "gis_marker.image.Trans_Port_S1.png"
        )
        table.insert(
            name = "rail_station",
            height = 33,
            width = 44,
            image = "gis_marker.image.Trans_Rail_Station_S1.png"
        )
        vehicle = table.insert(
            name = "vehicle",
            height = 50,
            width = 50,
            image = "gis_marker.image.Transport_Vehicle_Theme.png"
        )
        water = table.insert(
            name = "water",
            height = 33,
            width = 44,
            image = "gis_marker.image.Water_Supply_Infrastructure_Theme_S1.png"
        )
        table.insert(
            name = "volunteer2",
            height = 40,
            width = 39,
            image = "gis_marker.image.Volunteer2.png"
        )
        volunteer = table.insert(
            name = "volunteer",
            height = 27,
            width = 16,
            image = "gis_marker.image.Volunteer.png"
        )
        staff = table.insert(
            name = "staff",
            height = 27,
            width = 16,
            image = "gis_marker.image.Staff.png"
        )
        warehouse = table.insert(
            name = "warehouse",
            height = 27,
            width = 16,
            image = "gis_marker.image.Warehouse.png"
        )
    table = db.gis_symbology
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        table.insert(
            name = "Australasia"
        )
        table.insert(
            name = "Canada"
        )
        # "US" is the default symbology. If you remove it or change its name,
        # also change S3Config.get_gis_default_symbology().
        table.insert(
            name = "US"
        )
    table = db.gis_projection
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # We want to start at ID 1, but postgres won't let us truncate() & not needed anyway this is only run on 1st_run.
        #table.truncate()
        # "Spherical Mercator" is the default projection. If you remove it or
        # change its name, also change S3Config.get_gis_default_projection().
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-PROJECTION-900913",
            name = "Spherical Mercator",
            epsg = 900913,
            maxExtent = "-20037508, -20037508, 20037508, 20037508.34",
            maxResolution = 156543.0339,
            units = "m"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-PROJECTION-4326",
            name = "WGS84",
            epsg = 4326,
            maxExtent = "-180,-90,180,90",
            maxResolution = 1.40625,
            units = "degrees"
            # OSM use these:
            #maxResolution = 156543.0339,
            #units = "m"
        )

    table = db.gis_config
    # Ensure that the projection/marker we defined are in the DB ready to be
    # used as FKs
    db.commit()
    query = db.gis_symbology.name == deployment_settings.get_gis_default_symbology()
    site_symbology = db(query).select(db.gis_symbology.id,
                                      limitby=(0, 1)).first().id
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # We want to start at ID 1, but postgres won't let us truncate() & not
        # needed anyway as this is only run on 1st_run.
        #table.truncate()
        default_gis_config_values = Storage()
        default_gis_config_values.update(
            deployment_settings.get_gis_default_config_values())
        if not default_gis_config_values.symbology_id:
            default_gis_config_values.symbology_id = site_symbology
        if not default_gis_config_values.projection_id:
            query = db.gis_projection.name == deployment_settings.get_gis_default_projection()
            projection_id = db(query).select(db.gis_symbology.id,
                                             limitby=(0, 1)).first().id
            if projection_id:
                default_gis_config_values.projection_id = projection_id
        if not default_gis_config_values.marker_id:
            query = db.gis_marker.name == deployment_settings.get_gis_default_marker()
            marker_id = db(query).select(db.gis_marker.id,
                                         limitby=(0, 1)).first().id
            if marker_id:
                default_gis_config_values.marker_id = marker_id
        default_gis_config_values.update(
            gis.get_location_hierarchy_settings())
        # Since the values from deployment_settings have not been validated,
        # check them.
        errors = Storage()
        gis.config_onvalidation(default_gis_config_values, errors)
        # Do a minimal fixup of any errors.
        # If there's an error in region settings, don't show it in the menu.
        if errors.region_location_id or errors.name:
            default_gis_config_values.show_in_menu = False
        # If there are missing level names, default them to Ln.
        for error in errors:
            if len(error) == 2 and error[0] == "L":
                default_gis_config_values[error] = error
        # @ToDo: Log the errors.

        table.insert(**default_gis_config_values)

    # Feature Classes
    # - used to provide Markers for Feed Exports, like KML
    table = db.gis_feature_class
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-TRACK",
            name = "Track",
            gps_marker = "TracBack Point",
            resource = "gis_track"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-L0",
            name = "Country",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-L1",
            name = "Province",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-L2",
            name = "District",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-L3",
            name = "Town",
            gps_marker = "City (Medium)",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-L4",
            name = "Village",
            gps_marker = "City (Small)",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-AIRPORT",
            name = "Airport",
            symbology_id = site_symbology,
            marker_id = airport,
            gps_marker = "Airport",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-ASSESSMENT",
            name = "Assessment",
            marker_id = assessment,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-ASSET",
            name = "Asset",
            marker_id = asset,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-BRIDGE",
            name = "Bridge",
            symbology_id = site_symbology,
            marker_id = bridge,
            gps_marker = "Bridge",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-CHURCH",
            name = "Church",
            symbology_id = site_symbology,
            marker_id = church,
            gps_marker = "Church",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-FOOD",
            name = "Food",
            symbology_id = site_symbology,
            marker_id = food,
            gps_marker = "Restaurant",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-HOSPITAL",
            name = "Hospital",
            symbology_id = site_symbology,
            marker_id = hospital,
            gps_marker = "Medical Facility",
            resource = "hms_hospital"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-INCIDENT",
            name = "Incident",
            marker_id = incident,
            gps_marker = "Danger Area",
            resource = "irs_ireport"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-OFFICE",
            name = "Office",
            symbology_id = site_symbology,
            marker_id = office,
            gps_marker = "Building",
            resource = "org_office"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-PERSON",
            name = "Person",
            symbology_id = site_symbology,
            marker_id = person,
            gps_marker = "Contact, Dreadlocks",
            resource = "pr_person"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-PORT",
            name = "Port",
            symbology_id = site_symbology,
            marker_id = port,
            gps_marker = "Marina",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-PROJECT",
            name = "Project",
            marker_id = project,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-SCHOOL",
            name = "School",
            marker_id = school,
            gps_marker = "School",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-SHELTER",
            name = "Shelter",
            symbology_id = site_symbology,
            marker_id = shelter,
            gps_marker = "Campground",
            resource = "cr_shelter"
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-SMS",
            name = "SMS",
            marker_id = phone,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-STAFF",
            name = "Staff",
            symbology_id = site_symbology,
            marker_id = staff,
            gps_marker = "Contact, Dreadlocks",
            resource = "hrm_human_resource",
            filter_field = "type",
            filter_value = 1,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-VEHICLE",
            name = "Vehicle",
            symbology_id = site_symbology,
            marker_id = vehicle,
            gps_marker = "Car",
            resource = "asset_asset",
            filter_field = "type",
            filter_value = 1,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-VOLUNTEER",
            name = "Volunteer",
            symbology_id = site_symbology,
            marker_id = volunteer,
            gps_marker = "Contact, Dreadlocks",
            resource = "hrm_human_resource",
            filter_field = "type",
            filter_value = 2,
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-WAREHOUSE",
            name = "Warehouse",
            symbology_id = site_symbology,
            marker_id = warehouse,
            gps_marker = "Building",
        )
        table.insert(
            uuid = "www.sahanafoundation.org/GIS-FEATURE-CLASS-WATER",
            name = "Water",
            symbology_id = site_symbology,
            marker_id = water,
            gps_marker = "Drinking Water",
        )
    table = db.gis_layer_feature
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        table.insert(
            name = "Events",
            module = "irs",
            resource = "ireport",
            popup_label = "Event",
            popup_fields = "name/category",
            # Default (but still better to define here as otherwise each feature needs to check it's feature_class)
            marker_id = incident
        )
        table.insert(
            name = "Offices",
            module = "org",
            resource = "office",
            comments = "All Active Offices",
            filter = "office.type=None,1,2,3,4&office.obsolete=False",
            popup_label = "Office",
            popup_fields = "name/organisation_id",
            marker_id = office
        )
        table.insert(
            name = "Staff",
            module = "hrm",
            resource = "human_resource",
            comments = "All Active Staff",
            filter = "human_resource.type=1&human_resource.status=1",
            popup_label = "Staff",
            popup_fields = "person_id/job_title/organisation_id",
            marker_id = staff
        )
        table.insert(
            name = "Volunteers",
            module = "hrm",
            resource = "human_resource",
            comments = "All Active Volunteers",
            filter = "human_resource.type=2&human_resource.status=1",
            popup_label = "Volunteer",
            popup_fields = "person_id/job_title/organisation_id",
            marker_id = volunteer,
            visible = False
        )
        table.insert(
            name = "Warehouses",
            module = "org",
            resource = "office",
            comments = "All Active Warehouses",
            filter = "office.type=5&office.obsolete=False",
            popup_label = "Warehouse",
            popup_fields = "name/organisation_id",
            marker_id = warehouse
        )
        table.insert(
            name = "Assets",
            module = "asset",
            resource = "asset",
            popup_label = "Asset",
            popup_fields = "item_id/number", # Would like Status & Condition here, but currently they're a Join away
            visible = False
        )
        table.insert(
            name = "Project Communities",
            module = "project",
            resource = "activity",
            popup_label = "Project Communities",
            #popup_fields = "",
            marker_id = project,
            visible = False
        )
        #table.insert(
        #    name = "Vehicles",
        #    module = "asset",
        #    resource = "asset",
        #    filter = "asset.type=1",
        #    popup_label = "Vehicle",
        #    popup_fields = "item_id/number", # Would like Status & Condition here, but currently they're a Join away
        #    marker_id = vehicle
        #)
    table = db.gis_layer_bing
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table with single default Record
        table.insert(
            name = "Bing",
            apikey = "", # Insert API Key here
            enabled = False
        )
    table = db.gis_layer_coordinate
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table with single default Record
        table.insert(
                name = "Coordinate Grid",
                enabled = False,
                visible = False
            )
    table = db.gis_layer_openstreetmap
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table
        table.insert(
                name = "OpenStreetMap (Mapnik)",
                url1 = "http://a.tile.openstreetmap.org/",
                url2 = "http://b.tile.openstreetmap.org/",
                url3 = "http://c.tile.openstreetmap.org/",
                attribution = '<a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>',
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (CycleMap)",
                url1 = "http://a.tile.opencyclemap.org/cycle/",
                url2 = "http://b.tile.opencyclemap.org/cycle/",
                url3 = "http://c.tile.opencyclemap.org/cycle/",
                attribution = '<a href="http://www.opencyclemap.org/" target="_blank">OpenCycleMap</a>',
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (Labels)",
                url1 = "http://tiler1.censusprofiler.org/labelsonly/",
                attribution = 'Labels overlay CC-by-SA by <a href="http://oobrien.com/oom/" target="_blank">OpenOrienteeringMap</a>/<a href="http://www.openstreetmap.org/">OpenStreetMap</a> data',
                base = False,
                visible = False,
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (Relief)",
                url1 = "http://toolserver.org/~cmarqu/hill/",
                attribution = 'Relief by <a href="http://hikebikemap.de/" target="_blank">Hike &amp; Bike Map</a>',
                base = False,
                visible = False,
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (MapQuest)",
                url1 = "http://otile1.mqcdn.com/tiles/1.0.0/osm/",
                url2 = "http://otile2.mqcdn.com/tiles/1.0.0/osm/",
                url3 = "http://otile3.mqcdn.com/tiles/1.0.0/osm/",
                attribution = 'Tiles Courtesy of <a href="http://open.mapquest.co.uk/" target="_blank">MapQuest</a> <img src="http://developer.mapquest.com/content/osm/mq_logo.png" border="0">',
                enabled = True
            )
        table.insert(
                name = "OpenStreetMap (Osmarender)",
                url1 = "http://a.tah.openstreetmap.org/Tiles/tile/",
                url2 = "http://b.tah.openstreetmap.org/Tiles/tile/",
                url3 = "http://c.tah.openstreetmap.org/Tiles/tile/",
                attribution = '<a href="http://www.openstreetmap.org/" target="_blank">OpenStreetMap</a>',
                zoom_levels = 18,
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (Taiwan)",
                url1 = "http://tile.openstreetmap.tw/tiles/",
                enabled = False
            )
        table.insert(
                name = "OpenStreetMap (Sahana)",
                url1 = "http://geo.eden.sahanafoundation.org/tiles/",
                enabled = False
            )
        #table.insert(
        #        name = "OpenAerialMap",
        #        url1 = "http://tile.openaerialmap.org/tiles/1.0.0/openaerialmap-900913/",
        #        enabled = False
        #    )
    table = db.gis_layer_google
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
       # Populate table with single default Record
        table.insert(
            name = "Google",
            apikey = "ABQIAAAAgB-1pyZu7pKAZrMGv3nksRTpH3CbXHjuCVmaTc5MkkU4wO1RRhQWqp1VGwrG8yPE2KhLCPYhD7itFw", # http://127.0.0.1:8000
            enabled = True
        )
    table = db.gis_layer_mgrs
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table
        table.insert(
                name = "MGRS Atlas PDFs",
                description = "http://en.wikipedia.org/wiki/Military_grid_reference_system",
                url = "http://www.sharedgeo.org/datasets/shared/maps/usng/pdf.map?VERSION=1.0.0&SERVICE=WFS&request=GetFeature&typename=wfs_all_maps",
                enabled = False
            )
    table = db.gis_layer_tms
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table
        table.insert(
                name = "Blue Marble Topography & Bathymetry (January)",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "blue-marble-topo-bathy-jan",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Blue Marble Topography & Bathymetry (July)",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "blue-marble-topo-bathy-jul",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Blue Marble Topography (January)",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "blue-marble-topo-jan",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Blue Marble Topography (July)",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "blue-marble-topo-jul",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Control Room",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "control-room",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Geography Class",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "geography-class",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 9,
                enabled = False
            )
        table.insert(
                name = "Natural Earth Hypsometric",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "natural-earth-hypso",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 7,
                enabled = False
            )
        table.insert(
                name = "Natural Earth Hypsometric & Bathymetry",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "natural-earth-hypso-bathy",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 7,
                enabled = False
            )
        table.insert(
                name = "Natural Earth I",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "natural-earth-1",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 7,
                enabled = False
            )
        table.insert(
                name = "Natural Earth II",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "natural-earth-2",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 7,
                enabled = False
            )
        table.insert(
                name = "World Dark",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "world-dark",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 12,
                enabled = False
            )
        table.insert(
                name = "World Light",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "world-light",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 12,
                enabled = False
            )
        table.insert(
                name = "World Glass",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "world-glass",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 11,
                enabled = False
            )
        table.insert(
                name = "World Print",
                description = "MapBox",
                url = "http://a.tiles.mapbox.com/mapbox/",
                url2 = "http://b.tiles.mapbox.com/mapbox/",
                url3 = "http://c.tiles.mapbox.com/mapbox/",
                layername = "world-print",
                attribution = '<a href="http://mapbox.com" target="_blank">MapBox</a>',
                zoom_levels = 10,
                enabled = False
            )

    table = db.gis_layer_georss
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # Populate table
        table.insert(
                name = "Earthquakes",
                description = "USGS: Global 7-day",
                url = "http://earthquake.usgs.gov/eqcenter/catalogs/eqs7day-M2.5.xml",
                marker_id = db(db.gis_marker.name == "earthquake").select(db.gis_marker.id,
                                                                          limitby=(0, 1)).first().id,
                enabled = False
            )
        table.insert(
                name = "Floods",
                description = "Dartmouth Flood Observatory",
                url = "http://www.gdacs.org/xml/rssfl.xml",
                image = "gdas:gfds_image",
                marker_id = db(db.gis_marker.name == "flood").select(db.gis_marker.id,
                                                                          limitby=(0, 1)).first().id,
                enabled = False
            )
        table.insert(
                name = "Volcanoes",
                description = "USGS: US recent",
                url = "http://volcano.wr.usgs.gov/rss/vhpcaprss.xml",
                marker_id = db(db.gis_marker.name == "volcano").select(db.gis_marker.id,
                                                                       limitby=(0, 1)).first().id,
                enabled = False
            )

    tablename = "gis_location"
    table = db[tablename]
    if not db(table.id > 0).select(table.id, limitby=(0, 1)).first():
        # L0 Countries
        import_file = os.path.join(request.folder,
                                   "private",
                                   "import",
                                   "countries.csv")
        table.import_from_csv_file(open(import_file, "r"))
        query = (db.auth_group.uuid == sysroles.MAP_ADMIN)
        map_admin = db(query).select(db.auth_group.id,
                                     limitby=(0, 1)).first().id
        db(table.level == "L0").update(owned_by_role=map_admin)
    # Should work for our 3 supported databases: sqlite, MySQL & PostgreSQL
    field = "name"
    db.executesql("CREATE INDEX %s__idx on %s(%s);" % \
        (field, tablename, field))

    if "climate" in deployment_settings.modules:
        climate_first_run()

    # Ensure DB population committed when running through shell
    db.commit()

    # Prepopulate import (from CSV)

    # Override authorization
    auth.override = True

    # Disable table protection
    protected = s3mgr.PROTECTED
    s3mgr.PROTECTED = []

    # Additional settings for user table imports:
    s3mgr.configure("auth_user",
                    onaccept = lambda form: \
                        auth.s3_link_to_person(user=form.vars))
    s3mgr.model.add_component("auth_membership", auth_user="user_id")

    # Create the bulk Importer object
    bi = s3base.S3BulkImporter()

    # Allow population via shell scripts
    if not request.env.request_method:
        request.env.request_method = "GET"

    # Import data specific to the prepopulate setting
    if populate == 1:
        # Populate with the default data
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "default")
        bi.perform_tasks(path)

    elif populate == 2:
        # Populate data for the regression tests
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "regression")
        bi.perform_tasks(path)

    elif populate == 3:
        # Populate data for scalability testing
        # This is different from the repeatable imports that use csv files
        # This will generate millions of records of data for selected tables.

        # Code needs to go here to generate a large volume of test data
        pass

    elif populate == 10:
        # Populate data for user specific data
        path = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "user")
        bi.perform_tasks(path)

    elif populate >= 20:
        # Populate data for a deployment default demo
        """
            Read the demo_folders file and extract the folder for the specific demo
        """
        file = os.path.join(request.folder,
                            "private",
                            "prepopulate",
                            "demo",
                            "demo_folders.cfg")
        source = open(file, "r")
        values = source.readlines()
        source.close()
        demo = ""
        for demos in values:
            # strip out the new line
            demos = demos.strip()
            if demos == "":
                continue
            # split at the comma
            details = demos.split(",")
            if len(details) == 2:
                 # remove any spaces and enclosing double quote
                index = details[0].strip('" ')
                if int(index) == populate:
                    directory = details[1].strip('" ')
                    path = os.path.join(request.folder,
                                        "private",
                                        "prepopulate",
                                        "demo",
                                        directory)
                    demo = directory
                    if os.path.exists(path):
                        bi.perform_tasks(path)
                    else:
                        print >> sys.stderr, "Unable to install demo %s no demo directory found" % index
        if demo == "":
            print >> sys.stderr, "Unable to install a demo with of an id '%s', please check 000_config and demo_folders.cfg" % populate
        else:
            print >> sys.stderr, "Installed demo '%s'" % demo

    for errorLine in bi.errorList:
        print >> sys.stderr, errorLine
    # Restore table protection
    s3mgr.PROTECTED = protected

    # Restore view
    response.view = "default/index.html"
