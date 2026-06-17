from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HospitalMedicInfo(models.AbstractModel):
    """Common medical fields for doctors and patients."""

    _name = 'hospital.medic.info'
    _description = 'Medical information'

    blood_type = fields.Selection(
        selection=[
            ('o_positive', 'O(I) Rh+'),
            ('o_negative', 'O(I) Rh-'),
            ('a_positive', 'A(II) Rh+'),
            ('a_negative', 'A(II) Rh-'),
            ('b_positive', 'B(III) Rh+'),
            ('b_negative', 'B(III) Rh-'),
            ('ab_positive', 'AB(IV) Rh+'),
            ('ab_negative', 'AB(IV) Rh-'),
        ],
        string='Blood Type',
    )

    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
        ],
        string='Gender',
    )

    birth_date = fields.Date(
        string='Birth Date',
    )

    age = fields.Integer(
        string='Age',
        compute='_compute_age',
    )

    @api.depends('birth_date')
    def _compute_age(self):
        """Calculate age from birth date."""
        today = fields.Date.today()

        for record in self:
            record.age = 0

            if record.birth_date:
                record.age = relativedelta(today, record.birth_date).years
