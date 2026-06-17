from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrHospitalDiseaseReportWizard(models.TransientModel):
    """Wizard for report by diseases and visits."""

    _name = 'disease.report.wizard'
    _description = 'Disease Report Wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
    )

    disease_ids = fields.Many2many(
        comodel_name='hr.hospital.disease',
        string='Diseases',
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
        """Fill doctors automatically when wizard is opened from doctors."""
        result = super().default_get(fields_list)

        if self.env.context.get('active_model') == 'hr.hospital.doctor':
            active_ids = self.env.context.get('active_ids', [])
            if active_ids:
                result['doctor_ids'] = [(6, 0, active_ids)]

        return result

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Check that start date is not after end date."""
        for wizard in self:
            if wizard.date_from and wizard.date_to and wizard.date_from > wizard.date_to:
                raise ValidationError(_('Date From cannot be later than Date To.'))

    def action_show_report(self):
        """Open visits by selected doctors, diseases and dates."""
        self.ensure_one()

        domain = []

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.disease_ids:
            domain.append(('disease_id', 'in', self.disease_ids.ids))

        if self.date_from:
            date_from = datetime.combine(self.date_from, time.min)
            domain.append(('planned_datetime', '>=', fields.Datetime.to_string(date_from)))

        if self.date_to:
            date_to = datetime.combine(self.date_to, time.max)
            domain.append(('planned_datetime', '<=', fields.Datetime.to_string(date_to)))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Disease Report'),
            'res_model': 'hr.hospital.appointment',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'group_by': 'disease_id',
                'create': False,
            },
        }
