/**
 * jQuery UI Widget Classes for S3Dashboard
 *
 * @copyright 2016 (c) Sahana Software Foundation
 * @license MIT
 *
 * requires jQuery 1.9.1+
 * requires jQuery UI 1.10 widget factory
 *
 */

(function($, undefined) {

    "use strict";
    var dashboardID = 0;

    /**
     * Dashboard Controller
     */
    $.widget('s3.dashboardController', {

        /**
         * Default options
         *
         * @prop {string} ajaxURL - URL for dashboard agent Ajax requests
         */
        options: {

            ajaxURL: null

        },

        /**
         * Create the widget
         */
        _create: function() {

            var el = $(this.element);

            this.id = dashboardID;
            dashboardID += 1;

            // Namespace for events
            this.eventNamespace = '.dashboard';
        },

        /**
         * Update the widget options
         */
        _init: function() {

            var el = $(this.element);

            this.refresh();

            // @todo: remove
            s3_debug("dashboard initialized");
            s3_debug("dashboard ajaxURL=" + this.options.ajaxURL);
        },

        /**
         * Remove generated elements & reset other changes
         */
        _destroy: function() {

            $.Widget.prototype.destroy.call(this);
        },

        /**
         * Redraw contents
         */
        refresh: function() {

            var opts = this.options;

            this._unbindEvents();

            this._bindEvents();
        },

        /**
         * Get or set the current config-mode status
         *
         * @param {boolean} mode - true|false to turn config mode on/off,
         *                         undefined to return the current status
         */
        configMode: function(mode) {

            var el = this.element,
                ns = this.eventNamespace,
                modeSwitch = $('.db-config');

            if (typeof mode === 'undefined') {

                // Return the current status
                var status = modeSwitch.data('mode');
                if (status == 'on') {
                    mode = true;
                } else {
                    mode = false;
                }

            } else if (mode) {

                // Turn config mode on
                modeSwitch.data('mode', 'on');
                modeSwitch.find('.db-config-on').hide();
                modeSwitch.find('.db-config-off').show().removeClass('hide');

                // Turn on config mode for all widgets
                el.find('.db-widget').each(function() {
                    $(this).dashboardWidget('configMode', true);
                });

                // Trigger openConfig event
                el.trigger('openConfig' + ns);

            } else {

                // Trigger closeConfig event
                el.trigger('closeConfig' + ns);

                // Turn off config mode for all widgets
                el.find('.db-widget').each(function() {
                    $(this).dashboardWidget('configMode', false);
                });

                // Turn config mode off
                modeSwitch.data('mode', 'off');
                modeSwitch.find('.db-config-off').hide();
                modeSwitch.find('.db-config-on').show().removeClass('hide');

            }
            return mode;
        },

        /**
         * Bind events to generated elements (after refresh)
         */
        _bindEvents: function() {

            var ns = this.eventNamespace,
                self = this;

            // Config mode switches
            $('.db-config-on').bind('click' + ns, function() {
                self.configMode(true);
            });
            $('.db-config-off').bind('click' + ns, function() {
                self.configMode(false);
            });

            return true;
        },

        /**
         * Unbind events (before refresh)
         */
        _unbindEvents: function() {

            var ns = this.eventNamespace;

            $('.dashboard-config').unbind(ns);

            return true;
        }
    });
})(jQuery);

// ----------------------------------------------------------------------------

(function($, undefined) {

    "use strict";
    var dashboardWidgetID = 0;

    /**
     * Dashboard Controller
     */
    $.widget('s3.dashboardWidget', {

        /**
         * Default options
         *
         * @todo document options
         */
        options: {

        },

        /**
         * Create the widget
         */
        _create: function() {

            this.id = dashboardWidgetID;
            dashboardWidgetID += 1;

            // Namespace for events
            this.eventNamespace = '.dashboardWidget';
        },

        /**
         * Update the widget options
         */
        _init: function() {

            var el = $(this.element);

            // Identify the config-bar
            this.configBar = el.find('.db-configbar');

            // Refresh the widget contents
            this.refresh();

            // @todo: remove
            s3_debug("dashboard widget initialized");
        },

        /**
         * Remove generated elements & reset other changes
         */
        _destroy: function() {

            $.Widget.prototype.destroy.call(this);
        },

        /**
         * Redraw contents
         */
        refresh: function() {

            var el = $(this.element),
                opts = this.options;

            this._unbindEvents();

            this._bindEvents();
        },

        /**
         * Get or set the current config-mode status
         *
         * @param {bool} mode - true|false to turn config mode on/off,
         *                      undefined to return the current status
         */
        configMode: function(mode) {

            var el = $(this.element);

            if (typeof mode === 'undefined') {
                mode = this.configBar.is(':visible');
            } else if (mode) {
                this.configBar.show();
                el.addClass('db-config-active');
            } else {
                this.configBar.hide();
                el.removeClass('db-config-active');
            }
            return mode;
        },

        /**
         * @todo: docstring
         */
        _openConfigDialog: function() {

            var el = $(this.element),
                self = this;

            if (!$('.db-config-dialog').length) {
                var dialog = $('<div class="db-config-dialog">TESTING</div>').hide().appendTo('body');
                self.configDialog = dialog;
                dialog.dialog({
                    modal: true,
                    open: function() {
                        el.addClass('db-has-dialog');
                    },
                    close: function() {
                        el.removeClass('db-has-dialog');
                        self.configDialog.remove();
                        self.configDialog = null;
                    }
                }).show();
            }
        },

        /**
         * Bind events to generated elements (after refresh)
         */
        _bindEvents: function() {

            var el = $(this.element),
                ns = this.eventNamespace,
                self = this;

            this.configBar.find('.db-task-config').on('click' + ns, function() {
                self._openConfigDialog();
            });

            return true;
        },

        /**
         * Unbind events (before refresh)
         */
        _unbindEvents: function() {

            var ns = this.eventNamespace;

            this.configBar.find('.db-task-config').off('click' + ns);

            return true;
        }
    });
})(jQuery);
