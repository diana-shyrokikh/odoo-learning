import random
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin",
    ]
    _description = "Hospital Appointment"
    _rec_name = "ref"
    _order = "id desc, appointment_time"

    PRIORITIES = [
        ("0", "Normal"),
        ("1", "Low"),
        ("2", "High"),
        ("3", "Very High"),
    ]
    STATES = [
        ("draft", "Draft"),
        ("in_consultation", "In Consultation"),
        ("done", "Done"),
        ("canceled", "Canceled"),
    ]

    patient_id = fields.Many2one(
        comodel_name="hospital.patient",
        string="Patient",
        ondelete="restrict",  # if any refers it's prohibited
        tracking=1,
    )
    appointment_time = fields.Datetime(
        string="Appointment time",
        default=fields.Datetime.now,
        tracking=2,
    )
    booking_date = fields.Date(
        string="Booking Date",
        default=fields.Date.context_today,
        tracking=True,
    )
    gender = fields.Selection(
        related="patient_id.gender"
    )
    ref = fields.Char(
        string="Reference",
        tracking=True,
        default="HSP001",
        help="Reference of the patient from patient record"
    )
    prescription = fields.Html(
        string="Prescription",
        tracking=True,
    )
    priority = fields.Selection(
        PRIORITIES,
        string="Priority",
        tracking=True,
    )
    state = fields.Selection(
        STATES,
        default="draft",
        required=True,
        string="State",
        tracking=True,
    )
    doctor_id = fields.Many2one(
        comodel_name="res.users",
        string="Doctor",
        tracking=True,
    )
    pharmacy_line_ids = fields.One2many(
        "appointment.pharmacy.lines",
        "appointment_id",
        string="Pharmacy Lines"
    )
    hide_sales_price = fields.Boolean(string="Hide Sales Price")
    operation_id = fields.Many2one(
        comodel_name="hospital.operation",
        string="Operation",
        tracking=True,
    )
    progress = fields.Integer(
        string="Progress",
        compute="_compute_progress"
    )
    duration = fields.Float(string="Duration")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id"
    )

    def unlink(self):
        for appointment in self:
            if appointment.state != "draft":
                raise ValidationError(_(
                    "You can delete appointment only with 'Draft' status!"
                ))

        return super().unlink()

    @api.onchange("patient_id")
    def onchange_patient_id(self):
        self.ref = self.patient_id.ref

    def action_test(self):
        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": "https://www.odoo.com",
        }

    def action_draft(self):
        for patient in self:
            patient.state = "draft"

    def action_in_consultation(self):
        for appointment in self:
            if appointment.state == "draft":
                appointment.state = "in_consultation"

    def action_done(self):
        for appointment in self:
            if appointment.state == "in_consultation":
                appointment.state = "done"

        return {
            "effect": {
                "fadeout": "slow",
                "message": "Done",
                "type": "rainbow_man",
            }
        }

    def action_canceled(self):
        action = self.env.ref(
            "om_hospital.action_cancel_appointment"
        ).read()[0]

        return action

    @api.depends("state")
    def _compute_progress(self):
        progress = 0

        for appointment in self:
            if appointment.state == "draft":
                progress = random.randrange(0, 25)
            elif appointment.state == "in_consultation":
                progress = random.randrange(26, 99)
            elif appointment.state == "done":
                progress = 100

            appointment.progress = progress

    def action_share_whatsapp(self):
        if not self.patient_id.phone:
            raise ValidationError(
                _("Missing phone number in patient record!")
            )

        message = f"Hello {self.patient_id.name}"
        whatsapp_api_url = (
            f"https://api.whatsapp.com/send?phone={self.patient_id.phone}&text=*{message}*"
        )

        self.message_post(body=message, subject="Whatsapp Message")

        return {
            "type": "ir.actions.act_url",
            "target": "new",
            "url": whatsapp_api_url,
        }

    def action_notification(self):
        action = self.env.ref(
            "om_hospital.action_hospital_patient"
        )

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Click to open the patient record"),
                "message": "%s",
                "type": "success",
                "sticky": True,
                "links": [{
                    "label": self.patient_id.name,
                    "url": f"#action={action.id}&id={self.patient_id.id}&model=hospital.patient"
                }],
                "next": {
                    "type": "ir.actions.act_window",
                    "res_model": "hospital.patient",
                    "res_id": self.patient_id.id,
                    "views": [(False, "form")],
                }
            }
        }


class AppointmentPharmacyLines(models.Model):
    _name = "appointment.pharmacy.lines"
    _description = "Appointment Pharmacy Lines"

    product_id = fields.Many2one(
        "product.product",
        required=True,
    )
    qty = fields.Integer(
        string="Quantity",
        default=1
    )
    price = fields.Float(
        related="product_id.list_price",
        digits="Product Price",
    )
    appointment_id = fields.Many2one(
        "hospital.appointment",
        string="Appointment",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="appointment_id.currency_id"
    )
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_price_subtotal",
        currency_field="currency_id",
    )

    @api.depends("price", "qty")
    def _compute_price_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.price * rec.qty
