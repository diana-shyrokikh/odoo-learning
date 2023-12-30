{
    "name": "Hospital Management",
    "version": "1.0.0",
    "category": "Hospital",
    "summary": "Hospital management system",
    "description": """Hospital management system""",
    "depends": [
        "mail",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",

        "data/patient_tag_data.xml",
        "data/hospital.patient.csv",
        "data/sequence_data.xml",

        "wizard/cancel_appointment_view.xml",

        "views/menu.xml",
        "views/patient_view.xml",
        "views/female_patient_view.xml",
        "views/appointment_view.xml",
        "views/patient_tag_view.xml",
        "views/odoo_playground_view.xml",
        "views/res_config_settings.xml",
        "views/operation_view.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "application": True,
    "sequence": -100,
    "author": "Diashiro",
    "assets": {},
}
