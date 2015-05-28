# -*- coding: utf-8 -*-

"""
    Population Outreach Module - Controllers
"""

module = request.controller

if not settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

# -----------------------------------------------------------------------------
def index():
    """ Module's Home Page """

    # Page title
    module_name = settings.modules[module].name_nice

    response.title = module_name
    output = {"module_name": module_name}

    # Extract summary information
    atable = s3db.po_area
    htable = s3db.po_household
    rtable = s3db.po_organisation_household
    ftable = s3db.po_household_followup
    otable = s3db.po_referral_organisation

    # => Number of households
    query = (htable.deleted != True)
    count = htable.id.count()
    row = db(query).select(count).first()
    total_households = row[count]

    # => Number of referrals
    query = (rtable.deleted != True) & \
            (rtable.household_id == htable.id) & \
            (htable.deleted != True)
    count = rtable.id.count()
    row = db(query).select(count).first()
    total_referrals = row[count]

    # => Number of agencies involved
    query = (otable.deleted != True) & \
            (rtable.deleted != True) & \
            (rtable.organisation_id == otable.organisation_id)
    count = otable.id.count()
    rows = db(query).select(otable.id, groupby=otable.id)
    total_agencies = len(rows)

    # => Number of follow ups (broken down into pending/completed)
    query = (ftable.deleted != True) & \
            (ftable.household_id == htable.id) & \
            (htable.deleted != True) & \
            (htable.followup == True)
    count = ftable.id.count()
    completed = ftable.completed
    rows = db(query).select(completed, count, groupby=completed)
    follow_ups_pending, follow_ups_completed = 0, 0
    for row in rows:
        if row[completed]:
            follow_ups_completed += row[count]
        else:
            follow_ups_pending += row[count]
    total_follow_ups = follow_ups_pending + follow_ups_completed

    # => Number of attempted visits
    query = (atable.deleted != True)
    total = atable.attempted_visits.sum()
    result = db(query).select(total).first()
    total_attempted_visits = result[total] or 0

    # Summary
    output["summary"] = DIV(DIV(LABEL("%s: " % T("Total Households Visited")),
                                SPAN(total_households),
                                _class="po-summary-info",
                                ),
                            DIV(LABEL("%s: " % T("Attempted Visits")),
                                SPAN(total_attempted_visits),
                                _class="po-summary-info",
                                ),
                            DIV(LABEL("%s: " % T("Follow-ups")),
                                SPAN(total_follow_ups),
                                SPAN("(%s %s, %s %s)" % (follow_ups_completed,
                                                         T("completed"),
                                                         follow_ups_pending,
                                                         T("pending"),
                                                         )
                                     ),
                                _class="po-summary-info",
                                ),
                            DIV(LABEL("%s: " % T("Total Referrals Made")),
                                SPAN(total_referrals),
                                _class="po-summary-info",
                                ),
                            DIV(LABEL("%s: " % T("Agencies Involved")),
                                SPAN(total_agencies),
                                _class="po-summary-info",
                                ),
                            _class="po-summary",
                            )

    # Map of areas covered
    ftable = s3db.gis_layer_feature
    query = (ftable.controller == "po") & \
            (ftable.function == "area")
    layer = db(query).select(ftable.layer_id, limitby=(0, 1)).first()

    if layer:
        # We can take advantage of per-feature styling
        layer_id = layer.layer_id
        areas = {"name": T("Areas Covered"),
                 "id": "areas",
                 "active": True,
                 "layer_id": layer_id,
                 }
    else:
        # All features will be styled the same
        areas = {"name": T("Areas Covered"),
                 "id": "areas",
                 "active": True,
                 "tablename": "po_area",
                 "url": "area.geojson",
                 "style": '{"fill":"2288CC"}',
                 "opacity": 0.5,
                 }
    map_wrapper = gis.show_map(feature_resources=(areas,),
                               #catalogue_layers = True,
                               collapsed = True,
                               )
    #map_wrapper["_style"] = "width:100%"
    output["map"] = map_wrapper

    return output

# -----------------------------------------------------------------------------
def area():
    """ RESTful Controller for Area Model """

    def prep(r):
        component_name = r.component_name
        if component_name == "household":
            # Set the Starting Location to be that of the Area
            area_location = r.record.location_id
            if area_location:
                gtable = s3db.gis_location
                record = db(gtable.id == area_location).select(gtable.parent,
                                                               limitby=(0, 1)
                                                               ).first()
                if record:
                    s3db.po_household.location_id.default = record.parent

        elif component_name == "organisation":
            # Filter to just referral agencies
            otable = s3db.org_organisation
            rtable = s3db.po_referral_organisation
            atable = s3db.po_organisation_area
            query = (rtable.id != None) & \
                    ((atable.area_id == None) | (atable.area_id != r.id))
            left = [rtable.on((rtable.organisation_id == otable.id) & \
                              (rtable.deleted != True)),
                    atable.on((atable.organisation_id == otable.id) & \
                              (atable.deleted != True)),
                    ]
            atable.organisation_id.requires = IS_ONE_OF(
                                    db(query),
                                    "org_organisation.id",
                                    atable.organisation_id.represent,
                                    left=left,
                                    error_message=T("Agency is required")
                                    )

        return True
    s3.prep = prep

    return s3_rest_controller(rheader = s3db.po_rheader)

