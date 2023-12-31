from datetime import date
from dateutil import relativedelta
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
        store=True,
        inverse="_inverse_compute_age",
        search="_search_age",
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
    is_birthday = fields.Boolean(
        string="Birthday?",
        compute="_compute_is_birthday"
    )
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    @api.depends("appointment_ids")
    def _compute_appointment_count(self):
        appointment_group = self.env["hospital.appointment"].read_group(
                domain=[('state', '=', 'done')],
                fields=["patient_id"],
                groupby=["patient_id"],
        )

        for appointment in appointment_group:
            patient_id = appointment.get("patient_id")[0]
            patient_rec = self.browse(patient_id)

            patient_rec.appointment_count = appointment["patient_id_count"]

            self -= patient_rec

        self.appointment_count = 0

        # for patient in self:
        #     count = self.env["hospital.appointment"].search_count([(
        #         "patient_id", "=", patient.id
        #     )])
        #
        #     patient.appointment_count = count

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

    @api.depends("age")
    def _inverse_compute_age(self):
        today = date.today()
        for patient in self:
            patient.date_of_birth = today - relativedelta.relativedelta(
                years=patient.age
            )
            
    def _search_age(self, operator, value):
        date_of_birth = date.today() - relativedelta.relativedelta(
                years=value
        )
        start_of_year = date_of_birth.replace(day=1, month=1)
        end_of_year = date_of_birth.replace(day=31, month=12)

        return [
            ("date_of_birth", ">=", start_of_year),
            ("date_of_birth", "<=", end_of_year),
        ]


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

    @api.ondelete(at_uninstall=False)
    def _check_appointments(self):
        for patient in self:
            if patient.appointment_ids:
                raise ValidationError(_(
                    "You cannot delete a patient with appointments!"
                ))

    def action_test(self):
        print("Clicked")
        return

    def action_done(self):
        for patient in self:
            for appointment in patient.appointment_ids:
                if appointment.state == "in_consultation":
                    appointment.state = "done"

    @api.depends("date_of_birth")
    def _compute_is_birthday(self):
        for patient in self:
            is_birthday = False

            if patient.date_of_birth:
                today = date.today()

                if (
                    today.day == patient.date_of_birth.day
                    and
                    today.month == patient.date_of_birth.month
                ):
                    is_birthday = True

            patient.is_birthday = is_birthday

    def action_view_appointments(self):
        return {
            "name": _("Appointments"),
            "res_model": "hospital.appointment",
            "view_mode": "list,form,calendar,activity",
            "context": {"default_patient_id": self.id},
            "domain": [("patient_id", "=", self.id)],
            "target": "current",
            "type": "ir.actions.act_window",
        }

    #
    # @api.model
    # def print_report(self, *args, **kwargs):
    #     return self.env.ref('om_hospital.action_report_custom_template').report_action(self)
