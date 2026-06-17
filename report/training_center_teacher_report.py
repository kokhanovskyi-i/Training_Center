from odoo import api, fields, models


class ReportTrainingCenterTeacher(models.AbstractModel):
    """Report model for teacher PDF report."""

    _name = 'report.training_center.report_teacher_document'
    _description = 'Teacher Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Return data needed for teacher report."""
        teachers = self.env['training.center.teacher'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'training.center.teacher',
            'docs': teachers,
            'print_datetime': fields.Datetime.now(),
        }
