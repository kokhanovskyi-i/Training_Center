import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class HrHospitalPatient(models.Model):
    """Keep patient data and personal doctor."""

    _name = 'hr.hospital.patient'
    _description = 'Hospital patient'
    _inherit = ['hospital.medic.info']

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

    personal_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Personal Doctor',
    )

    doctor_history_ids = fields.One2many(
        comodel_name='hospital.doctor.history',
        inverse_name='patient_id',
        string='Personal Doctor History',
    )

    insurance_policy_number = fields.Char(
        string='Insurance Policy Number',
        size=20,
    )

    appointment_count = fields.Integer(
        string='Appointments',
        compute='_compute_appointment_count',
    )

    @api.depends()
    def _compute_appointment_count(self):
        """Count visits of the patient."""
        for patient in self:
            patient.appointment_count = self.env['hr.hospital.appointment'].search_count(
                [
                    ('patient_id', '=', patient.id),
                ]
            )

    def action_view_appointments(self):
        """Open visits of this patient."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Patient Visits'),
            'res_model': 'hr.hospital.appointment',
            'view_mode': 'list,form,calendar,pivot,graph',
            'domain': [('patient_id', '=', self.id)],
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.personal_doctor_id.id,
            },
        }

    def action_create_appointment(self):
        """Open new visit form with this patient already filled."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Visit'),
            'res_model': 'hr.hospital.appointment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_patient_id': self.id,
                'default_doctor_id': self.personal_doctor_id.id,
                'default_status': 'planned',
                'default_planned_datetime': fields.Datetime.to_string(fields.Datetime.now()),
            },
        }
