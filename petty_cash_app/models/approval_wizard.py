from odoo import fields, models, _
from odoo.exceptions import UserError

class PettyCashApprovalWizard(models.TransientModel):
    _name = "petty.cash.approval.wizard"
    _description = "Petty Cash Approval Wizard"

    res_model = fields.Char(readonly=True)
    res_id = fields.Integer(readonly=True)
    decision = fields.Selection(
        [("approve", "Approve"), ("reject", "Reject")],
        required=True, default="approve"
    )
    reason = fields.Text(string="Reason")

    def action_confirm(self):
        self.ensure_one()
        if not self.res_model or not self.res_id:
            raise UserError(_("Missing target record."))
        rec = self.env[self.res_model].browse(self.res_id)
        if not rec.exists():
            raise UserError(_("Record not found."))

        if self.decision == "approve":
            rec.action_approve()
        else:
            rec.action_reject(reason=self.reason)

        return {"type": "ir.actions.act_window_close"}
