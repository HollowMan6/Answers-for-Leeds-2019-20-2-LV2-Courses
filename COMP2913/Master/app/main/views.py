import datetime as dt
from functools import reduce

import qrcode
import pdfkit
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import main
from .tables import ActivityTable, FacilityTable
from .forms import *
from ..models import *
from .. import db
from ..decorators import admin_required, permission_required
from ..email import send_email


@main.route('/')
def index():
    if current_user.is_administrator():
        return render_template('admin/index.html')
    return render_template('index.html')


@main.route('/facility')
def facility():
    facilities = Facility.query.all()
    return render_template('facilities.html', facilities=facilities)


@main.route('/facility_info/<int:id>')
def view_info(id):
    facility = Facility.query.filter_by(id=id).first()
    return render_template('facility_info.html', facility=facility)


@main.route('/membership')
def view_membership_type():
    memberships = MembershipType.query.all()
    return render_template('membership.html', memberships=memberships)


@main.route('/my_bookings/<int:id>')
@login_required
@permission_required(Permission.DISPLAY)
def display_my_bookings(id):
    account = User.query.get_or_404(id)
    bookings = Booking.query.order_by(Booking.timestamp.desc()).filter_by(account_id=account.id).all()
    start_time = []
    end_time = []
    for booking in bookings:
        timetable = TimeManagement.query.filter_by(booking_id=booking.id).get()
        start_time.append(timetable.start_time)
        end_time.append(timetable.end_time)
    return render_template('my_booking.html', bookings=bookings)


@main.route('/pricing_list')
def display_pricing_list():
    return render_template('pricing_list.html', facilities=Facility.query.all())


