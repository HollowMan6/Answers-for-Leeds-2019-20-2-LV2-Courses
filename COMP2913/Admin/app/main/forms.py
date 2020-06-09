from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,IntegerField,RadioField,DateField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class MembershipForm(FlaskForm):
    title = SelectField('Title', choices=[('Ms', 'Ms'), ('Mrs', 'Mrs'), ('Mr', 'Mr')], validators=[DataRequired()])
    firstname = StringField('First name', validators=[
        DataRequired(), Length(1, 64), ])
    lastname = StringField('Last name', validators=[
        DataRequired(), Length(1, 64), ])
    streetname = StringField('House number and Street name', validators=[DataRequired()])
    city = StringField('Town/City', validators=[DataRequired()])
    county = StringField('County', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    phone = IntegerField('Area code + Phone number', validators=[DataRequired()])
    payment = RadioField('Payment method', choices=[('Credit Card', 'Credit Card'),('Cash', 'Cash')],
                         validators=[DataRequired()])
    submit = SubmitField('Submit')

class RefundForm(FlaskForm):
    card_number = StringField('Card number', validators=[Length(0, 64)])
    expire_month = IntegerField('Expire month', validators=[DataRequired()])
    expire_year = IntegerField('Expire year', validators=[DataRequired()])
    security_code = IntegerField('Security code', validators=[DataRequired()])
    submit = SubmitField('Cancel it now', validators=[DataRequired()])

class BasicBookingForm(FlaskForm):
    number = IntegerField('Numbers of people:')
    date = DateField('Date(e.g 2020-05-13):', validators=[DataRequired()],format='%Y-%m-%d')
    start_time = IntegerField('Start time(e.g 19):', validators=[DataRequired()])
    end_time = IntegerField('End time(e.g 20):', validators=[DataRequired()])
    payment = RadioField('Payment method', choices=[('Credit Card', 'Credit Card'),('Cash', 'Cash')],
                         validators=[DataRequired()])



class PoolBookingForm(BasicBookingForm):
    activity = SelectField('Activity',choices=[('General use','General use'),('Lane swimming','Lane swimming'),
                                                ('Lessons','Lessons'),('Team events','Team events')])
    submit = SubmitField('Book')

class FitnessBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('General use', 'General use')])
    submit = SubmitField('Book')

class SquashBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('General use', 'General use'),('Team events','Team events')])
    submit = SubmitField('Book')

class HallBookingForm(BasicBookingForm):
    activity = SelectField('Activity', choices=[('1-hour sessions', '1-hour sessions')])
    submit = SubmitField('Book')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class CardForm(FlaskForm):
    card_number = IntegerField('Card number',validators=[DataRequired()])
    holder_name = StringField('Name on account:', validators=[Length(0, 64)])
    expire_month = IntegerField('Expire month',validators=[DataRequired()])
    expire_year = IntegerField('Expire year', validators=[DataRequired()])
    security_code = IntegerField('Security code', validators=[DataRequired()])
    submit = SubmitField('Pay securely now', validators=[DataRequired()])

class ConfigureFacilityForm(FlaskForm):
    operation = SelectField('Operation', choices=[('add', 'add'), ('edit', 'edit'),('delete', 'delete')])
    name = StringField('Facility name',validators=[Length(0, 64)])
    capacity = IntegerField('Capacity',validators=[DataRequired()])
    url = StringField('Photo url',validators=[Length(0, 64)])
    description = StringField('Description',validators=[Length(0, 64)])
    submit = SubmitField('Submit', validators=[DataRequired()])

class ConfigureActivityForm(FlaskForm):
    operation = SelectField('Operation', choices=[('add', 'add'), ('edit', 'edit'),('delete', 'delete')])
    facility = StringField('Facility name',validators=[Length(0, 64)])
    price = IntegerField('Price',validators=[DataRequired()])
    activity = StringField('Activity name',validators=[Length(0, 64)])
    submit = SubmitField('Submit', validators=[DataRequired()])

class ConfigureTimetableForm(FlaskForm):
    facility = StringField('Facility name', validators=[Length(0, 64)])
    date = DateField('Date',validators=[DataRequired()])
    start_time = IntegerField('Open time',validators=[DataRequired()])
    end_time = IntegerField('Close time',validators=[DataRequired()])
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

