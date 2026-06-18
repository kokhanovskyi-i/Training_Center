import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TrainingCenterLesson(models.Model):
    """Keep lesson records for students and teachers."""

    _name = 'training.center.lesson'
    _description = 'Training center lesson'
    _rec_name = 'planned_datetime'
    _order = 'planned_datetime desc, id desc'

    status = fields.Selection(
        selection=[
            ('planned', 'Planned'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Lesson Status',
        default='planned',
        required=True,
    )

    planned_datetime = fields.Datetime(
        string='Planned Date and Time',
        default=fields.Datetime.now,
        required=True,
    )

    lesson_datetime = fields.Datetime(
        string='Lesson Date and Time',
    )

    teacher_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='Teacher',
        required=True,
    )

    student_id = fields.Many2one(
        comodel_name='training.center.student',
        string='Student',
        required=True,
    )

    summary = fields.Html(
        string='Summary',
    )

    subject_id = fields.Many2one(
        comodel_name='training.center.subject',
        string='Subject',
    )

    same_subject_lesson_count = fields.Integer(
        string='Same Subject Lessons',
        compute='_compute_same_subject_lesson_count',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    def write(self, vals):
        """Stop changes that are not allowed for completed lessons."""
        protected_fields = {
            'planned_datetime',
            'lesson_datetime',
            'teacher_id',
        }

        if protected_fields.intersection(vals):
            finished_lessons = self.filtered(lambda lesson: lesson.status == 'done')
            if finished_lessons:
                raise UserError(_('You cannot change date, time or teacher for a completed lesson.'))

        if vals.get('active') is False:
            finished_lessons = self.filtered(lambda lesson: lesson.status == 'done')
            if finished_lessons:
                raise UserError(_('You cannot archive completed lessons.'))

        return super().write(vals)

    def unlink(self):
        """Do not delete completed lessons, except for training center admin."""
        if self.env.user.has_group('training_center.group_training_center_admin'):
            return super().unlink()

        finished_lessons = self.filtered(lambda lesson: lesson.status == 'done')
        if finished_lessons:
            raise UserError(_('You cannot delete completed lessons.'))

        return super().unlink()

    @api.depends('subject_id')
    def _compute_same_subject_lesson_count(self):
        """Count lessons with the same subject."""
        for lesson in self:
            if lesson.subject_id:
                lesson.same_subject_lesson_count = self.search_count(
                    [
                        ('subject_id', '=', lesson.subject_id.id),
                    ]
                )
            else:
                lesson.same_subject_lesson_count = 0

    def action_view_same_subject_lessons(self):
        """Open lessons with the same subject as current lesson."""
        self.ensure_one()

        domain = [('id', '=', False)]
        context = {}

        if self.subject_id:
            domain = [('subject_id', '=', self.subject_id.id)]
            context = {
                'default_subject_id': self.subject_id.id,
            }

        return {
            'type': 'ir.actions.act_window',
            'name': _('Lessons With Same Subject'),
            'res_model': 'training.center.lesson',
            'view_mode': 'list,form',
            'domain': domain,
            'context': context,
        }

    def action_set_done(self):
        """Set status to done"""
        self.write({'status': 'done'})

    def action_set_cancelled(self):
        """Set status to cancelled"""
        self.write({'status': 'cancelled'})

    def action_set_planned(self):
        """Set status back to planned"""
        self.write({'status': 'planned'})
