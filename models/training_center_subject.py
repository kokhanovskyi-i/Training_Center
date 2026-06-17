import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TrainingCenterSubject(models.Model):
    """Keep subjects in a simple parent and child structure."""

    _name = 'training.center.subject'
    _description = 'Subject'
    _parent_name = 'parent_id'
    _parent_store = True
    _order = 'parent_path, name'

    code = fields.Char(
        string='Code',
        required=True,
    )

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        recursive=True,
    )

    parent_id = fields.Many2one(
        comodel_name='training.center.subject',
        string='Parent Subject',
        index=True,
        ondelete='restrict',
    )

    child_ids = fields.One2many(
        comodel_name='training.center.subject',
        inverse_name='parent_id',
        string='Child Subjects',
    )

    parent_path = fields.Char(
        index=True,
    )

    @api.constrains('parent_id')
    def _check_parent_id(self):
        """Check that subject hierarchy has no recursion."""
        for subject in self:
            if subject._has_cycle():
                raise ValidationError(_('Subject hierarchy cannot be recursive.'))

    @api.depends('name', 'parent_id.display_name')
    def _compute_display_name(self):
        """Set full name for subject with parent names."""
        for subject in self:
            subject.display_name = subject._get_complete_name()

    def _get_complete_name(self):
        """Return subject name together with its parents."""
        self.ensure_one()

        names = []
        current = self

        while current:
            names.append(current.name or '')
            current = current.parent_id

        return ' / '.join(reversed(names))
