from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from ..const import EDUCATION_LEVEL_LIST


class TrainingCenterPersonInfo(models.AbstractModel):
    """Common medical fields for teachers and students."""

    _name = 'training.center.person.info'
    _description = 'Medical information'

    education_level = fields.Selection(
        selection=EDUCATION_LEVEL_LIST,
        string='Education Level',
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
