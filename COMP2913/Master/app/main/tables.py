from flask_table import Table, Col, LinkCol


class ActivityTable(Table):
    id = Col('Id', show=False)
    activity_name = Col('Name')
    activity_price = Col('Price')
    repeat_every = Col('Repeat')
    activity_staff_id = Col('Staff ID number')
    facility_id = Col('Facility Id')
    edit = LinkCol('Edit', 'edit_actvitiy', url_kwargs=dict(id='id'))


class FacilityTable(Table):
    id = Col('Id', show=False)
    name = Col('Name')
    capacity = Col('Capacity')
    description = Col('Description')
    courts = Col('Courts')
    activities = Col('Activities')
    edit = LinkCol('Edit', 'edit_facility', url_kwargs=dict(id='id'))
