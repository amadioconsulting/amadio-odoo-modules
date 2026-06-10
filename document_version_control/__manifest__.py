{
    'name': 'Document Version Control',
    'version': '18.0.1.0.2',
    'summary': 'Attach versioned documents to any Odoo record — track revisions, view full history, and optionally require approval before a new version goes live.',
    'category': 'Document Management',
    'author': 'AMADIO',
    'website': 'https://amadio.io',
    'license': 'OPL-1',
    'depends': [
        'mail',
        'base',
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/document_version_views.xml",
    ],
    'installable': True,
    'application': False,
    'price': 49.00,
    'currency': 'EUR',
    'images': [
        'static/description/icon.png',
    ],
}
