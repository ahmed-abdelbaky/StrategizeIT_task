from odoo import  models, fields, api
from odoo.exceptions import ValidationError


class employeeOnboarding(models.Model):
    _name = 'employee.onboarding'

    name = fields.Char("employee's Full Name")
    job_position = fields.Many2one('hr.job', 'Job Position')
    start_date = fields.Date('Start Date', required=True)
    onboarding_checklist_ids = fields.One2many('onboarding.task', 'employee_onboarding_id','Onboarding Checklist')
    state = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
    ], default='new', string='Status')
    employee_id = fields.Many2one('hr.employee', 'Employee')

    def set_state_progress(self):
        self.state='progress'

    def set_state_finish(self):
        for rec in self.onboarding_checklist_ids:
            rec.state = 'finish'
        self.state = 'done'

    @api.constrains('start_date')
    def _constrain_on_start_date(self):
        for record in self:
            if record.start_date:
                if record.start_date < fields.Date.today():
                    raise ValidationError('Start Date Must be Equal or Greater Today Date')

