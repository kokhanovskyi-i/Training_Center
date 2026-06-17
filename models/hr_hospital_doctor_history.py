from odoo import _, api, fields, models


class HospitalDoctorHistory(models.Model):
    """Keep history of personal doctor changes."""

    _name = 'hospital.doctor.history'
    _description = 'Personal doctor history'
    _order = 'assignment_date desc, id desc'

    patient_id = fields.Many2one(
        comodel_name='hr.hospital.patient',
        string='Patient',
        required=True,
    )

    doctor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Doctor',
        required=True,
    )

    assignment_date = fields.Date(
        string='Assignment Date',
        required=True,
        default=fields.Date.today,
    )

    doctor_change_date = fields.Date(
        string='Doctor Change Date',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.onchange('assignment_date', 'doctor_change_date')
    def _onchange_doctor_change_date(self):
        """Show warning if change date is before assignment date."""
        if self.assignment_date and self.doctor_change_date and self.doctor_change_date < self.assignment_date:
            return {
                'warning': {
                    'title': _('Warning'),
                    'message': _('Doctor change date cannot be earlier than assignment date.'),
                }
            }

        return None

    @api.depends(
        'patient_id.name',
        'doctor_id.name',
        'doctor_id.category_id.name',
        'assignment_date',
    )
    def _compute_display_name(self):
        """Make name for history record from patient and doctor."""
        for record in self:
            patient_name = record.patient_id.name or ''
            doctor_name = record.doctor_id.name or ''
            category_name = record.doctor_id.category_id.name or ''
            assignment_date = record.assignment_date or ''

            record.display_name = f'{patient_name} - {doctor_name} ({category_name}) {assignment_date}'
