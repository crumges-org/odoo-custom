/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.PortalTimesheetForm = publicWidget.Widget.extend({
    selector: '#timesheet_form',
    // improved dependency management: declare jquery as a required lib for this widget.
    // Odoo will ensure it is loaded before 'start' is called.
    jsLibs: [
        '/web/static/src/legacy/js/libs/jquery.js',
    ],
    events: {
        'change #project_id': '_onProjectChange',
    },

    /**
     * @override
     */
    start: function () {
        return this._super.apply(this, arguments);
    },

    /**
     * On project change, fetch related tasks
     */
    _onProjectChange: function (ev) {
        var projectId = ev.target.value;

        // Use window.$ or this.$ (which uses the window.$ bound to the element)
        // With jsLibs loaded, window.$ should be safe.
        var $taskSelect = this.$('#task_id');

        // Clear existing options
        $taskSelect.empty().append('<option value="">Select Task...</option>');

        if (projectId) {
            $taskSelect.prop('disabled', true);

            rpc('/timesheet/project_tasks', {
                project_id: parseInt(projectId),
            }).then(function (tasks) {
                if ($taskSelect.length === 0) return;

                $taskSelect.empty().append('<option value="">Select Task...</option>');

                if (tasks && tasks.length) {
                    tasks.forEach(function (task) {
                        // Safe to use global jQuery now
                        const $ = window.jQuery;
                        $taskSelect.append(
                            $('<option>', {
                                value: task.id,
                                text: task.name
                            })
                        );
                    });
                    $taskSelect.prop('disabled', false);
                } else {
                    $taskSelect.append('<option value="">No tasks found</option>');
                    $taskSelect.prop('disabled', true);
                }
            }).catch(function (error) {
                console.error("Error fetching tasks:", error);
                if ($taskSelect.length > 0) {
                    $taskSelect.empty().append('<option value="">Error fetching tasks</option>');
                }
            });
        } else {
            $taskSelect.prop('disabled', true);
        }
    },
});

export default publicWidget.registry.PortalTimesheetForm;