@main.route('/activities/<int:id>/book', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def book_activity(id):
    form = BookActivityForm(activity=Activity.query.get(id))
    if form.validate_on_submit():
        return render_template('book_activity_instance.html', instance_id=form.activity_instance_id.data)
    return render_template('book_activity.html', form=form)


@main.route('/activity-instances/<int:instance_id>/book', methods=['GET', 'POST'])
def book_activity_instance(instance_id):
    form = SelectPaymentForm(cards=current_user.cards)
    instance = ActivityInstance.query.get_or_404(instance_id)
    if form.validate_on_submit():
        booking = Booking(activity_instance_id=instance_id,
                          status='Paid',
                          user_id=current_user.id)
        db.session.add(booking)
        db.session.commit()
        return render_template('booking_success.html', booking=booking)
    return render_template('book_activity_instance.html', form=form, instance=instance)


@main.route('/book/<int:type>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def book_facility(type):
    if type == 1:
        facility = "Swimming pool"
        form = PoolBookingForm()
    elif type == 2:
        facility = "Fitness room"
        form = FitnessBookingForm()
    elif type == 3:
        facility = "Squash courts"
        form = SquashBookingForm()
    else:
        facility = "Sports hall"
        form = HallBookingForm()

    if form.validate_on_submit():
        activity = form.activity.data
        number = form.number.data
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        payment = form.payment.data

        fac = Facility.query.filter_by(name=facility).first()
        act = fac.activities.query.filter_by(activity_name=activity).first()
        price = act.activity_price

        if end_time - start_time != 1:
            flash('You can only book a 1-hour session')
            return redirect(url_for('.book_facility', type=type))

        timetables = TimeManagement.query.filter_by(date=date).all()
        for timetable in timetables:
            if start_time == timetable.start_time:
                id = timetable.id

        timetable = TimeManagement.query.filter_by(id=id).get()

        if number + timetable.current_capacity > fac.capacity:
            flash('Your have too many people!')
            return redirect(url_for('.book_facility', type=type))

        else:
            act.weekly_income = act.weekly_income + price
            act.weekly_usage = act.weekly_usage + number
            db.session.add(act)
            db.session.commit()

            booking = Booking(number=number,
                              time_id=timetable.id,
                              activity=activity,
                              status="Unpaid",
                              payment=payment,
                              fees=price)
            db.session.add(booking)
            db.session.commit()

            account = Account.query.filter_by(user_id=current_user.id).first()
            book = Booking.query.order_by(Booking.timestamp.desc()).filter_by(account_id=account.id).first_or_404()

            timetable.current_capacity = number + timetable.current_capacity
            db.session.add(timetable)
            db.session.commit()

            if payment == "Credit Card":
                flash('Pay for your booking.')
                return redirect(url_for('.handle_card_booking'), book_id=book.id)
            elif payment == "Cash":
                flash('You will pay for your booking by cash.')
                return redirect(url_for('.index'))

    return render_template('book.html', form=form)


'''
@main.route('/book_season', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def book_regular():
    form = RegularBookForm()
    if form.validate_on_submit():
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
'''


@main.route('/handle_card_booking/<int:book_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.HANDLE)
def handle_card_booking(book_id):
    account = Account.query.filter_by(user_id=current_user.id).first()
    card = CreditCardInfo.query.filter_by(account_id=account.id).first()
    book = Booking.query.filter_by(id=book_id).first()
    form = CardForm()

    if form.validate_on_submit():
        card_info = CreditCardInfo(card_number=form.card_number.data,
                                   expire_month=form.expire_month.data,
                                   expire_year=form.expire_year.data,
                                   security_code=form.security_code.data,
                                   holder_name=form.holder_name.data,
                                   account_id=id
                                   )
        if card is not None:
            form.card_number.data = card.card_number
            form.expire_month.data = card.expire_month
            form.expire_year.data = card.expire_year
            form.security_code.data = card.security_code
            form.holder_name.data = card.holder_name
        db.session.add(card_info)
        db.session.commit()
        book.status = "Paid"
        db.session.add(book)
        db.session.commit()

        receipt = book.activity + '\n' + book.time.date + '\n' + book.time.start_time + '~' + book.time.end_time + '\n'
        pdf_name = str(book.id) + '.pdf'
        pdfkit.from_string(receipt, pdf_name)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(
            book.activity + '\n' + book.time.date + '\n' + book.time.start_time + '~' + book.time.end_time + '\n')
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        send_email(current_user.email, 'Your booking receipt',
                   'booking_receipt', book=book, img=img)
        flash('A booking receipt has been sent to you by email.')
    return render_template('handle_card_booking.html', book=book, form=form)


@main.route('/bookings/<int:id>/cancel', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CANCEL)
def cancel_booking(id):
    booking = Booking.query.get_or_404(id)
    form = SelectPaymentForm(cards=current_user.cards)
    if form.validate_on_submit():
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('.display_user_bookings'))
    return render_template('cancel_booking.html', form=form, booking=booking)


@main.route('/pay_membership/<int:type_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def pay_membership(type_id):
    membership_type = MembershipType.query.query.filter_by(id=type_id).get()
    account = Account.query.filter_by(user_id=current_user.id).first()
    form = PurchaseMembershipForm()
    if form.validate_on_submit():
        membership = Membership(title=form.title.data,
                                status="Unpaid",
                                firstname=form.firstname.data,
                                lastname=form.lastname.data,
                                payment=form.payment.data,
                                account_id=account.id,
                                membership_type_id=membership_type.id
                                )
        db.session.add(membership)
        db.session.commit()

        if (membership_type.length == 3):
            length = 30
        elif (membership_type.length == 3):
            length = 90
        else:
            length = 365
        membership.valueOfEnd_date(length)
        db.session.commit()

        flash('Thanks! You have become our membership!')
        return redirect(url_for('handle_card_membership', id=account.id))
    return render_template('pay_membership.html', form=form, membership_type=membership_type)


@main.route('/handle_card_membership/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.HANDLE)
def handle_card_membership(id):
    membership = Membership.query.filter_by(account_id=id).first()
    card = CreditCardInfo.query.filter_by(account_id=id).first()
    form = CardForm()
    membership_type = MembershipType.query.filter_by(id=membership.membership_type_id).first()
    price = membership_type.id
    if form.validate_on_submit():
        card_info = CreditCardInfo(card_number=form.card_number.data,
                                   expire_month=form.expire_month.data,
                                   expire_year=form.expire_year.data,
                                   security_code=form.security_code.data,
                                   holder_name=form.holder_name.data,
                                   account_id=id
                                   )
        if card is not None:
            form.card_number.data = card.card_number
            form.expire_month.data = card.expire_month
            form.expire_year.data = card.expire_year
            form.security_code.data = card.security_code
            form.holder_name.data = card.holder_name
        db.session.add(card_info)
        db.session.commit()
        membership.status = "Paid"
        db.session.add(membership)
        db.session.commit()
        send_email(current_user.email, 'Your booking receipt',
                   'booking_receipt', membership=membership)
        flash('A booking receipt has been sent to you by email.')
    return render_template('handle_card_membership.html', price=price, form=form)


@main.route('/configure_facility', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CONFIGURE)
def configure_facility():
    form = ConfigureFacilityForm()
    if form.validate_on_submit():
        operation = form.operation.data
        capacity = form.capacity.data
        name = form.name.data
        url = form.url.data
        description = form.description.data

        if operation == "add":
            facility = Facility(name=name,
                                url=url,
                                capacity=capacity,
                                description=description)
            db.session.add(facility)
            db.session.commit()
            flash('You have added the facility')

        elif operation == "edit":
            fac = Facility.query.filter_by(name=name).get()
            fac.capacity = capacity
            fac.url = url
            fac.description = description

            db.session.add(fac)
            db.session.commit()
            flash('You have edited the facility')

        elif operation == "delete":
            fac = Facility.query.filter_by(name=name).get()
            db.session.delete(fac)
            db.session.commit()
            flash('You have deleted the facility')

    return render_template('configure_facility.html', form=form)


@main.route('/configure_activity', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CONFIGURE)
def configure_activity():
    form = ConfigureActivityForm()
    if form.validate_on_submit():
        operation = form.operation.data
        facility = form.facility.data
        activity = form.activity.data
        price = form.price.data

        fac = Facility.query.filter_by(name=facility).get
        if operation == "add":
            act = Activity(weekly_income=0,
                           weekly_usage=0,
                           activity_price=price,
                           activity_name=activity,
                           facility_id=fac.id
                           )
            db.session.add(act)
            db.session.commit()
            flash('You have added the activity')

        elif operation == "edit":
            act = Activity.query.filter_by(activity_name=activity).get()
            act.activity_price = price,
            act.activity_name = activity
            act.facility_id = fac.id

            db.session.add(act)
            db.session.commit()
            flash('You have edited the activity')

        elif operation == "delete":
            act = Activity.query.filter_by(activity_name=activity).get()
            db.session.delete(act)
            db.session.commit()
            flash('You have deleted the activity')

        return render_template('configure_activity.html', form=form)


@main.route('/configure_timetable')
@login_required
@permission_required(Permission.CONFIGURE)
def configure_timetable():
    form = ConfigureTimetableForm()
    if form.validate_on_submit():
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        facility = form.facility.data

        fac = Facility.query.filter_by(name=facility).get()

        for i in range(start_time, end_time):
            timetable = TimeManagement(date=date,
                                       start_time=i,
                                       end_time=i + 1,
                                       facility_id=fac.id)
            db.session.add(timetable)
            db.session.commit()

        return render_template('configure_timetable.html', form=form)


@main.route('/facilities')
def display_facilities():
    facilities = Facility.query.all()
    template = 'admin/facilities.html' if current_user.is_administrator() else 'facilities.html'
    return render_template(template, facilities=facilities)


@main.route('/membership-types')
def display_membership_types():
    memberships = MembershipType.query.all()
    template = 'admin/membership_types.html' if current_user.is_administrator() else 'membership.html'
    return render_template(template, membership_types=memberships)


@main.route('/membership-types/<int:type>/purchase', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def purchase_membership(type):
    membership_type = MembershipType.query.get_or_404(type)
    form = SelectPaymentForm(cards=current_user.cards)

    if form.validate_on_submit():
        membership = Membership(membership_type_id=type, user_id=current_user.id)
        db.session.add(membership)

        if form.payment_card.data == SelectPaymentForm.NEW_CARD_CHOICE[0]:
            card_form = form.new_payment_card
            new_card = CreditCardInfo(
                holder_name=card_form.cardholder_name.data,
                card_number=card_form.card_number.data,
                expire_month=card_form.expiry_date.expiry_month.data,
                expire_year=card_form.expiry_date.expiry_year.data,
                security_code=card_form.security_code.data,
                user_id=current_user.id
            )
            db.session.add(new_card)
            flash('Card successfully added to your account.')

        db.session.commit()
        flash('Thanks! You have successfully purchased a {} membership.'.format(membership_type.name))
        return redirect(url_for('main.index'))

    return render_template('pay_membership.html', membership_type=membership_type, form=form)


@main.route('/my/bookings')
@login_required
def display_user_bookings():
    return render_template('my_booking.html', bookings=current_user.bookings)


@main.route('/my_card/<int:id>')
@login_required
@permission_required(Permission.DISPLAY)
def display_cards(id):
    user = User.query.filter_by(id=id).first()
    cards = CreditCardInfo.query.filter_by(user_id=user.id).all()
    return render_template('my_card.html', cards=cards)


@main.route('/my/membership')
@login_required
@permission_required(Permission.DISPLAY)
def display_membership():
    membership = Membership.query.filter_by(user_id=current_user.id).first()
    membership_type = MembershipType.query.filter_by(id=membership.membership_type_id).first() if membership else None
    return render_template('my_membership.html', membership=membership, membership_type=membership_type)


@main.route('/timetable')
def timetable_all():
    date = request.args.get('date', default=datetime.today(), type=dt.datetime)
    end_of_day = datetime(
        year=date.year,
        month=date.month,
        day=date.day + 1,
        hour=0,
        minute=0,
        second=0
    )
    activity_instances = ActivityInstance.query \
        .filter(ActivityInstance.start_time >= date, ActivityInstance.end_time < end_of_day) \
        .order_by(ActivityInstance.start_time) \
        .all()

    activity_instances_by_facility = {facility.name: [] for facility in Facility.query.all()}
    for instance in activity_instances:
        activity_instances_by_facility[instance.activity.facility.name].append(instance)

    return render_template('timetable_all.html', activity_instances=activity_instances_by_facility)


@main.route('/facilities/<int:id>/timetable')
def timetable_facility(id):
    facility = Facility.query.get_or_404(id)
    activity_instances = reduce(list.__add__, [activity.instances.order_by(ActivityInstance.start_time).all() for activity in facility.activities.all()])
    return render_template('timetable_all.html', activity_instances={facility.name: activity_instances})


# @main.route('/timetable_facility/<int:type>')
# def timetable_facility(type):
#     if type == 1:
#         facility = "Swimming pool"
#     elif type == 2:
#         facility = "Fitness room"
#     elif type == 3:
#         facility = "Squash courts"
#     else:
#         facility = "Sports hall"
#
#     facility = Facility.query.filter_by(name=facility).all()
#     today = dt.date.today()
#     day2 = today + dt.timedelta(days=1)
#     day3 = today + dt.timedelta(days=2)
#     day4 = today + dt.timedelta(days=3)
#     day5 = today + dt.timedelta(days=4)
#     timetable1 = TimeManagement.query.filter_by(start_time=today).all()
#     timetable2 = TimeManagement.query.filter_by(start_time=day2).all()
#     timetable3 = TimeManagement.query.filter_by(start_time=day3).all()
#     timetable4 = TimeManagement.query.filter_by(start_time=day4).all()
#     timetable5 = TimeManagement.query.filter_by(start_time=day5).all()
#     return render_template('timetable_facility.html', type=type + 1, today=today, day3=day3, day2=day2, day4=day4,
#                            day5=day5, facility=facility, timetable1=timetable1, timetable2=timetable2,
#                            timetable3=timetable3, timetable4=timetable4, timetable5=timetable5)


@main.route('/my/membership/cancel', methods=['GET', 'POST'])
@login_required
def cancel_membership():
    membership = current_user.membership
    if membership is None:
        return redirect(url_for('main.display_membership'))
    timedelta = membership.get_end_date() - dt.datetime.now()
    days_left = timedelta.days
    money_refund = 0.9 * (days_left / membership.membership_type.length) * membership.membership_type.price
    form = SelectPaymentForm(cards=current_user.cards)
    if form.validate_on_submit():
        db.session.delete(membership)
        db.session.commit()
        flash('You have cancelled our membership!')
        return redirect(url_for('main.display_membership'))
    return render_template('cancel_membership.html', money_refund=money_refund, days_left=days_left,
                           membership=membership, form=form)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/search_booking')
@login_required
@permission_required(Permission.CANCEL)
def search_booking():
    form = SearchForm()
    if form.validate_on_submit():
        email = form.eamil.data

        user = User.query.filter_by(email=email).get()
        return redirect(url_for('display_bookings', id=user.id))
    return render_template('search_booking.html', form=form)


@main.route('/search_membership')
@login_required
@permission_required(Permission.CANCEL)
def search_membership():
    form = SearchForm()
    if form.validate_on_submit():
        email = form.eamil.data

        user = User.query.filter_by(email=email).get()
        return redirect(url_for('display_membership', id=user.id))
    return render_template('search_membership.html', form=form)


@main.route('/view_income')
@login_required
@permission_required(Permission.VIEW_BUSINESS)
def view_income():
    """income_facility1 = 0
    income_facility2 = 0
    income_facility3 = 0
    income_facility4 = 0

    today = datetime.date.today()
    day1 = today - datetime.timedelta(days=1)
    day2 = today - datetime.timedelta(days=2)
    day3 = today - datetime.timedelta(days=3)
    day4 = today - datetime.timedelta(days=4)
    day5 = today - datetime.timedelta(days=5)
    day6 = today - datetime.timedelta(days=6)

    timetable1 = Time_management.query.filter_by(date=today).all()
    timetable2 = Time_management.query.filter_by(date=day1).all()
    timetable3 = Time_management.query.filter_by(date=day2).all()
    timetable4 = Time_management.query.filter_by(date=day3).all()
    timetable5 = Time_management.query.filter_by(date=day4).all()
    timetable6 = Time_management.query.filter_by(date=day5).all()
    timetable7 = Time_management.query.filter_by(date=day6).all()

    for timetable in timetable1:
        if timetable.facility == 1:
            booking = Booking.query.filter_by(id=timetable.booking_id).get()
            income_facility1 += booking.fees
"""
    overall_income = 0
    overall_usage = 0
    activities = Activity.query.all()
    for activity in activities:
        overall_income += activity.weekly_income
        overall_usage += activity.weekly_usage
    return render_template('business.html', overall_income=overall_income,
                           overall_usage=overall_usage, activities=activities)


@admin_required
@main.route('/users')
def display_users():
    return render_template('admin/users.html', users=User.query.all())


@admin_required
@main.route('/users/new', methods=['GET', 'POST'])
def add_user():
    form = EditUserForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password=form.password.data,
                    role_id=form.role.data.id)
        db.session.add(user)
        db.session.commit()
        flash('User successfully added to database.')
        return redirect(url_for('.display_users'))
    return render_template('admin/edit_user.html', form=form)


@admin_required
@main.route('/activity-instances')
def display_activity_instances():
    return render_template('admin/activity_instances.html', activity_instances=ActivityInstance.query.all())


@admin_required
@main.route('/activity-instances/new', methods=['GET', 'POST'])
def add_activity_instance():
    form = EditActivityInstanceForm()
    if form.validate_on_submit():
        instance = ActivityInstance(
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            activity_id=form.activity_id.data,
            court_id=form.court_id.data
        )
        db.session.add(instance)
        db.session.commit()
        flash('Activity instance successfully added to database.')
        return redirect(url_for('.display_activity_instances'))
    return render_template('admin/edit_activity_instance.html', form=form)


@admin_required
@main.route('/memberships')
def display_memberships():
    return render_template('admin/memberships.html', memberships=Membership.query.all())


@admin_required
@main.route('/memberships/new', methods=['GET', 'POST'])
def add_membership():
    form = EditMembershipForm()
    if form.validate_on_submit():
        membership = Membership(
            membership_type_id=form.membership_type_id.data,
            user_id=form.user_id.data
        )
        db.session.add(membership)
        db.session.commit()
        flash('Membership successfully added to database.')
        return redirect(url_for('.display_memberships'))
    return render_template('admin/edit_membership.html', form=form)


@admin_required
@main.route('/activities')
def display_activities():
    return render_template('admin/activities.html', activities=Activity.query.all())


@admin_required
@main.route('/bookings')
def display_bookings():
    return render_template('admin/bookings.html', bookings=Booking.query.all())


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/facilities/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_facility():
    form = EditFacilityForm()
    if form.validate_on_submit():
        facility = Facility(name=form.name.data,
                            capacity=form.capacity.data,
                            description=form.description.data)
        db.session.add(facility)
        db.session.commit()
        flash('Facility has been added to Database')
        return redirect(url_for('.display_facilities'))

    return render_template('admin/edit_facility.html', form=form)


@main.route('/activities/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_activity():
    form = EditActivityForm()
    if form.validate_on_submit():
        activity = Activity(activity_staff_id=form.activity_staff_id.data,
                            activity_price=form.activity_price.data,
                            activity_name=form.activity_name.data,
                            facility_id=form.facility_id.data)
        db.session.add(activity)
        db.session.commit()
        flash('Facility has been added to Database')
        return redirect(url_for('.display_activities'))

    return render_template('admin/edit_activity.html', form=form)


@main.route('/membership-types/new', methods=['GET', 'POST'])
@login_required
@admin_required
def add_membership_type():
    form = EditMembershipTypeForm()
    if form.validate_on_submit():
        membership_type = MembershipType(name=form.name.data, length=form.length.data, price=form.price.data)
        db.session.add(membership_type)
        db.session.commit()
        flash('Membership type has been added to database')
        return redirect(url_for('.display_membership_types'))
    return render_template('admin/edit_membership_type.html', form=form)


@main.route('/membership-types/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_membership_type(id):
    mtype = MembershipType.query.get_or_404(id)
    form = EditMembershipTypeForm()

    if form.validate_on_submit():
        mtype.name = form.name.data
        mtype.length = form.length.data
        mtype.price = form.price.data

        db.session.commit()
        flash('Membership type successfully updated!')
        return redirect('/')

    form.name.data = mtype.name
    form.length.data = mtype.length
    form.price.data = mtype.price

    return render_template('admin/edit_facility.html', form=form)


# TODO: need some kind of display function for each facility to reach id before calling this method
@main.route('/facilities/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_facility(id):
    facility = Facility.query.get_or_404(id)
    form = EditFacilityForm()

    if form.validate_on_submit():
        facility.name = form.name.data
        facility.capacity = form.capacity.data
        facility.description = form.description.data

        db.session.commit()
        flash('Facility successfully updated!')
        return redirect('/')

    form.name.data = facility.name
    form.capacity.data = facility.capacity
    form.description.data = facility.description

    return render_template('admin/edit_facility.html', form=form)


# TODO: need some kind of display function for each activity to reach id before calling this method
@main.route('/activities/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    form = EditActivityForm()

    if form.validate_on_submit():
        activity.activity_name = form.activity_name.data
        activity.activity_staff_id = form.activity_staff_id.data
        activity.activity_price = form.activity_price.data
        activity.facility_id = form.facility_id.data

        db.session.commit()
        flash('Activity successfully updated!')
        return redirect(url_for('.display_activities'))

    form.activity_name.data = activity.activity_name
    form.activity_staff_id.data = activity.activity_staff_id
    form.activity_price.data = activity.activity_price
    form.facility_id.data = activity.facility_id

    return render_template('admin/edit_activity.html', form=form)


# Display method to display the list of activities to get to the edit function
@main.route('/activities/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def display_activity(id):
    activities = db.session.query(Activity).all()

    if not activities:
        flash('No results found!')
        return redirect('/')
    else:
        table = ActivityTable(activities)
        table.border = True
        return render_template('admin/display_activity.html', table=table)


@main.route('/facilities/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def display_facility(id):
    facilities = db.session.query(Facility).all()

    if not facilities:
        flash('No results found!')
        return redirect('/')
    else:
        table = FacilityTable(facilities)
        table.border = True
        return render_template('admin/display_facility.html', table=table)
