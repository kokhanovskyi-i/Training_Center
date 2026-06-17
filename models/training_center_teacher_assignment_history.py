from odoo import _, api, fields, models


class TrainingCenterTeacherAssignmentHistory(models.Model):
    """Keep history of main teacher changes."""

    _name = 'training.center.teacher.assignment.history'
    _description = 'Main teacher history'
    _order = 'assignment_date desc, id desc'

    student_id = fields.Many2one(
        comodel_name='training.center.student',
        string='Student',
        required=True,
    )

    teacher_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='Teacher',
        required=True,
    )

    assignment_date = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today,
    )

    teacher_change_date = fields.Date(
        string='Teacher Change Date',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.onchange('assignment_date', 'teacher_change_date')
    def _onchange_teacher_change_date(self):
        """Show warning if change date is before assignment date."""
        if self.assignment_date and self.teacher_change_date and self.teacher_change_date < self.assignment_date:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Teacher change date cannot be earlier than assignment date.'),
                }
            }

        return None

    @api.depends(
        'student_id.name',
        'teacher_id.name',
        'teacher_id.category_id.name',
        'assignment_date',
    )
    def _compute_display_name(self):
        """Make name for history record from student and teacher."""
        for record in self:
            student_name = record.student_id.name or ''
            teacher_name = record.teacher_id.name or ''
            category_name = record.teacher_id.category_id.name or ''
            assignment_date = record.assignment_date or ''

            record.display_name = f'{student_name} - {teacher_name} ({category_name}) {assignment_date}'
