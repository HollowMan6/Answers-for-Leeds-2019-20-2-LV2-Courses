from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, \
    SubmitField, IntegerField, RadioField, FormField, DecimalField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange, Length, Email, Regexp
from wtforms import ValidationError
from card_identifier.card_type import identify_card_type

from ..auth.forms import RegistrationForm
from ..models import Role, User


class EditMembershipTypeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    length = IntegerField('Length in days', validators=[DataRequired(), NumberRange(min=1)])
    price = DecimalField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ExpiryDate(FlaskForm):
    expiry_month = IntegerField(validators=[NumberRange(1, 12)])
    expiry_year = IntegerField(validators=[NumberRange(min=date.today().year)])


class PaymentCardForm(FlaskForm):
    cardholder_name = StringField('Cardholder name', validators=[DataRequired()])
    card_number = StringField('Card number',
                              validators=[DataRequired(),
                                          Regexp(r'(?:[0-9]{4}-){3}[0-9]{4}|[0-9]{16}',
                                                 message='Invalid card number')])
    expiry_date = FormField(ExpiryDate, label='Expiry date')
    security_code = StringField('Security code', validators=[DataRequired(), Length(min=3, max=3)])


class BasicBookingForm(FlaskForm):
    number = IntegerField('Numbers of people:')
    date = DateField('Date:', validators=[DataRequired()])
    start_time = IntegerField('Start time:', validators=[DataRequired()])
    end_time = IntegerField('End time:', validators=[DataRequired()])
    payment = RadioField('Payment method', choices=[('Pay on delivery', 'Pay on delivery')],
                         validators=[DataRequired()])
    submit = SubmitField('Book')


class PoolBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('General use', 'General use'), ('Lane swimming', 'Lane swimming'),
                                                ('Lessons', 'Lessons'), ('Team events', 'Team events')])


class FitnessBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('General use', 'General use')])


class SquashBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('General use', 'General use'), ('1-hour sessions', '1-hour sessions')])


class HallBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('Basketball', 'Basketball'), ('Badminton', 'Badminton'),
                                                ('1-hour sessions', '1-hour sessions')])


class BookActivityForm(FlaskForm):
    activity_instance_id = RadioField('Choose a date/time', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, activity, *args, **kwargs):
        super(BookActivityForm, self).__init__(*args, **kwargs)
        self.activity_instance_id.choices = [(instance.id, self.instance_preview(instance)) for instance in activity.instances]

    @staticmethod
    def instance_preview(instance):
        return instance.start_time


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class CardForm(FlaskForm):
    card_number = StringField('Card number', validators=[Length(0, 64)])
    expire_month = IntegerField('Expire month', validators=[DataRequired()])
    expire_year = IntegerField('Expire year', validators=[DataRequired()])
    security_code = IntegerField('Security code', validators=[DataRequired()])
    submit = SubmitField('Pay securely now', validators=[DataRequired()])


class ConfigureFacilityForm(FlaskForm):
    operation = SelectField('Operation', choices=[('add', 'add'), ('edit', 'edit'), ('delete', 'delete')])
    name = StringField('Facility name', validators=[Length(0, 64)])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    url = StringField('Photo url', validators=[Length(0, 64)])
    description = StringField('Description', validators=[Length(0, 64)])
    submit = SubmitField('Submit', validators=[DataRequired()])


class ConfigureActivityForm(FlaskForm):
    operation = SelectField('Operation', choices=[('add', 'add'), ('edit', 'edit'), ('delete', 'delete')])
    facility = StringField('Facility name', validators=[Length(0, 64)])
    price = IntegerField('Capacity', validators=[DataRequired()])
    activity = StringField('Photo url', validators=[Length(0, 64)])
    submit = SubmitField('Submit', validators=[DataRequired()])


class ConfigureTimetableForm(FlaskForm):
    facility = StringField('Facility name', validators=[Length(0, 64)])
    date = DateField('Date', validators=[DataRequired()])
    start_time = IntegerField('Open time', validators=[DataRequired()])
    end_time = IntegerField('Close time', validators=[DataRequired()])
    submit = SubmitField('Submit', validators=[DataRequired()])


class SearchForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Submit', validators=[DataRequired()])


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class SelectPaymentForm(FlaskForm):
    NEW_CARD_CHOICE = (-1, '+ Add payment card')
    payment_card = SelectField('Payment card', coerce=int)
    new_payment_card = FormField(PaymentCardForm, id='new_payment_card')
    submit = SubmitField('Submit')

    def __init__(self, cards, *args, **kwargs):
        super(SelectPaymentForm, self).__init__(*args, **kwargs)
        self.payment_card.choices = [(card.id, self.card_preview(card.card_number))
                                     for card in cards]
        self.payment_card.choices.append(self.NEW_CARD_CHOICE)

    @staticmethod
    def card_preview(card_number):
        return '{card_type} (•••• •••• •••• {last_digits})'.format(
            card_type=identify_card_type(card_number), last_digits=card_number[-4:])

    def validate(self):
        super(SelectPaymentForm, self).validate()

        no_other_errors = not any(getattr(self, field).errors for field in self._fields if field != "new_payment_card")
        only_new_card_invalid = self.new_payment_card.errors and no_other_errors

        # If new card is invalid but we're not adding a card, ignore
        return only_new_card_invalid and self.payment_card.data != self.NEW_CARD_CHOICE


class EditFacilityForm(FlaskForm):
    name = StringField('Facility Name', validators=[Length(0, 64)])
    capacity = IntegerField('Capacity of Facility', validators=[DataRequired()])
    description = TextAreaField('Facility Description')
    # courts and activities linked to facility when added themselves
    submit = SubmitField('Submit')


class EditActivityForm(FlaskForm):
    activity_staff_id = IntegerField('Staff ID number', validators=[DataRequired()])
    activity_price = DecimalField('Price of Activity', validators=[DataRequired()])
    activity_name = StringField('Activity Name', validators=[Length(0, 64)])
    facility_id = IntegerField('Facility ID', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditUserForm(RegistrationForm):
    role = QuerySelectField(query_factory=lambda: Role.query.all())


class EditActivityInstanceForm(FlaskForm):
    start_time = DateTimeLocalField('Start time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    activity_id = IntegerField('Activity ID', validators=[DataRequired()])
    court_id = IntegerField('Court ID', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditMembershipForm(FlaskForm):
    membership_type_id = IntegerField('Membership type ID', validators=[DataRequired()])
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Submit')
