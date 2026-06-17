import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class TrainingCenterMassReassignTeacherWizard(models.TransientModel):
    """Wizard to change main teacher for many students."""

    _name = 'training.center.mass.reassign.teacher.wizard'
    _description = 'Mass reassign teacher wizard'

    new_teacher_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='New Teacher',
        required=True,
    )

    change_date = fields.Date(
        string='Change Date',
        default=fields.Date.today,
    )

    def action_reassign_teacher(self):
        """Set new teacher and add history lines."""
        students = self.env['training.center.student'].browse(self.env.context.get('active_ids', []))

        for wizard in self:
            for student in students:
                active_histories = self.env['training.center.teacher.assignment.history'].search(
                    [
                        ('student_id', '=', student.id),
                        ('active', '=', True),
                    ]
                )

                active_histories.write(
                    {
                        'active': False,
                        'teacher_change_date': wizard.change_date,
                    }
                )

                self.env['training.center.teacher.assignment.history'].create(
                    {
                        'student_id': student.id,
                        'teacher_id': wizard.new_teacher_id.id,
                        'assignment_date': wizard.change_date,
                        'active': True,
                    }
                )

                student.personal_teacher_id = wizard.new_teacher_id

        return {'type': 'ir.actions.act_window_close'}
