from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TrainingCenterSubjectReportWizard(models.TransientModel):
    """Wizard for report by subjects and lessons."""

    _name = 'training.center.subject.report.wizard'
    _description = 'Subject Report Wizard'

    teacher_ids = fields.Many2many(
        comodel_name='training.center.teacher',
        relation='tc_subject_report_teacher_rel',
        column1='wizard_id',
        column2='teacher_id',
        string='Teachers',
    )

    subject_ids = fields.Many2many(
        comodel_name='training.center.subject',
        relation='tc_subject_report_subject_rel',
        column1='wizard_id',
        column2='subject_id',
        string='Subjects',
    )

    date_from = fields.Date(
        string='Date From',
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )

    date_to = fields.Date(
        string='Date To',
        required=True,
        default=lambda self: fields.Date.context_today(self) + relativedelta(day=31),
    )

    @api.model
    def default_get(self, fields_list):
        """Fill teachers automatically when wizard is opened from teachers."""
        result = super().default_get(fields_list)

        if self.env.context.get('active_model') == 'training.center.teacher':
            active_ids = self.env.context.get('active_ids', [])
            if active_ids:
                result['teacher_ids'] = [(6, 0, active_ids)]

        return result

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Check that start date is not after end date."""
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise ValidationError(_('Date From cannot be later than Date To.'))

    def action_show_report(self):
        """Open lessons by selected teachers, subjects and dates."""
        self.ensure_one()

        domain = []

        if self.teacher_ids:
            domain.append(('teacher_id', 'in', self.teacher_ids.ids))

        if self.subject_ids:
            domain.append(('subject_id', 'in', self.subject_ids.ids))

        if self.date_from:
            date_from = datetime.combine(self.date_from, time.min)
            domain.append(('planned_datetime', '>=', fields.Datetime.to_string(date_from)))

        if self.date_to:
            date_to = datetime.combine(self.date_to, time.max)
            domain.append(('planned_datetime', '<=', fields.Datetime.to_string(date_to)))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Subject Report'),
            'res_model': 'training.center.lesson',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'group_by': 'subject_id',
                'create': False,
            },
        }
