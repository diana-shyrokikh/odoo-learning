import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        result["date_cancel"] = datetime.datetime.today().date()
        result["appointment_id"] = self.env.context.get("active_id")
        return result

    appointment_id = fields.Many2one(
        "hospital.appointment",
        string="Appointment"
    )
    reason = fields.Text(
        string="Reason",
        default="Plans have been changed"
    )
    date_cancel = fields.Date("Cancellation Date")

    def action_cancel(self):
        if self.appointment_id.booking_date == fields.Date.today():
            raise ValidationError(_(
                "Cancellation is not allowed on the same day of booking!"
            ))

        for wizard in self:
            if wizard.appointment_id:
                wizard.appointment_id.state = "canceled"
