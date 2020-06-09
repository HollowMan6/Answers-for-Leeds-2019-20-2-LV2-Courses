import datetime

from flask import render_template, redirect, url_for, abort, flash, request, current_app
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, MembershipForm, PoolBookingForm, \
    FitnessBookingForm, SquashBookingForm, HallBookingForm, CardForm, RefundForm, ConfigureActivityForm, \
    ConfigureTimetableForm, \
    ConfigureFacilityForm, SearchForm
from .. import db
from ..models import Role, User, Facility, Membership, Account, Activity, Time_management, Booking, Credit_card_info, \
    Membership_type, Permission
from ..decorators import admin_required, permission_required
from ..email import send_email, str_to_pdf
import qrcode
import pdfkit


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/facility')
def facility():
    facilities = Facility.query.all()
    '''for facility in facilities:
        print(facility.name)'''
    return render_template('facility.html', facilities=facilities)


@main.route('/facility_info/<int:id>')
def view_info(id):
    facility = Facility.query.filter_by(id=id).first()
    return render_template('facility_info.html', facility=facility)


@main.route('/membership')
def view_membership_type():
    memberships = Membership_type.query.all()
    for membership in memberships:
        print(membership.length)
    return render_template('membership.html', memberships=memberships)


@main.route('/my_bookings/<int:id>')
@login_required
@permission_required(Permission.DISPLAY)
def display_bookings(id):
    account = Account.query.filter_by(user_id=id).first()
    bookings = Booking.query.order_by(Booking.timestamp.desc()).filter_by(account_id=account.id).all()
    number = Booking.query.order_by(Booking.timestamp.desc()).filter_by(account_id=account.id).count()
    facilities = Facility.query.all()
    timetable_booking = []
    for booking in bookings:
        timetable = Time_management.query.filter_by(id=booking.time_id).first()
        timetable_booking.append(timetable)

    return render_template('my_booking.html', number=number, bookings=bookings, timetable_booking=timetable_booking,
                           facilities=facilities)


@main.route('/my_card/<int:id>')
@login_required
@permission_required(Permission.DISPLAY)
def display_cards(id):
    account = Account.query.filter_by(user_id=id).first()
    cards = Credit_card_info.query.filter_by(account_id=account.id).all()
    number = Credit_card_info.query.filter_by(account_id=account.id).count()
    return render_template('my_card.html', cards=cards, number=number)


