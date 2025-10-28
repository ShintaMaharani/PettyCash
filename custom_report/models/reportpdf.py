from odoo import api, models
from odoo.exceptions import UserError

class FinancialReportCustom(models.AbstractModel):
    _name = 'report.custom_report.report_financial'
    _inherit = 'report.base_accounting_kit.report_financial'  # inherit dari report asli
    _description = 'Custom Financial Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Override method asli untuk ubah tampilan format"""
        if not data or not data.get('form'):
            raise UserError("Data laporan tidak ditemukan.")

        # ambil fungsi asli dari base_accounting_kit
        original_values = super(FinancialReportCustom, self)._get_report_values(docids, data)

        # salin data asli
        report_lines = original_values.get('report_lines', [])
        journal_items = original_values.get('journal_items', [])
        currency = self.env.company.currency_id

        # modifikasi data (contoh rounding dan set level)
        def set_report_level(item):
            if not item.get('parent'):
                return 1
            return 2

        for item in report_lines:
            item['balance'] = round(item.get('balance', 0.0), 2)
            if not item.get('parent'):
                item['level'] = 1
            else:
                item['level'] = set_report_level(item)

        data.update({
            'currency': currency,
            'report_lines': report_lines,
            'journal_items': journal_items,
        })

        return {
            'doc_ids': docids,
            'doc_model': 'financial.report',
            'data': data,
            'report_lines': report_lines,
            'currency': currency,
        }

    # Fungsi untuk memanggil report dari controller atau wizard
    def financial_report(self, data):
        """Custom action report"""
        return self.env.ref('custom_report.financial_report_pdf').report_action(self, data=data)
