from datetime import timedelta
from odoo import models, fields, api, exceptions, _


class Openacademy(models.Model):
    _name = 'openacademy.openacademy'
    _description = 'Openacademy'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    full_name = fields.Char(compute='_comput_full_name', store=False)
    value = fields.Integer(required=True)
    description = fields.Text()
    responsible_id = fields.Many2one(
        'res.users', ondelete='set null', string='Responsible', index=True)
    session_ids = fields.One2many(
        'openacademy.session', 'name', string='Sessions')

    _sql_constraints = [
        ('last_name_description_check',
         'CHECK(last_name != description)',
         _('The last name should not be the description')),

        ('last_name_unique',
         'UNIQUE(last_name)',
         _('The last name must be unique')),
    ]

    @api.depends('first_name', 'last_name')
    def _comput_full_name(self):
        for record in self:
            record.full_name = '%s %s' % (
                record.first_name or '', record.last_name or '')

    def copy(self, default=None):
        default = dict(default or {})
        default['last_name'] = self._copy_last_name()
        return super(Openacademy, self).copy(default)

    def _copy_last_name(self):
        copied_count = self.search_count([
            ('last_name', '=like', _(u'Copy of {}%').format(self.last_name))
        ])
        if not copied_count:
            new_name = _(u'Copy of {}').format(self.last_name)
        else:
            new_name = _(u'Copy of {} ({})').format(
                self.last_name, copied_count)
        return new_name


class Session(models.Model):
    _name = 'openacademy.session'
    _description = 'OpenAcademy Sessions'

    name = fields.Char(required=True)
    start_date = fields.Date(default=fields.Date.today)
    duration = fields.Float(digits=(6, 2), help='Duration in days')
    end_date = fields.Date(
        string='End Date', store=True,
        compute='_compute_end_date', inverse='_inverse_end_date')
    hours = fields.Float(string='Duration in hours',
                         compute='_compute_hours', inverse='_inverse_hours')
    seats = fields.Integer(string='Number of seats')
    taken_seats = fields.Float(string='Taken seats',
                               compute='_compute_taken_seats')
    active = fields.Boolean(default=True)
    color = fields.Integer()

    instructor_id = fields.Many2one(
        'res.partner',
        string='Instructor',
        domain=[('instructor', '=', True)], default=lambda self: self.env.user)
    attendee_ids = fields.Many2many('res.partner', string='Attendees')
    attendees_count = fields.Integer(
        string='Attendees count', compute='_compute_attendees_count',
        store=True)

    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            # Add duration to start_date,
            # but: Monday + 5 days = Saturday,
            # so subtract one second to get on Friday instead
            duration = timedelta(days=r.duration, seconds=-1)
            r.end_date = r.start_date + duration

    def _inverse_end_date(self):
        for r in self:
            if not (r.start_date and r.end_date):
                continue

            # Compute the difference between dates,
            # but: Friday - Monday = 4 days,
            # so add one day to get 5 days instead
            r.duration = (r.end_date - r.start_date).days + 1

    @api.depends('duration')
    def _compute_hours(self):
        for r in self:
            r.hours = r.duration * 24

    def _inverse_hours(self):
        for r in self:
            r.duration = r.hours / 24

    @api.depends('seats', 'attendee_ids')
    def _compute_taken_seats(self):
        for r in self:
            if not r.seats or r.seats < 0:
                r.taken_seats = 0.0
            else:
                r.taken_seats = 100.0 * len(r.attendee_ids) / r.seats

    @api.onchange('seats', 'attendee_ids')
    def _verify_valid_seats(self):
        if self.seats < 0:
            self.seats = 0
            return {
                'warning': {
                    'title': _('Incorrect \'seats\' value'),
                    'message': _('The number of available seats'
                                 'may not be negative'),
                },
            }
        if self.seats < len(self.attendee_ids):
            return {
                'warning': {
                    'title': _('Too many attendees'),
                    'message': _('Increase seats or remove excess attendees'),
                },
            }

    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id and r.instructor_id in r.attendee_ids:
                raise exceptions.ValidationError(
                    _('A session\'s instructor can\'t be an attendee'))

    @api.depends('attendee_ids')
    def _compute_attendees_count(self):
        for r in self:
            r.attendees_count = len(r.attendee_ids)
