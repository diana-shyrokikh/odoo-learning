import datetime

from odoo import api, fields, models


class CancelAppointmentWizard(models.TransientModel):
    _name = "cancel.appointment.wizard"
    _description = "Cancel Appointment Wizard"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        result["date_cancel"] = datetime.datetime.today().date()
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
        for wizard in self:
            if wizard.appointment_id:
                wizard.appointment_id.state = "canceled"
