/**
 * jQuery UI Widget for auth_Consent
 *
 * @copyright 2019 (c) Sahana Software Foundation
 * @license MIT
 *
 * requires jQuery 1.9.1+
 * requires jQuery UI 1.10 widget factory
 */
(function($, undefined) {

    "use strict";
    var consentQuestionID = 0;

    /**
     * consentQuestion
     */
    $.widget('s3.consentQuestion', {

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

            this.id = consentQuestionID;
            consentQuestionID += 1;

            this.eventNamespace = '.consentQuestion';
        },

        /**
         * Update the widget options
         */
        _init: function() {

            var el = $(this.element);

            this.input = $('#' + el.attr('id') + '-response');

            this.refresh();
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

            this._unbindEvents();

            this._bindEvents();
        },

        /**
         * Parse the value in the hidden input
         *
         * @returns {object} - the parsed data {code: [id, consenting], ...}
         */
        _deserialize: function() {

            var jsonData = this.input.val(),
                parsed = {};

            if (jsonData) {
                try {
                    parsed = JSON.parse(jsonData);
                } catch(e) {
                    // pass
                }
            }
            return parsed;
        },

        /**
         * Read the status of all consent checkboxes in the widget
         * and update the hidden input accordingly
         */
        _serialize: function() {

            var el = $(this.element),
                responses = this._deserialize();

            $('.consent-checkbox', el).each(function() {

                var code = $(this).data('code'),
                    response = responses[code];

                if (response !== undefined) {
                    response[1] = $(this).prop('checked');
                }
            });

            this.input.val(JSON.stringify(responses));
        },

        /**
         * Bind events to generated elements (after refresh)
         */
        _bindEvents: function() {

            var el = $(this.element),
                ns = this.eventNamespace,
                self = this;

            el.on('change' + ns, '.consent-checkbox', function() {
                self._serialize();
            });

            return true;
        },

        /**
         * Unbind events (before refresh)
         */
        _unbindEvents: function() {

            var el = $(this.element),
                ns = this.eventNamespace;

            el.off(ns);

            return true;
        }
    });
})(jQuery);
