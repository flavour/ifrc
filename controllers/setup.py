# -*- coding: utf-8 -*-

"""
    Setup Tool:
        Assists with Installation of a Deployment
        tbc: Assists with Configuration of a Deployment
"""

module = request.controller

if not settings.has_module(module):
    raise HTTP(404, body="Module disabled: %s" % module)

if not s3_has_role("ADMIN"):
        auth.permission.fail()

# -----------------------------------------------------------------------------
def index():
    """ Show the index """

    dtable = s3db.setup_deployment
    exists = db(dtable.id > 0).select(dtable.id,
                                      limitby = (0, 1),
                                      )
    if exists:
        # Redirect to the list of deployments
        redirect(URL(c="setup", f="deployment"))
    else:
        templates = settings.get_template()
        if templates != "setup":
            # Import the current deployment
            country = None
            if isinstance(templates, list):
                for template in templates:
                    try:
                        country = template.split("locations.", 1)[1]
                    except IndexError:
                        continue
                    else:
                        break
                if country:
                    templates.remove("locations.%s" % country)
            deployment_id = s3db.setup_deployment.insert(# @ToDo:
                                                         #repo_url = ,
                                                         country = country,
                                                         template = templates,
                                                         db_password = settings.database.get("password"),
                                                         )
            # @ToDo: Support multi-host deployments
            s3db.setup_server.insert(deployment_id = deployment_id,
                                     )
            task_id = current.s3task.async("dummy")
            instance_id = s3db.setup_instance.insert(deployment_id = deployment_id,
                                                     url = settings.get_base_public_url(),
                                                     sender = settings.get_mail_sender(),
                                                     task_id = task_id,
                                                     )
            s3db.setup_instance_settings_read(instance_id, deployment_id)

            # Redirect to the list of deployments
            redirect(URL(c="setup", f="deployment"))

    # User-friendly index page to step through deploying Eden
    return {}

