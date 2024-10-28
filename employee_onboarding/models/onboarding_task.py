from odoo import models, fields,api


class onboardingTask(models.Model):
    _name = 'onboarding.task'

    name = fields.Char('Name')
    employee_onboarding_id = fields.Many2one('employee.onboarding')
    state = fields.Selection([
        ('running', 'Running'),
        ('finish', 'Finished'),
    ], default='running', string='Status')