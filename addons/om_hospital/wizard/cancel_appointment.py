import datetime
from dateutil import relativedelta

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
        string="Appointment",
        # domain=[
        #     # "|",  or operator
        #     ("state", "=", "draft"),
        #     ("priority", "in", ("0", "1", False))
        # ]
    )
    reason = fields.Text(
        string="Reason",
        default="Plans have been changed"
    )
    date_cancel = fields.Date("Cancellation Date")

    def action_cancel(self):
        cancel_day = self.env["ir.config_parameter"].get_param(
            "om_hospital.cancel_day"
        )
        today = datetime.date.today()
        allowed_date = self.appointment_id.booking_date - relativedelta.relativedelta(
            days=int(cancel_day)
        )
        if allowed_date < today:
            raise ValidationError(_(
                "Cancellation is not allowed for that day of booking!"
            ))

        for wizard in self:
            if wizard.appointment_id:
                wizard.appointment_id.state = "canceled"
                return {
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": "cancel.appointment.wizard",
                    "target": "new",
                    "res_id": self.id,
                }

                # reload the screen

                # return {
                #     "type": "ir.actions.client",
                #     "tag": "reload",
                # }

