from odoo import fields, models


class HospitalDoctorCategory(models.Model):
    """Keep doctor categories and their order."""

    _name = 'hospital.doctor.category'
    _description = 'Doctor category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    doctor_ids = fields.One2many(
        comodel_name='hr.hospital.doctor',
        inverse_name='category_id',
        string='Doctors',
    )

    _name_unique = models.Constraint(
        'unique (name)',
        'Doctor category name must be unique.',
    )
