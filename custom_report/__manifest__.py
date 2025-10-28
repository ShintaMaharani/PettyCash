{
    'name': 'Custom Financial Reports',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Custom Profit & Loss and Balance Sheet Reports',
    'depends': ['base_accounting_kit'],  # inherit dari modul aslinya
    'data': [
        'report/report_action.xml',
        'report/report_financial.xml',
    ],
    'installable': True,
    'application': False,
}