# -----------------------------------------------------------------------------
def deployment():

    def prep(r):
        if r.interactive:
            s3.scripts.append("/%s/static/scripts/S3/s3.setup.js" % appname)
            if r.component:

                # No new servers once deployment is created
                #s3db.configure("setup_server",
                #               insertable = False
                #               )

                # Check if no scheduler task is pending
                #itable = s3db.setup_instance
                #sctable = db.scheduler_task
                #query = (itable.deployment_id == r.id) & \
                #        ((sctable.status != "COMPLETED") & \
                #        (sctable.status  != "FAILED")) & \
                #        (itable.task_id == sctable.id)

                #exists = db(query).select(itable.task_id,
                #                          limitby = (0, 1)
                #                          ).first()

                #if exists:
                #    # Disable creation of new instances
                #    s3db.configure("setup_instance",
                #                   insertable = False
                #                   )

                if r.component.name == "instance":
                    if r.method in (None, "create"):
                        itable = db.setup_instance
                        # Additional instances off by default
                        itable.start.default = False
                        # Remove already-deployed instances from dropdown
                        sctable = db.scheduler_task
                        query = (itable.deployment_id == r.id) & \
                                (sctable.status == "COMPLETED")

                        rows = db(query).select(itable.type,
                                                join = itable.on(itable.task_id == sctable.id)
                                                )
                        types = {1: "prod",
                                 2: "setup",
                                 3: "test",
                                 4: "demo",
                                 }
                        for row in rows:
                            del types[row.type]

                        itable.type.requires = IS_IN_SET(types)

            elif r.method == "create":
                # Include Production URL/Sender in main form

                # Redefine Component to make 1:1
                #s3db.add_components("setup_deployment",
                #                    setup_instance = {"joinby": "deployment_id",
                #                                      "multiple": False,
                #                                      },
                #                    )
                # Reset the component (we're past resource initialization)
                #r.resource.components.reset(("instance",))

                from s3 import S3SQLCustomForm
                crud_form = S3SQLCustomForm((T("Production URL"), "production.url"),
                                            "production.sender",
                                            #"repo_url",
                                            "country",
                                            "template",
                                            "webserver_type",
                                            "db_type",
                                            "remote_user",
                                            "private_key",
                                            #"secret_key",
                                            #"access_key",
                                            )

                s3db.configure("setup_deployment",
                               crud_form = crud_form,
                               )

        return True
    s3.prep = prep

    def postp(r, output):
        component = r.component
        if component is None:
            #if r.id and r.method in (None, "read") and "item" in output:
            #    # Get scheduler status for the last queued task
            #    itable = db.setup_instance
            #    sctable = db.scheduler_task

            #    query = (db.setup_instance.deployment_id == r.id)
            #    row = db(query).select(sctable.id,
            #                           sctable.status,
            #                           join = itable.on(itable.task_id == sctable.id),
            #                           orderby = itable.task_id
            #                           ).last()
            #    if row:
            #        item_append = output["item"][0].append
            #        item_append(TR(TD(LABEL("Status"), _class="w2p_fl")))
            #        item_append(TR(TD(row.status)))
            #        if row.status == "FAILED":
            #            resource = s3db.resource("scheduler_run")
            #            task = db(resource.table.task_id == row.id).select().first()
            #            item_append(TR(TD(LABEL("Traceback"), _class="w2p_fl")))
            #            item_append(TR(TD(task.traceback)))
            #            item_append(TR(TD(LABEL("Output"), _class="w2p_fl")))
            #            item_append(TR(TD(task.run_output)))
            pass

        else:
            cname = component.name
            if cname == "instance" and r.method in (None, "read"):
                # Normal Action Buttons
                s3_action_buttons(r)
                # Custom Action Buttons
                table = component.table
                deployment_id = r.id
                query = (table.deployment_id == deployment_id) & \
                        (table.deleted == False)
                rows = db(query).select(table.id,
                                        table.task_id,
                                        )
                restrict_d = [str(row.id) for row in rows if row.task_id is None]
                restrict_s = [str(row.id) for row in rows if row.task_id is not None]
                s3.actions += [{"url": URL(c = module,
                                           f = "deployment",
                                           args = [deployment_id, "instance", "[id]", "deploy"],
                                           ),
                                "_class": "action-btn",
                                "label": s3_str(T("Deploy")),
                                "restrict": restrict_d,
                                },
                               {"url": URL(c = module,
                                           f = "deployment",
                                           args = [deployment_id, "instance", "[id]", "settings"],
                                           ),
                                "_class": "action-btn",
                                "label": s3_str(T("Read Settings")),
                                "restrict": restrict_s,
                                },
                               {"url": URL(c = module,
                                           f = "deployment",
                                           args = [deployment_id, "instance", "[id]", "start"],
                                           ),
                                "_class": "action-btn",
                                "label": s3_str(T("Start")),
                                "restrict": restrict_s,
                                },
                               {"url": URL(c = module,
                                           f = "deployment",
                                           args = [deployment_id, "instance", "[id]", "stop"],
                                           ),
                                "_class": "action-btn",
                                "label": s3_str(T("Stop")),
                                "restrict": restrict_s,
                                },
                               #{"url": URL(c = module,
                               #            f = "management",
                               #            vars = {"instance": "[id]",
                               #                    "type": "clean",
                               #                    "deployment": r.id,
                               #                    }
                               #            ),
                               # "_class": "action-btn",
                               # "label": s3_str(T("Clean")),
                               # },
                               #{"url": URL(c = module,
                               #            f = "management",
                               #            vars = {"instance": "[id]",
                               #                    "type": "eden",
                               #                    "deployment": r.id
                               #                    }
                               #            ),
                               # "_class": "action-btn",
                               # "label": s3_str(T("Upgrade")),
                               # },
                               ]

            elif cname == "setting" and r.method in (None, "read"):
                # Normal Action Buttons
                s3_action_buttons(r)
                # Custom Action Buttons
                table = component.table
                deployment_id = r.id
                query = (table.deployment_id == deployment_id) & \
                        (table.deleted == False)
                rows = db(query).select(table.id,
                                        table.new_value,
                                        )
                restrict_a = [str(row.id) for row in rows if row.new_value is not None]
                s3.actions.append({"url": URL(c = module,
                                              f = "deployment",
                                              args = [deployment_id, "setting", "[id]", "apply"],
                                              ),
                                   "_class": "action-btn",
                                   "label": s3_str(T("Apply")),
                                   "restrict": restrict_a,
                                   })

        return output
    s3.postp = postp

    return s3_rest_controller(rheader = s3db.setup_rheader,
                              )

# -----------------------------------------------------------------------------
def server():

    return s3_rest_controller(#rheader = s3db.setup_rheader,
                              )

# -----------------------------------------------------------------------------
#def instance():

#    return s3_rest_controller(#rheader = s3db.setup_rheader,
#                              )

# -----------------------------------------------------------------------------
#def setting():

#    return s3_rest_controller(#rheader = s3db.setup_rheader,
#                              )

# END =========================================================================
