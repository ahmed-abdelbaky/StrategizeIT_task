from odoo import models, fields, api, _
from odoo.tools.populate import compute


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    onboarding_finish_button_invisible = fields.Boolean(compute='_compute_invisible_button')

    def _compute_invisible_button(self):
        for record in self:
            onboarding = self.env['employee.onboarding'].search([('employee_id', '=', self.id), ('state', '=', 'new')])
            if onboarding:
                record.onboarding_finish_button_invisible = True
            else:
                record.onboarding_finish_button_invisible = False



    def show_onboarding_employee(self):
        return {
            'name': _('Onboarding Employee'),
            'res_model': 'employee.onboarding',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'view_mode': 'kanban,form',
            'context': {'default_employee_id': self.id},
            'domain':[('employee_id', '=', self.id), ('state', '=', 'new')]
        }