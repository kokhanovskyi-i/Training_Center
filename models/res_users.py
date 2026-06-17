from odoo import fields, models


class ResUsers(models.Model):
    "Add training center profile links to users."

    _inherit = 'res.users'

    training_center_teacher_id = fields.Many2one(
        comodel_name='training.center.teacher',
        string='Teacher Profile',
    )

    training_center_student_id = fields.Many2one(
        comodel_name='training.center.student',
        string='Student Profile',
    )
