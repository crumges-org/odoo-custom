/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.PortalTimesheetForm = publicWidget.Widget.extend({
    selector: '#timesheet_form',
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
        var self = this;
        var projectId = $(ev.currentTarget).val();
        var $taskSelect = this.$('#task_id');

        // Clear existing options
        $taskSelect.html('<option value="">Select Task...</option>');

        if (projectId) {
            rpc('/timesheet/project_tasks', {
                project_id: projectId,
            }).then(function (tasks) {
                if (tasks && tasks.length) {
                    tasks.forEach(function (task) {
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
                $taskSelect.append('<option value="">Error fetching tasks</option>');
            });
        } else {
            $taskSelect.prop('disabled', true);
        }
    },
});