# -----------------------------------------------------------------------------
def household():
    """ RESTful Controller for Household Model """

    def prep(r):

        record = r.record

        if r.component_name == "person":
            # Configure CRUD form and list fields
            s3db.add_components("pr_person",
                                po_age_group = {"joinby": "person_id",
                                                "multiple": False,
                                                },
                                )
            crud_form = s3base.S3SQLCustomForm("first_name",
                                               "middle_name",
                                               "last_name",
                                               "gender",
                                               "age_group.age_group",
                                               )
            list_fields = ["first_name",
                           "middle_name",
                           "last_name",
                           "gender",
                           "age_group.age_group",
                           ]
            s3db.configure("pr_person",
                           crud_form = crud_form,
                           list_fields = list_fields,
                           )
            # Tweak CRUD strings
            crud_strings = s3.crud_strings["pr_person"]
            crud_strings["label_create"] = T("Add Household Member")

        # Filter organisations to just referrals and by area
        # @todo: suppress area filter per deployment setting
        elif record and r.component_name == "organisation_household":

            table = r.component.table
            otable = s3db.org_organisation
            rtable = s3db.po_referral_organisation
            atable = s3db.po_organisation_area

            query = (rtable.id != None) & \
                    ((atable.area_id == record.area_id) |
                     (atable.area_id == None))
            left = [rtable.on((rtable.organisation_id == otable.id) & \
                              (rtable.deleted != True)),
                    atable.on((atable.organisation_id == otable.id) & \
                              (atable.deleted != True)),
                    ]

            table.organisation_id.requires = IS_ONE_OF(
                                    db(query),
                                    "org_organisation.id",
                                    atable.organisation_id.represent,
                                    left=left,
                                    error_message=T("Agency is required")
                                    )

        return True
    s3.prep = prep

    def postp(r, output):
        # Replace normal list button by summary button
        if isinstance(output, dict) and "buttons" in output:
            buttons = output["buttons"]
            if "summary_btn" in buttons:
                buttons["list_btn"] = buttons["summary_btn"]
        return output
    s3.postp = postp

    return s3_rest_controller(rheader = s3db.po_rheader)

# -----------------------------------------------------------------------------
def due_followups():
    """ RESTful Controller for Due Follow-ups """

    # CRUD Strings
    s3.crud_strings["po_household_followup"] = Storage(
        title_display = T("Follow-up Details"),
        title_list = T("Due Follow-ups"),
        title_update = T("Edit Follow-up Details"),
        label_list_button = T("List Follow-ups"),
        msg_record_modified = T("Follow-up Details updated"),
        msg_list_empty = T("No due follow-ups"),
    )

    # Filter Widgets
    from s3 import S3DateFilter, S3OptionsFilter, S3TextFilter
    filter_widgets = [S3TextFilter(["household_id$location_id$addr_street",
                                    "followup_required",
                                    "comments",
                                    ],
                                    label = T("Search"),
                                   ),
                      S3OptionsFilter("household_id$area_id"),
                      S3DateFilter("household_id$date_visited",
                                   label = T("Date visited"),
                                   hidden = True,
                                   ),
                      S3DateFilter("followup_date",
                                   hidden=True,
                                   ),
                      ]

    s3db.configure("po_household_followup",
                   insertable = False,
                   deletable = False,
                   filter_widgets = filter_widgets,
                   list_fields = ["followup_date",
                                  "household_id$area_id",
                                  "household_id",
                                  "followup_required",
                                  "comments",
                                  ],
                   )

    def prep(r):
        if not r.record:
            query = (FS("followup_date") <= datetime.datetime.utcnow().date()) & \
                    (FS("completed") != True)
            r.resource.add_filter(query)
        return True
    s3.prep = prep

    return s3_rest_controller("po", "household_followup")

# -----------------------------------------------------------------------------
def organisation():
    """ RESTful Controller for Organisation (Referral Agencies) """

    def prep(r):

        # @todo: limit organisation types?
        # @todo: hide unwanted form fields?

        # Filter for just referral agencies
        query = FS("organisation_id:po_referral_organisation.id") != None
        r.resource.add_filter(query)

        # Create referral_organisation record onaccept
        onaccept = s3db.get_config("org_organisation", "onaccept")
        s3db.configure("org_organisation",
                       onaccept = (onaccept, s3db.po_organisation_onaccept))

        # Filter households to areas served (if any areas defined)
        # @todo: suppress this filter per deployment setting
        if r.record and r.component_name == "organisation_household":

            atable = s3db.po_organisation_area
            query = (atable.organisation_id == r.id) & \
                    (atable.deleted != True)
            rows = db(query).select(atable.area_id)
            if rows:
                area_ids = [row.area_id for row in rows]
                area_ids.append(None)
                table = r.component.table
                table.household_id.requires.set_filter(filterby="area_id",
                                                       filter_opts=area_ids,
                                                       )

        if r.interactive:
            # Adapt CRUD Strings
            s3.crud_strings["org_organisation"].update(
                {"label_create": T("Create Agency"),
                 "title_list": T("Referral Agencies"),
                 "title_display": T("Agency Details"),
                 "title_update": T("Edit Agency Details"),
                 "label_delete_button": T("Delete Agency"),
                 }
            )
            if r.component_name == "area":
                s3.crud_strings["po_organisation_area"].update(
                    {"label_create": T("Add Area"),
                     }
                )

        return True
    s3.prep = prep

    return s3_rest_controller("org", "organisation",
                              rheader = s3db.po_rheader)

# -----------------------------------------------------------------------------
def organisation_area():
    """ @todo: docstring """

    s3.prep = lambda r: r.representation == "s3json" and r.method == "options"
    return s3_rest_controller()

# END =========================================================================
