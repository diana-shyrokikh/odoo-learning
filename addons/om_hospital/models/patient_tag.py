from odoo import api, fields, models


class PatientTag(models.Model):
    _name = "patient.tag"
    _description = "Patient Tag"

    name = fields.Char(
        string="Name",
        required=True
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    color = fields.Integer(string="Color")
    color_2 = fields.Char(string="Color 2")
    sequence = fields.Integer(string="Sequence")

    _sql_constraints = [
        (
            "unique_tag_name",
            "unique (name, active)",
            "Name should be unique!"
        ),
        (
            "check_sequence",
            "check (sequence > 0)",
            "Sequence should be non zero positive number!"
        )
    ]
