from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
import io, zipfile


class PettyCashOut(models.Model):
    _name = "petty.cash.out"
    _description = "Petty Cash Out"
    # _inherit = 'ir.actions.report'
    _order = "date desc, id desc"

    name = fields.Char(string="Voucher Name", default="New", readonly=True, copy=False)
    date = fields.Date(string="Date", default=fields.Date.context_today, required=True)
    source_account_id = fields.Many2one(
        "account.account", string="Source of Fund (Cash)",
        domain=[("code", "=", "101501")], required=True
    )
    line_ids = fields.One2many("petty.cash.out.line", "out_id", string="List of Expense")
    amount_total = fields.Monetary(string="Total Amount", compute="_compute_total", store=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id.id, required=True
    )
    notes = fields.Text(string="Notes")
    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ], default="draft", tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )

    reject_reason = fields.Text(readonly=True)

    @api.depends("line_ids.amount")
    def _compute_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped("amount"))

    def _generate_voucher_number(self):
        today = datetime.today()
        year = today.strftime("%y")
        month = today.strftime("%m")
        prefix = f"AI/CO/{year}/{month}/"

        last_rec = self.search([("name", "like", prefix)], order="id desc", limit=1)
        if last_rec and last_rec.name:
            last_number = int(last_rec.name.split("/")[-1])
            new_number = f"{last_number + 1:03d}"
        else:
            new_number = "001"

        return prefix + new_number

    def action_submit(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Add at least one expense line."))
            if rec.name == "New":
                rec.name = rec._generate_voucher_number()
            rec.state = "submitted"

    def _make_move_vals(self):
        self.ensure_one()
        lines = []
        # debit per baris expense
        for l in self.line_ids:
            lines.append((0, 0, {
                "account_id": l.account_id.id,
                "debit": l.amount,
                "credit": 0.0,
                "currency_id": self.currency_id.id,
                "name": l.description or _("Petty Cash Out %s") % self.name,
            }))
        # credit akun sumber (total)
        lines.append((0, 0, {
            "account_id": self.source_account_id.id,
            "debit": 0.0,
            "credit": self.amount_total,
            "currency_id": self.currency_id.id,
            "name": _("Petty Cash Out %s") % self.name,
        }))
        return {"date": self.date, "ref": self.name, "line_ids": lines}

    def action_approve(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError(_("Only submitted records can be approved."))
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
        return self.env.ref('petty_cash_app.action_report_pc_out').report_action(self)


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

class PettyCashOutLine(models.Model):
    _name = "petty.cash.out.line"
    _description = "Petty Cash Out Line"

    out_id = fields.Many2one("petty.cash.out", string="Cash Out", ondelete="cascade")
    account_id = fields.Many2one(
        "account.account", string="COA (Expense)",
        domain=[("deprecated", "=", False)], required=True
    )
    description = fields.Char(string="Description")
    amount = fields.Monetary(string="Amount", required=True)
    currency_id = fields.Many2one(
        "res.currency", related="out_id.currency_id", store=True, readonly=True
    )