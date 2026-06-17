import logging
from datetime import datetime, time

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class TrainingCenterLessonReportWizard(models.TransientModel):
    """Wizard for lesson report filters."""

    _name = 'training.center.lesson.report.wizard'
    _description = 'Lesson report wizard'

    teacher_ids = fields.Many2many(
        comodel_name='training.center.teacher',
        relation='tc_lesson_report_teacher_rel',
        column1='wizard_id',
        column2='teacher_id',
        string='Teachers',
    )

    student_ids = fields.Many2many(
        comodel_name='training.center.student',
        relation='tc_lesson_report_student_rel',
        column1='wizard_id',
        column2='student_id',
        string='Students',
    )

    date_from = fields.Date(
        string='Date From',
    )

    date_to = fields.Date(
        string='Date To',
    )

    only_done = fields.Boolean(
        string='Only Completed Lessons',
    )

    subject_id = fields.Many2one(
        comodel_name='training.center.subject',
        string='Subject',
    )

    @api.model
    def default_get(self, fields_list):
        """Fill students or teachers from selected records."""
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'training.center.student' and active_ids:
            res['student_ids'] = [(6, 0, active_ids)]

        if active_model == 'training.center.teacher' and active_ids:
            res['teacher_ids'] = [(6, 0, active_ids)]

        return res

    def action_show_lessons(self):
        """Open lessons by selected filter values."""
        self.ensure_one()

        domain = []

        if self.teacher_ids:
            domain.append(('teacher_id', 'in', self.teacher_ids.ids))

        if self.student_ids:
            domain.append(('student_id', 'in', self.student_ids.ids))

        if self.date_from:
            date_from = datetime.combine(self.date_from, time.min)
            domain.append(('planned_datetime', '>=', fields.Datetime.to_string(date_from)))

        if self.date_to:
            date_to = datetime.combine(self.date_to, time.max)
            domain.append(('planned_datetime', '<=', fields.Datetime.to_string(date_to)))

        if self.only_done:
            domain.append(('status', '=', 'done'))

        if self.subject_id:
            domain.append(('subject_id', '=', self.subject_id.id))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Lesson Report'),
            'res_model': 'training.center.lesson',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'create': False,
            },
        }
