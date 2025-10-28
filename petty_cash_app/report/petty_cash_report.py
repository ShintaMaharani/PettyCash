from odoo import models, api
import io, zipfile

class ReportPCOut(models.AbstractModel):
    _name = 'report_petty_cash_out'
    _description = 'Petty Cash Out Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['petty.cash.out'].browse(docids)
        return {
            'docs': docs,
            'doc_ids': docids,
            'doc_model': 'petty.cash.out',
        }

class PettyCashReport(models.Model):
    _name = 'petty.cash.report'
    _description = 'Petty Cash Report'


class IrActionsReportCustom(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """Cetak beberapa dokumen menjadi beberapa file PDF terpisah (dalam ZIP)."""
        if self.report_name == 'petty_cash_app.report_petty_cash_out' and len(res_ids) > 1:
            pdfs = []
            for rid in res_ids:
                pdf, _ = super()._render_qweb_pdf(report_ref, res_ids=[rid], data=data)
                record = self.env['petty.cash.out'].browse(rid)
                pdfs.append((f"{record.name or 'Petty_Cash'}.pdf", pdf))

            # Buat ZIP berisi semua PDF
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, pdf in pdfs:
                    zipf.writestr(filename, pdf)
            buf.seek(0)
            return buf.read(), 'zip'

        # Default behavior (1 dokumen = 1 file PDF)
        return super()._render_qweb_pdf(report_ref, res_ids, data)

