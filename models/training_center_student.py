import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class TrainingCenterStudent(models.Model):
    """Keep student data and main teacher."""

    _name = 'training.center.student'
    _description = 'Training center student'
    _inherit = ['training.center.person.info']

    name = fields.Char(
        string='Name',
        required=True,
    )

    email = fields.Char(
        string='Email',
    )

    phone = fields.Char(
        string='Phone',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
    )

    personal_teacher_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='Main Teacher',
    )

    teacher_history_ids = fields.One2many(
        comodel_name='training.center.teacher.assignment.history',
        inverse_name='student_id',
        string='Main Teacher History',
    )

    contract_number = fields.Char(
        string='Contract Number',
        size=20,
    )

    lesson_count = fields.Integer(
        string='Lessons',
        compute='_compute_lesson_count',
    )

    @api.depends()
    def _compute_lesson_count(self):
        """Count lessons of the student."""
        for student in self:
            student.lesson_count = self.env['training.center.lesson'].search_count(
                [
                    ('student_id', '=', student.id),
                ]
            )

    def action_view_lessons(self):
        """Open lessons of this student."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Lessons'),
            'res_model': 'training.center.lesson',
            'view_mode': 'list,form,calendar,pivot,graph',
            'domain': [('student_id', '=', self.id)],
            'context': {
                'default_student_id': self.id,
                'default_teacher_id': self.personal_teacher_id.id,
            },
        }

    def action_create_lesson(self):
        """Open new lesson form with this student already filled."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Lesson'),
            'res_model': 'training.center.lesson',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_student_id': self.id,
                'default_teacher_id': self.personal_teacher_id.id,
                'default_status': 'planned',
                'default_planned_datetime': fields.Datetime.to_string(fields.Datetime.now()),
            },
        }
