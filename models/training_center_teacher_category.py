from odoo import fields, models


class TrainingCenterTeacherCategory(models.Model):
    """Keep teacher categories and their order."""

    _name = 'training.center.teacher.category'
    _description = 'Teacher category'
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

    teacher_ids = fields.One2many(
        comodel_name='training.center.teacher',
        inverse_name='category_id',
        string='Teachers',
    )

    _name_unique = models.Constraint(
        'unique (name)',
        'Teacher category name must be unique.',
    )