@main.route('/remove_card/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.DISPLAY)
def remove_card(id):
    card = Credit_card_info.query.get_or_404(id)
    db.session.delete(card)
    db.session.commit()
    flash('Successfully remove a card.')
    # The function will go to all function and render the template index.heml
    return redirect(url_for('.display_cards', id=current_user.id))


@main.route('/my_membership/<int:id>')
@login_required
@permission_required(Permission.DISPLAY)
def display_membership(id):
    account = Account.query.filter_by(user_id=id).first()
    membership = Membership.query.filter_by(account_id=account.id).first()
    membership_type = Membership_type.query.filter_by(id=membership.membership_type_id).first()
    number = Membership.query.filter_by(account_id=account.id).count()
    return render_template('my_membership.html', membership=membership, membership_type=membership_type, number=number)


@main.route('/pricing_list')
def display_pricing_list():
    facilities = Facility.query.all()
    activities = Activity.query.all()
    return render_template('pricing_list.html', facilities=facilities, activities=activities)


@main.route('/timetable_all/<int:date>/<int:offset>')
def timetable_all(date, offset):
    if date == 2 and offset == 0:
        date = 0
    if date == 2:
        date = -1
    newdate = offset + date
    new_date = datetime.date.today() + datetime.timedelta(days=newdate)
    offset += date

    timetables = Time_management.query.filter_by(date=new_date).all()
    facilities = Facility.query.all()

    return render_template('timetable_all.html', offset=offset, timetables=timetables, facilities=facilities,
                           new_date=new_date)

@main.route('/timetable_facility/<int:type>')
def timetable_facility(type):
    if type == 1:
        type = type + 1
        facility = "Swimming pool"
    elif type == 2:
        type = type + 1
        facility = "Fitness room"
    elif type == 3:
        type = type + 1
        facility = "Squash courts"
    else:
        type = 1
        facility = "Sports hall"

    facility = Facility.query.filter_by(name=facility).first()
    today = datetime.date.today()
    day2 = today + datetime.timedelta(days=1)
    day3 = today + datetime.timedelta(days=2)
    day4 = today + datetime.timedelta(days=3)
    day5 = today + datetime.timedelta(days=4)
    timetable1 = Time_management.query.filter_by(date=today).all()
    timetable2 = Time_management.query.filter_by(date=day2).all()
    timetable3 = Time_management.query.filter_by(date=day3).all()
    timetable4 = Time_management.query.filter_by(date=day4).all()
    timetable5 = Time_management.query.filter_by(date=day5).all()
    return render_template('timetable_facility.html', type=type, today=today, day3=day3, day2=day2, day4=day4,
                           day5=day5, facility=facility, timetable1=timetable1, timetable2=timetable2,
                           timetable3=timetable3, timetable4=timetable4, timetable5=timetable5)


@main.route('/book_facility/<int:type>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.PAY)
def book_facility(type):
    if type == 1:
        form = PoolBookingForm()
    elif type == 2:
        form = FitnessBookingForm()
    elif type == 3:
        form = SquashBookingForm()
    else:
        form = HallBookingForm()

    if form.validate_on_submit():
        '''activity = form.activity.data
        number = form.number.data
        date = form.date.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        payment = form.payment.data'''

        fac = Facility.query.filter_by(id=type).first()
        account = Account.query.filter_by(user_id=current_user.id).first()
        for booking in account.bookings:
            book_timetable = Time_management.query.filter_by(id=booking.time_id).first()
            if book_timetable.date == form.date.data:
                flash("You can only have exactly one booking each day")
                return redirect(url_for('.book_facility', type=type))

        if form.end_time.data - form.start_time.data != 1:
            flash('You can only book a 1-hour session')
            return redirect(url_for('.book_facility', type=type))

        timetables = Time_management.query.filter_by(facility_id=type).all()
        for timetable in timetables:
            if form.start_time.data == timetable.start_time and form.date.data ==timetable.date:
                time_id = timetable.id

        timetable_booking = Time_management.query.filter_by(id=time_id).first()
        if form.number.data + timetable_booking.current_capacity > fac.capacity:
            flash('Your have too many people!')
            return redirect(url_for('.book_facility', type=type))

        else:
            account = Account.query.filter_by(user_id=current_user.id).first()
            for activity in fac.activities:
                print(activity.activity_name)
                if activity.activity_name == form.activity.data:
                    fees=activity.activity_price
                    activity_id=activity.id

            booking = Booking(number=form.number.data,
                              time_id=time_id,
                              account_id=account.id,
                              activity=form.activity.data,
                              activity_id=activity_id,
                              status="Unpaid",
                              payment=form.payment.data,
                              fees=fees)
            db.session.add(booking)
            db.session.commit()

            book = Booking.query.order_by(Booking.timestamp.desc()).filter_by(account_id=account.id).first_or_404()

            timetable_booking.current_capacity = form.number.data + timetable_booking.current_capacity
            db.session.add(timetable_booking)
            db.session.commit()

            if form.payment.data == "Credit Card":
                flash('Pay for your booking.')
                return redirect(url_for('.handle_card_booking', book_id=book.id))
            elif form.payment.data == "Cash":
                flash('You will pay for your booking by cash.')
                return redirect(url_for('.index'))

    return render_template('book_facility.html', form=form)

@main.route('/handle_card_booking/<int:book_id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.HANDLE)
def handle_card_booking(book_id):
    account = Account.query.filter_by(user_id=current_user.id).first()
    card = Credit_card_info.query.filter_by(account_id=account.id).first()
    book = Booking.query.filter_by(id=book_id).first()
    time = Time_management.query.filter_by(id=book.time_id).first()
    form = CardForm()

    if form.validate_on_submit():
        length = len(str(form.card_number.data))
        length_year = len(str(form.expire_year.data))
        length_code = len(str(form.security_code.data))

        if card is None or card.card_number != form.card_number.data:
            if length != 16:
                flash("Your card number should have 16 numbers.")
                return redirect(url_for(".handle_card_booking", book_id=book_id))
            if form.expire_month.data > 12 or form.expire_month.data < 1:
                flash("Your expire month is invalid.")
                return redirect(url_for(".handle_card_booking", book_id=book_id))
            if length_year != 4:
                flash("Your expire year is invalid.")
                return redirect(url_for(".handle_card_booking", book_id=book_id))
            if length_code != 3:
                flash("Your security code is invalid.")
                return redirect(url_for(".handle_card_booking", book_id=book_id))

            card_info = Credit_card_info(card_number=form.card_number.data,
                                         expire_month=form.expire_month.data,
                                         expire_year=form.expire_year.data,
                                         security_code=form.security_code.data,
                                         holder_name=form.holder_name.data,
                                         account_id=account.id
                                         )
            db.session.add(card_info)
            db.session.commit()
        book.status = "Paid"
        db.session.add(book)
        db.session.commit()

        act = Activity.query.filter_by(id=book.activity_id).first()
        act.weekly_income = act.weekly_income + book.fees
        act.weekly_usage = act.weekly_usage + book.number
        db.session.add(act)
        db.session.commit()

        receipt = "Receipt:\n" + "Payer:" + current_user.username + "\n" + "item:" + book.activity + "\n" + "Fees:" + str(
            book.fees) + "\n" + book.timestamp.strftime('%Y-%m-%d %H:%M:%S') + "\n"
        pdf_name = 'app/static/' + str(book.id) + '.pdf'
        str_to_pdf(receipt, pdf_name)

        img = qrcode.make(receipt)
        img.save("app/static/receipt.jpg")
        send_email(current_user.email, 'Your booking receipt',
                   'booking_receipt', book=book, time=time)

        flash('A booking receipt has been sent to you by email.')
        return redirect(url_for("main.index"))
    if card is not None:
        form.card_number.data = card.card_number
        form.expire_month.data = card.expire_month
        form.expire_year.data = card.expire_year
        form.security_code.data = card.security_code
        form.holder_name.data = card.holder_name
    return render_template('handle_card_booking.html', book=book, time=time, form=form)


@main.route('/cancel_booking/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CANCEL)
def cancel_booking(id):
    booking = Booking.query.filter_by(id=id).first()
    time = Time_management.query.filter_by(id=booking.time_id).first()
    if booking.status == "Unpaid":
        db.session.delete(booking)
        db.session.commit()
        return redirect(url_for('main.display_bookings', id=current_user.id))
    else:
        form = RefundForm()
        if form.validate_on_submit():
            time.current_capacity = time.current_capacity - booking.number
            db.session.add(time)
            db.session.commit()
            db.session.delete(booking)
            db.session.commit()
            activity = Activity.query.filter_by(activity_name=booking.activity).first()
            activity.weekly_usage = activity.weekly_usage - booking.number
            activity.weekly_income = activity.weekly_income - booking.fees
            db.session.add(activity)
            db.session.commit()
            return redirect(url_for('main.display_bookings', id=current_user.id))

    return render_template('cancel_booking.html', form=form, booking=booking, time=time)


@main.route('/pay_membership/<int:type_id>', methods=['GET', 'POST'])
@login_required
def pay_membership(type_id):
    membership_type = Membership_type.query.filter_by(id=type_id).first()
    account = Account.query.filter_by(user_id=current_user.id).first()
    form = MembershipForm()
    if form.validate_on_submit():
        membership = Membership(title=form.title.data,
                                status="Unpaid",
                                firstname=form.firstname.data,
                                lastname=form.lastname.data,
                                account_id=account.id,
                                membership_type_id=membership_type.id
                                )
        db.session.add(membership)
        db.session.commit()

        membership = Membership.query.filter_by(account_id=account.id).first()
        if (membership_type.length == 1):
            length = 30
        elif (membership_type.length == 3):
            length = 90
        else:
            length = 365
        membership.valueOfEnd_date(length)
        db.session.commit()

        if form.payment.data == "Credit Card":
            flash('Pay for your booking.')
            return redirect(url_for('.handle_card_membership', id=account.id))
        elif form.payment.data == "Cash":
            flash('You will pay for your booking by cash.')
            return redirect(url_for('.index'))

    return render_template('pay_membership.html', form=form, membership_type=membership_type)


@main.route('/handle_card_membership/<int:id>', methods=['GET', 'POST'])
@login_required
def handle_card_membership(id):
    membership = Membership.query.filter_by(account_id=id).first()
    card = Credit_card_info.query.filter_by(account_id=id).first()
    form = CardForm()
    membership_type = Membership_type.query.filter_by(id=membership.membership_type_id).first()
    price = membership_type.price
    if form.validate_on_submit():
        card_info = Credit_card_info(card_number=form.card_number.data,
                                     expire_month=form.expire_month.data,
                                     expire_year=form.expire_year.data,
                                     security_code=form.security_code.data,
                                     holder_name=form.holder_name.data,
                                     account_id=id
                                     )
        db.session.add(card_info)
        db.session.commit()
        membership.status = "Paid"
        db.session.add(membership)
        db.session.commit()
        return redirect(url_for('main.index'))

    if card is not None:
        form.card_number.data = card.card_number
        form.expire_month.data = card.expire_month
        form.expire_year.data = card.expire_year
        form.security_code.data = card.security_code
        form.holder_name.data = card.holder_name

    return render_template('handle_card_membership.html', price=price, form=form)


@main.route('/configure_facility', methods=['GET', 'POST'])
@login_required
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
            return redirect(url_for('main.index'))

        elif operation == "edit":
            fac = Facility.query.filter_by(name=name).first()
            fac.capacity = capacity
            fac.url = url
            fac.description = description

            db.session.add(fac)
            db.session.commit()
            flash('You have edited the facility')
            return redirect(url_for('main.index'))

        elif operation == "delete":
            fac = Facility.query.filter_by(name=name).first()
            db.session.delete(fac)
            db.session.commit()
            flash('You have deleted the facility')
            return redirect(url_for('main.index'))

    return render_template('configure_facility.html', form=form)


@main.route('/configure_activity', methods=['GET', 'POST'])
@login_required
def configure_activity():
    form = ConfigureActivityForm()
    if form.validate_on_submit():

        fac = Facility.query.filter_by(name=form.facility.data).first()
        if form.operation.data == "add":
            act = Activity(weekly_income=0,
                           weekly_usage=0,
                           activity_price=form.price.data,
                           activity_name=form.activity.data,
                           facility_id=fac.id
                           )
            db.session.add(act)
            db.session.commit()
            flash('You have added the activity')
            return redirect(url_for('main.index'))

        elif form.operation.data == "edit":
            act = Activity.query.filter_by(activity_name=form.activity.data).first()
            act.activity_price = form.price.data,
            act.activity_name = form.activity.data
            act.facility_id = fac.id

            db.session.add(act)
            db.session.commit()
            flash('You have edited the activity')
            return redirect(url_for('main.index'))

        elif form.operation.data == "delete":
            act = Activity.query.filter_by(activity_name=form.activity.data).first()
            db.session.delete(act)
            db.session.commit()
            flash('You have deleted the activity')
            return redirect(url_for('main.index'))

    return render_template('configure_activity.html', form=form)


@main.route('/configure_timetable', methods=['GET', 'POST'])
@login_required
def configure_timetable():
    form = ConfigureTimetableForm()
    if form.validate_on_submit():
        fac = Facility.query.filter_by(name=form.facility.data).first()

        if fac is None:
            flash("The facility is not existed")
            return redirect(url_for("main.configure_timetable"))

        for i in range(form.start_time.data, form.end_time.data):
            timetable = Time_management(date=form.date.data,
                                        start_time=i,
                                        end_time=i + 1,
                                        facility_id=fac.id)
            db.session.add(timetable)
            db.session.commit()
        flash("Sucessful operation!")
        return redirect(url_for('main.index'))
    return render_template('configure_timetable.html', form=form)


@main.route('/cancel_membership/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CANCEL)
def cancel_membership(id):
    membership = Membership.query.filter_by(id=id).first()
    timedelta = membership.end_date - datetime.datetime.utcnow()
    days_left = timedelta.days
    money_refund = timedelta.days * 0.5
    form = RefundForm()
    if form.validate_on_submit():
        db.session.delete(membership)
        db.session.commit()
        flash('You have cancelled our membership!')
        return redirect(url_for('main.display_membership', id=current_user.id))
    return render_template('cancel_membership.html', money_refund=money_refund, days_left=days_left,
                           membership=membership, form=form)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/search_booking', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CANCEL)
def search_booking():
    form = SearchForm()
    if form.validate_on_submit():
        email = form.email.data

        user = User.query.filter_by(email=email).first()
        return redirect(url_for('main.display_bookings', id=user.id))
    return render_template('search_booking.html', form=form)


@main.route('/search_membership', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.CANCEL)
def search_membership():
    form = SearchForm()
    if form.validate_on_submit():
        email = form.email.data

        user = User.query.filter_by(email=email).first()
        return redirect(url_for('main.display_membership', id=user.id))
    return render_template('search_membership.html', form=form)


@main.route('/view_income')
@login_required
def view_income():
    session1_income, session2_income, session3_income, session4_income, session5_income, session6_income, session14_income = 0, 0, 0, 0, 0, 0, 0
    session7_income, session8_income, session9_income, session10_income, session11_income, session12_income, session13_income = 0, 0, 0, 0, 0, 0, 0
    session1_usage, session2_usage, session3_usage, session4_usage, session5_usage, session6_usage, session14_usage = 0, 0, 0, 0, 0, 0, 0
    session7_usage, session8_usage, session9_usage, session10_usage, session11_usage, session12_usage, session13_usage = 0, 0, 0, 0, 0, 0, 0
    time8 = Time_management.query.filter_by(start_time=8).all()
    for timetable in time8:
        for booking in timetable.bookings:
            session1_income += booking.fees
            session1_usage += booking.number

    time9 = Time_management.query.filter_by(start_time=9).all()
    for timetable in time9:
        for booking in timetable.bookings:
            session2_income += booking.fees
            session2_usage += booking.number

    time10 = Time_management.query.filter_by(start_time=10).all()
    for timetable in time10:
        for booking in timetable.bookings:
            session3_income += booking.fees
            session3_usage += booking.number

    time11 = Time_management.query.filter_by(start_time=11).all()
    for timetable in time11:
        for booking in timetable.bookings:
            session4_income += booking.fees
            session4_usage += booking.number

    time12 = Time_management.query.filter_by(start_time=12).all()
    for timetable in time12:
        for booking in timetable.bookings:
            session5_income += booking.fees
            session5_usage += booking.number

    time13 = Time_management.query.filter_by(start_time=13).all()
    for timetable in time13:
        for booking in timetable.bookings:
            session6_income += booking.fees
            session6_usage += booking.number

    time14 = Time_management.query.filter_by(start_time=14).all()
    for timetable in time14:
        for booking in timetable.bookings:
            session7_income += booking.fees
            session7_usage += booking.number

    time15 = Time_management.query.filter_by(start_time=15).all()
    for timetable in time15:
        for booking in timetable.bookings:
            session8_income += booking.fees
            session8_usage += booking.number

    time16 = Time_management.query.filter_by(start_time=16).all()
    for timetable in time16:
        for booking in timetable.bookings:
            session9_income += booking.fees
            session9_usage += booking.number

    time17 = Time_management.query.filter_by(start_time=17).all()
    for timetable in time17:
        for booking in timetable.bookings:
            session10_income += booking.fees
            session10_usage += booking.number

    time18 = Time_management.query.filter_by(start_time=18).all()
    for timetable in time18:
        for booking in timetable.bookings:
            session11_income += booking.fees
            session11_usage += booking.number

    time19 = Time_management.query.filter_by(start_time=19).all()
    for timetable in time19:
        for booking in timetable.bookings:
            session12_income += booking.fees
            session12_usage += booking.number

    time20 = Time_management.query.filter_by(start_time=20).all()
    for timetable in time20:
        for booking in timetable.bookings:
            session13_income += booking.fees
            session13_usage += booking.number

    time21 = Time_management.query.filter_by(start_time=21).all()
    for timetable in time21:
        for booking in timetable.bookings:
            session14_income += booking.fees
            session14_usage += booking.number

    overall_income = 0
    overall_usage = 0
    activities = Activity.query.all()
    for activity in activities:
        overall_income += activity.weekly_income
        overall_usage += activity.weekly_usage
    return render_template('business.html', session14_usage=session14_usage, session14_income=session14_income,
                           session13_usage=session13_usage, session13_income=session13_income,
                           session12_usage=session12_usage, session12_income=session12_income,
                           session11_usage=session11_usage, session11_income=session11_income,
                           session10_usage=session10_usage, session10_income=session10_income,
                           session9_usage=session9_usage, session9_income=session9_income,
                           session8_usage=session8_usage, session8_income=session8_income,
                           session7_usage=session7_usage, session7_income=session7_income,
                           session6_usage=session6_usage,
                           session6_income=session6_income, session5_usage=session5_usage,
                           session5_income=session5_income, session4_usage=session4_usage,
                           session4_income=session4_income,
                           session3_usage=session3_usage, session3_income=session3_income,
                           session2_usage=session2_usage, session2_income=session2_income,
                           session1_usage=session1_usage, session1_income=session1_income,
                           overall_income=overall_income, overall_usage=overall_usage, activities=activities)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
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
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('edit_profile.html', form=form, user=user)
