from odoo import api, fields, models, _

class VehicleAsset(models.Model):
    _name = "asset.vehicle"
    _description = "Asset Kendaraan"
    _rec_name = "license_plate"

    license_plate = fields.Char(
        string='Nomor Polisi',
        required=True,
        tracking=True
    )
    brand = fields.Char(string="Merk", required=True, tracking=True)
    model = fields.Char(string="Model Kendaraan", required=True, tracking=True)
    vin_number = fields.Char(string="Nomor Rangka", tracking=True)
    engine_number = fields.Char(string="Nomor Mesin", tracking=True)
    year = fields.Integer(string="Tahun Pembuatan")
    purchase_date = fields.Date(string="Tanggal Pembelian")
    purchase_value = fields.Float(string="Nilai Perolehan")
    responsible_id = fields.Many2one(
        'res.partner',
        string="Penanggung Jawab",
        tracking=True
    )
    location_id = fields.Many2one(
        'stock.location',
        string="Lokasi Kendaraan"
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        readonly=True,
        default=lambda self: self.env.company
    )
    state = fields.Selection([
        ('active', 'Aktif'),
        ('maintenance', 'Perawatan'),
        ('sold', 'Dijual'),
        ('scrap', 'Dibuang'),
    ], string="Status", default="active", tracking=True)
