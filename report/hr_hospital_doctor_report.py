from odoo import api, fields, models


class ReportHrHospitalDoctor(models.AbstractModel):
    """Report model for doctor PDF report."""

    _name = 'report.hr_hospital.report_doctor_document'
    _description = 'Doctor Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Return data needed for doctor report."""
        doctors = self.env['hr.hospital.doctor'].browse(docids)

        return {
            'doc_ids': docids,
            'doc_model': 'hr.hospital.doctor',
            'docs': doctors,
            'print_datetime': fields.Datetime.now(),
        }
