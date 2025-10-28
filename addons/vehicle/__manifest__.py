{
    'name': 'Custom Modul - Asset Kendaraan',
    'version': '1.0',
    'summary': 'Manajemen Asset Kendaraan',
    'sequence': 10,
    'category': 'Assets',
    'author': 'Shinta Maharani',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_vehicle_views.xml',
        'data/security.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
