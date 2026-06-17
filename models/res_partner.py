from odoo import fields, models


class ResPartner(models.Model):
    "Add training center fields to contacts."

    _inherit = 'res.partner'

    training_center_role = fields.Selection(
        selection=[
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('company', 'Company'),
            ('other', 'Other'),
        ],
        string='Training Center Role',
    )
