import logging
from datetime import datetime, time

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class VisitReportWizard(models.TransientModel):
    """Wizard for visit report filters."""

    _name = 'visit.report.wizard'
    _description = 'Visit report wizard'

    doctor_ids = fields.Many2many(
        comodel_name='hr.hospital.doctor',
        string='Doctors',
    )

    patient_ids = fields.Many2many(
        comodel_name='hr.hospital.patient',
        string='Patients',
    )

    date_from = fields.Date(
        string='Date From',
    )

    date_to = fields.Date(
        string='Date To',
    )

    only_done = fields.Boolean(
        string='Only Completed Visits',
    )

    disease_id = fields.Many2one(
        comodel_name='hr.hospital.disease',
        string='Disease',
    )

    @api.model
    def default_get(self, fields_list):
        """Fill patients or doctors from selected records."""
        res = super().default_get(fields_list)

        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids', [])

        if active_model == 'hr.hospital.patient' and active_ids:
            res['patient_ids'] = [(6, 0, active_ids)]

        if active_model == 'hr.hospital.doctor' and active_ids:
            res['doctor_ids'] = [(6, 0, active_ids)]

        return res

    def action_show_visits(self):
        """Open visits by selected filter values."""
        self.ensure_one()

        domain = []

        if self.doctor_ids:
            domain.append(('doctor_id', 'in', self.doctor_ids.ids))

        if self.patient_ids:
            domain.append(('patient_id', 'in', self.patient_ids.ids))

        if self.date_from:
            date_from = datetime.combine(self.date_from, time.min)
            domain.append(('planned_datetime', '>=', fields.Datetime.to_string(date_from)))

        if self.date_to:
            date_to = datetime.combine(self.date_to, time.max)
            domain.append(('planned_datetime', '<=', fields.Datetime.to_string(date_to)))

        if self.only_done:
            domain.append(('status', '=', 'done'))

        if self.disease_id:
            domain.append(('disease_id', '=', self.disease_id.id))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Visit Report'),
            'res_model': 'hr.hospital.appointment',
            'view_mode': 'list,form',
            'domain': domain,
            'context': {
                'create': False,
            },
        }
