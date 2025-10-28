from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime

class PettyCashIn(models.Model):
    _name = "petty.cash.in"
    _description = "Petty Cash In"
    _order = "date desc, id desc"

    name = fields.Char(string="Voucher No.", default="New", readonly=True, copy=False)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    transfer_account_id = fields.Many2one(
        "account.account", string="Transfer From (Credit)",
        domain=[("deprecated", "=", False)], required=True
    )
    received_account_id = fields.Many2one(
        "account.account", string="To",
        domain=[("code", "=", "101501")], required=True
    )
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        default=lambda self: self.env.company.currency_id.id, required=True
    )
    notes = fields.Text(string="Notes")

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)

    reject_reason = fields.Text(readonly=True)

    def action_new(self):
        self.write({"state": "draft"})

    def _generate_voucher_number(self):
        today = datetime.today()
        year = today.strftime("%y")
        month = today.strftime("%m")
        prefix = f"AI/CI/{year}/{month}/"

        last_rec = self.search([("name", "like", prefix)], order="id desc", limit=1)
        if last_rec and last_rec.name:
            last_number = int(last_rec.name.split("/")[-1])
            new_number = f"{last_number + 1:03d}"
        else:
            new_number = "001"

        return prefix + new_number

    def create(self, vals):
        return super(PettyCashIn, self).create(vals)

    def action_submit(self):
        for rec in self:
            if rec.amount <= 0:
                raise UserError(_("Amount must be positive."))
            if rec.name == "New":
                rec.name = rec._generate_voucher_number()

            rec.state = "submitted"

    def _make_move_vals(self):
        self.ensure_one()
        return {
            "date": self.date,
            "ref": self.name,
            "line_ids": [
                (0, 0, {
                    "account_id": self.received_account_id.id,
                    "debit": self.amount,
                    "credit": 0.0,
                    "currency_id": self.currency_id.id,
                    "name": _("Petty Cash In %s") % self.name,
                }),
                (0, 0, {
                    "account_id": self.transfer_account_id.id,
                    "debit": 0.0,
                    "credit": self.amount,
                    "currency_id": self.currency_id.id,
                    "name": _("Petty Cash In %s") % self.name,
                }),
            ],
        }

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only submitted records can be approved."))

            # Tidak perlu generate nomor di sini, karena sudah saat submit
            move = self.env["account.move"].sudo().create(rec._make_move_vals())
            move.action_post()
            rec.state = "approved"

    def action_reject(self, reason=False):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only submitted records can be rejected."))
            rec.state = "rejected"
            rec.reject_reason = reason or False

    def action_print(self):
        return self.env.ref('petty_cash_app.action_report_pc_in').report_action(self)

    def open_approval_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Approve / Reject",
            "res_model": "petty.cash.approval.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_res_model": self._name,
                "default_res_id": self.id,
            },
        }
