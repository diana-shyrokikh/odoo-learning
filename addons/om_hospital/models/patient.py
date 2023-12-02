from datetime import date
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


# Configure the logging module
logging.basicConfig(
    level=logging.INFO,  # Set the logging level according to your needs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _description = "Hospital Patient"
    _rec_name = "name"

    GENDERS = [
        ("male", "Male"),
        ("female", "Female")
    ]
    MARITAL_STATUSES = [
        ("married", "Married"),
        ("single", "Single"),

    ]

    name = fields.Char(
        string="Name", tracking=True
    )
    ref = fields.Char(
        string="Reference",
        tracking=True,
        default="HSP001"
    )
    date_of_birth = fields.Date(
        string="Date of Birth", tracking=True
    )
    age = fields.Integer(
        string="Age",
        tracking=True,
        compute="_compute_age",
        store=True
    )
    gender = fields.Selection(
        GENDERS, string="Gender", tracking=True
    )
    active = fields.Boolean(
        string="Active", default=True, tracking=True
    )
    appointment_id = fields.Many2one(
        "hospital.appointment", string="Appointments"
    )
    image = fields.Image(string="Image")
    tag_ids = fields.Many2many(
        "patient.tag",
        string="Tags"
    )
    appointment_count = fields.Integer(
        string="Appointment Count",
        compute="_compute_appointment_count",
        store=True
    )
    appointment_ids = fields.One2many(
        "hospital.appointment",
        "patient_id",
        string="Appointments"
    )
    parent = fields.Char(string="Parent")
    marital_status = fields.Selection(
        MARITAL_STATUSES,
        string="Marital Status",
        tracking=True
    )
    partner_name = fields.Char(string="Partner Name")

    @api.depends("appointment_ids")
    def _compute_appointment_count(self):
        for patient in self:
            patient.appointment_count = self.env["hospital.appointment"].search_count([(
                "patient_id", "=", patient.id
            )])

    @api.constrains("date_of_birth")
    def _check_date_of_birth(self):
        for patient in self:
            if (
                    patient.date_of_birth
                    and
                    patient.date_of_birth > fields.Date.today()
            ):
                raise ValidationError(_(
                    "The entered date of birth is not acceptable!"
                ))

    @api.depends('date_of_birth')
    def _compute_age(self):
        for patient in self:
            if patient.date_of_birth:
                date_of_birth = patient.date_of_birth
                today = date.today()
                age = (today.year
                       - date_of_birth.year
                       - ((today.month, today.day)
                          < (date_of_birth.month, date_of_birth.day)))
                patient.age = age
            else:
                patient.age = 0

    @api.model
    def create(self, vals):
        print("Create")
        logging.info(f"{vals}")
        vals["ref"] = self.env["ir.sequence"].next_by_code(
            "hospital.patient"
        )
        return super(HospitalPatient, self).create(vals)

    def write(self, vals):
        print("Write")
        logging.info(f"{vals}")
        vals["ref"] = self.env["ir.sequence"].next_by_code(
            "hospital.patient"
        )
        return super().write(vals)

    def name_get(self):
        return [
            (patient.id, f"{patient.ref} {patient.name}")
            for patient in self
        ]

    #
    # @api.model
    # def print_report(self, *args, **kwargs):
    #     return self.env.ref('om_hospital.action_report_custom_template').report_action(self)
