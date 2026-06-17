import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class MassReassignDoctorWizard(models.TransientModel):
    """Wizard to change personal doctor for many patients."""

    _name = 'mass.reassign.doctor.wizard'
    _description = 'Mass reassign doctor wizard'

    new_doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='New Doctor',
        required=True,
    )

    change_date = fields.Date(
        string='Change Date',
        default=fields.Date.today,
    )

    def action_reassign_doctor(self):
        """Set new doctor and add history lines."""
        patients = self.env['hr.hospital.patient'].browse(self.env.context.get('active_ids', []))

        for wizard in self:
            for patient in patients:
                active_histories = self.env['hospital.doctor.history'].search(
                    [
                        ('patient_id', '=', patient.id),
                        ('active', '=', True),
                    ]
                )

                active_histories.write(
                    {
                        'active': False,
                        'doctor_change_date': wizard.change_date,
                    }
                )

                self.env['hospital.doctor.history'].create(
                    {
                        'patient_id': patient.id,
                        'doctor_id': wizard.new_doctor_id.id,
                        'assignment_date': wizard.change_date,
                        'active': True,
                    }
                )

                patient.personal_doctor_id = wizard.new_doctor_id

        return {'type': 'ir.actions.act_window_close'}
