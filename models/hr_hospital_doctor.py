import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrHospitalDoctor(models.Model):
    """Keep doctor data, category, mentor and interns."""

    _name = 'hr.hospital.doctor'
    _description = 'Hospital doctor'
    _inherit = ['hospital.medic.info']

    name = fields.Char(
        string='Name',
        required=True,
    )

    specialty = fields.Char(
        string='Specialty',
        required=True,
    )

    category_id = fields.Many2one(
        comodel_name='hospital.doctor.category',
        string='Category',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='System User',
    )

    is_intern = fields.Boolean(
        string='Doctor Is Intern',
        compute='_compute_is_intern',
        store=True,
    )

    mentor_id = fields.Many2one(
        comodel_name='hr.hospital.doctor',
        string='Mentor',
        domain=[('is_intern', '=', False)],
    )

    intern_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='mentor_id',
        string='Interns',
        readonly=True,
    )

    intern_names = fields.Char(
        string='Intern Names',
        compute='_compute_intern_names',
    )

    appointment_ids = fields.One2many(
        comodel_name='hr.hospital.appointment',
        inverse_name='doctor_id',
        string='Visits',
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
    def _compute_is_intern(self):
        """Set intern flag by doctor category."""
        intern_category = self.env.ref(
            'hr_hospital.doctor_category_intern',
            raise_if_not_found=False,
        )

        for doctor in self:
            doctor.is_intern = bool(doctor.category_id and intern_category and doctor.category_id == intern_category)

    @api.constrains('mentor_id')
    def _check_mentor_is_not_intern(self):
        """Do not allow intern doctor as mentor."""
        for doctor in self:
            if doctor.mentor_id and doctor.mentor_id.is_intern:
                raise ValidationError(_('Mentor cannot be an intern.'))

    def action_create_appointment(self):
        """Open new visit form with this doctor already filled."""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Visit'),
            'res_model': 'hr.hospital.appointment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_doctor_id': self.id,
                'default_status': 'planned',
                'default_planned_datetime': fields.Datetime.to_string(fields.Datetime.now()),
            },
        }

    def _get_report_appointments(self):
        """Return doctor visits from newest to oldest."""
        self.ensure_one()

        return self.env['hr.hospital.appointment'].search(
            [('doctor_id', '=', self.id)],
            order='planned_datetime desc, id desc',
        )

    def _get_report_patients(self):
        """Return patients of this doctor for PDF report."""
        self.ensure_one()

        appointment_patients = self._get_report_appointments().mapped('patient_id')
        personal_patients = self.env['hr.hospital.patient'].search(
            [
                ('personal_doctor_id', '=', self.id),
            ]
        )

        return (appointment_patients | personal_patients).sorted('name')

    def _get_appointment_status_label(self, status):
        """Return status label for visit status value."""
        status_labels = dict(self.env['hr.hospital.appointment']._fields['status'].selection)
        return status_labels.get(status, status)

    def _get_appointment_status_style(self, status):
        """Return simple style for status in report."""
        status_styles = {
            'planned': 'background-color: #fff3cd; color: #856404; font-weight: bold;',
            'done': 'background-color: #d4edda; color: #155724; font-weight: bold;',
            'cancelled': 'background-color: #f8d7da; color: #721c24; font-weight: bold;',
        }
        return status_styles.get(status, '')

    @api.depends('intern_ids.name')
    def _compute_intern_names(self):
        """Make intern names text for kanban card."""
        for doctor in self:
            doctor.intern_names = ', '.join(doctor.intern_ids.mapped('name'))
