from datetime import datetime, timedelta
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    PAY= 1
    CANCEL = 2
    HANDLE = 3
    DISPLAY = 4
    VIEW_BUSINESS = 5
    CONFIGURE = 6
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')


    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.PAY, Permission.CANCEL, Permission.HANDLE,Permission.DISPLAY],
            'Employee':[Permission.PAY, Permission.CANCEL, Permission.HANDLE,Permission.DISPLAY],
            'Manager': [Permission.VIEW_BUSINESS, Permission.CONFIGURE],

            'Moderator': [ Permission.MODERATE],
            'Administrator': [ Permission.MODERATE,Permission.ADMIN],

        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

class Membership_type(db.Model):
    __tablename__ = 'membership_type'
    id=db.Column(db.Integer,primary_key=True)
    length=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    memberships = db.relationship('Membership',backref='user',lazy='dynamic')

class Membership(db.Model): #have a one-to-one relationship with user since one user can only have at most one membership
    __tablename__ = 'membership'
    id=db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(8), index=True)
    firstname = db.Column(db.String(32), index=True)
    lastname = db.Column(db.String(32), index=True)
    status = db.Column(db.String(16), nullable=False)
    start_date=db.Column(db.DateTime, default=datetime.utcnow)
    end_date=db.Column(db.DateTime, default=datetime.utcnow)
    membership_type_id=db.Column(db.Integer,db.ForeignKey('membership_type.id'))
    account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))

    def valueOfEnd_date(self,length):
        self.end_date = self.start_date + timedelta(days=length)
        db.session.add(self)

class User(UserMixin, db.Model): #customers
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'),default=1)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        url = 'https://secure.gravatar.com/avatar'
        hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

"""
#each staff can manage many facilities and each facility can be managed by many staffs.
manage_facility_table=db.Table('manage_facility_table',
                               db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'), primary_key=True),
                               db.Column('facility_id', db.Integer, db.ForeignKey('facility.id'), primary_key=True))
                               """

class Facility(db.Model): #facility table, each facility can have many courts and activities
    __tablename__ = 'facilities'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(16),nullable=False)
    url = db.Column(db.String(256), nullable=False)
    capacity=db.Column(db.Integer)
    description=db.Column(db.String(64),nullable=False)
    times = db.relationship('Time_management', backref='court',
                            lazy='dynamic')  # each court have many intervals for booking
    '''courts=db.relationship('Court',backref='facility')'''
    activities=db.relationship('Activity',backref='facility')

class Booking(db.Model): #each user can have many bookings
    __tablename__ = 'bookings'
    id=db.Column(db.Integer,primary_key=True)
    number=db.Column(db.Integer)
    activity=db.Column(db.String(16))
    activity_id = db.Column(db.Integer,db.ForeignKey('activities.id'))
    status=db.Column(db.String(16),nullable=False)
    payment=db.Column(db.String(32),default='Cash')
    fees=db.Column(db.Integer,nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    time_id = db.Column(db.Integer, db.ForeignKey("timetables.id"))
    account_id=db.Column(db.Integer,db.ForeignKey('accounts.id'))

class Time_management(db.Model):
    __tablename__ = 'timetables'
    id=db.Column(db.Integer,primary_key=True)
    date=db.Column(db.Date,nullable=False)
    start_time = db.Column(db.Integer,nullable=False)
    end_time = db.Column(db.Integer,nullable=False)
    current_capacity = db.Column(db.Integer,default=0)
    '''booking_id=db.Column(db.Integer,db.ForeignKey(Booking.id),default=-1)'''
    bookings=db.relationship('Booking',backref="timetable")
    facility_id=db.Column(db.Integer,db.ForeignKey(Facility.id))

"""
class Court(db.Model): #e.g like basketball court, there are 7 courts for use
    __tablename__ = 'courts'
    id=db.Column(db.Integer,primary_key=True)
    number=db.Column(db.Integer)
    availablity=db.Column(db.String,default='available')
    times=db.relationship('Time_management',backref='court',lazy='dynamic') #each court have many intervals for booking
    facility_id = db.Column(db.Integer, db.ForeignKey('facilities.id'))
"""

class Activity(db.Model): #avtivity
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    weekly_income = db.Column(db.Integer)
    weekly_usage = db.Column(db.Integer)
    #activity_staff_id=db.Column(db.Integer)
    activity_price=db.Column(db.Integer)
    activity_name=db.Column(db.String(16))
    repeat_every = db.Column(db.Integer)
    bookings = db.relationship('Booking', backref="activity_ii")
    facility_id=db.Column(db.Integer,db.ForeignKey('facilities.id'))

class Credit_card_info(db.Model): #paying card information
    __tablename__ = 'cards'
    id=db.Column(db.Integer,primary_key=True)
    card_number=db.Column(db.Integer,nullable=False)
    expire_month=db.Column(db.Integer,nullable=False)
    expire_year=db.Column(db.Integer,nullable=False)
    security_code=db.Column(db.Integer,nullable=False)
    holder_name=db.Column(db.String(64),nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))

class Account(db.Model):
    __tablename__='accounts'
    id=db.Column(db.Integer, primary_key=True, nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('users.id'), unique=True)
    membership = db.relationship('Membership', uselist=False)
    cards = db.relationship('Credit_card_info', backref='account', lazy='dynamic')
    bookings = db.relationship('Booking', backref='account', lazy='dynamic')

"""
class Staff(db.Model):
    __tablename__ = 'staffs'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),nullable=False)
    role=db.Column(db.String(64),nullable=False)
    facilities = db.relationship('Facility',secondary=manage_facility_table,backref='Staff')
    """

"""
class Business(db.Model):
    __tablename__= 'business'
    id = db.Column(db.Integer,primart_key=True)
    people = db.Column(db.Integer)
    income = db.Column(db.Integer)
"""
