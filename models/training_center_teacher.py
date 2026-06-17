import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TrainingCenterTeacher(models.Model):
    """Keep teacher data, category, mentor and assistants."""

    _name = 'training.center.teacher'
    _description = 'Training center teacher'
    _inherit = ['training.center.person.info']

    name = fields.Char(
        string='Name',
        required=True,
    )

    specialty = fields.Char(
        string='Specialty',
        required=True,
    )

    category_id = fields.Many2one(
        comodel_name='training.center.teacher.category',
        string='Category',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
    )

    is_assistant = fields.Boolean(
        string='Teacher Is Assistant',
        compute='_compute_is_assistant',
        store=True,
    )

    mentor_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='Mentor',
        domain=[('is_assistant', '=', False)],
    )

    assistant_ids = fields.One2many(
        comodel_name='training.center.teacher',
        inverse_name='mentor_id',
        string='Assistants',
        readonly=True,
    )

    assistant_names = fields.Char(
        string='Assistant Names',
        compute='_compute_assistant_names',
    )

    lesson_ids = fields.One2many(
        comodel_name='training.center.lesson',
        inverse_name='teacher_id',
        string='Lessons',
        readonly=True,
    )

    email = fields.Char(
        string='Email',
        required=True,
    )

    phone = fields.Char(
        string='Phone',
        required=True,
    )

    @api.depends('category_id')
    def _compute_is_assistant(self):
        """Set assistant flag by teacher category."""
        assistant_category = self.env.ref(
            'training_center.teacher_category_assistant',
            raise_if_not_found=False,
        )

        for teacher in self:
            teacher.is_assistant = bool(
                teacher.category_id and assistant_category and teacher.category_id == assistant_category
            )

    @api.constrains('mentor_id')
    def _check_mentor_is_not_assistant(self):
        """Do not allow assistant teacher as mentor."""
        for teacher in self:
            if teacher.mentor_id and teacher.mentor_id.is_assistant:
                raise ValidationError(_('Mentor cannot be an assistant.'))

    def action_create_lesson(self):
        """Open new lesson form with this teacher already filled."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Lesson'),
            'res_model': 'training.center.lesson',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_teacher_id': self.id,
                'default_status': 'planned',
                'default_planned_datetime': fields.Datetime.to_string(fields.Datetime.now()),
            },
        }

    def _get_report_lessons(self):
        """Return teacher lessons from newest to oldest."""
        self.ensure_one()

        return self.env['training.center.lesson'].search(
            [('teacher_id', '=', self.id)],
            order='planned_datetime desc, id desc',
        )

    def _get_report_students(self):
        """Return students of this teacher for PDF report."""
        self.ensure_one()

        lesson_students = self._get_report_lessons().mapped('student_id')
        personal_students = self.env['training.center.student'].search(
            [
                ('personal_teacher_id', '=', self.id),
            ]
        )

        return (lesson_students | personal_students).sorted('name')

    def _get_lesson_status_label(self, status):
        """Return status label for lesson status value."""
        status_labels = dict(self.env['training.center.lesson']._fields['status'].selection)
        return status_labels.get(status, status)

    def _get_lesson_status_style(self, status):
        """Return simple style for status in report."""
        status_styles = {
            'planned': 'background-color: #fff3cd; color: #856404; font-weight: bold;',
            'done': 'background-color: #d4edda; color: #155724; font-weight: bold;',
            'cancelled': 'background-color: #f8d7da; color: #721c24; font-weight: bold;',
        }
        return status_styles.get(status, '')

    @api.depends('assistant_ids.name')
    def _compute_assistant_names(self):
        """Make assistant names text for kanban card."""
        for teacher in self:
            teacher.assistant_names = ', '.join(teacher.assistant_ids.mapped('name'))
