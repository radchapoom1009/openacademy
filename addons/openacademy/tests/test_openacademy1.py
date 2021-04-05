import pytest
from pytest_tr_odoo.fixtures import env
from pytest_tr_odoo import utils
from odoo import exceptions

@pytest.fixture
def oo_model(env):
    return env['openacademy.openacademy']


@pytest.fixture
def os_model(env):
    return env['openacademy.session']


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'TurtleheadsAitch'
    })


@pytest.mark.parametrize('test_input, expected', [
    ({'first_name': 'Radchapoom',
        'last_name': 'katechode',
        'value': 10}, 'Radchapoom katechode'),
])
def test_comput_full_name(oo_model, test_input, expected):
    openacademy = oo_model.create(test_input)
    assert openacademy.full_name == expected


@pytest.fixture
def openacademy(oo_model):
    return oo_model.create({
            'first_name': 'Radchapoom',
            'last_name': 'katechode',
            'value': 10,
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 0}, 'Copy of katechode'),
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 1}, 'Copy of katechode (1)'),
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 2}, 'Copy of katechode (2)'),
])
def test_copy_last_name(openacademy, test_input, expected):
    for l in range(test_input['count']):
        openacademy.copy()
    assert openacademy._copy_last_name() == expected


@pytest.mark.parametrize('test_input, expected', [
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 0}, 'Copy of katechode'),
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 1}, 'Copy of katechode (1)'),
    ({'first_name': 'Radchapoom', 'last_name': 'katechode', 'value': 10,
        'count': 2}, 'Copy of katechode (2)'),
])
def test_copy(monkeypatch, mocker, openacademy, test_input, expected):
    monkeypatch.setattr(type(openacademy), '_copy_last_name', lambda a: 'Copy')
    spy = mocker.spy(type(openacademy), '_copy_last_name')
    data = openacademy.copy()
    assert spy.called
    assert data.last_name == 'Copy'


@pytest.fixture
def session(os_model):
    return os_model.create({
        'name': 'Incitement'
    })


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Incitement', 'start_date': '2021-01-01'},
        '2021-01-01'),
    ({'name': 'Reconsign', 'start_date': '2021-01-01', 'duration': 1},
        '2021-01-01'),
    ({'name': 'Convents', 'start_date': '2021-01-01', 'duration': 3},
        '2021-01-03'),
    ])
def test_compute_end_date(os_model, test_input, expected):
    session = os_model.create(test_input)
    print("test_compute_end_date =============> :", session.end_date.strftime(
        '%Y-%m-%d'))
    assert session.end_date.strftime('%Y-%m-%d') == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Sestons', 'start_date': False, 'end_date': '2021-01-01'},
     False),
    ({'name': 'Pushdowns', 'start_date': '2021-01-01',
      'end_date': '2021-01-01'},
     1),
    ({'name': 'Redoubtableness', 'start_date': '2021-01-01',
      'end_date': '2021-01-03'},
     3),
])
def test_inverse_end_date(os_model, test_input, expected):
    session = os_model.create(test_input)
    print("test_inverse_end_date =============> :", session.duration, expected)
    assert session.duration == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Gleeni', 'duration': 1},
     24),
    ({'name': 'Uncombative', 'duration': 3},
     72),
])
def test__compute_hours(os_model, test_input, expected):
    session = os_model.create(test_input)
    print("test__compute_hours =============> :", session.hours, expected)
    assert session.hours == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Gleeni', 'hours': 24},
     1),
    ({'name': 'Uncombative', 'hours': 72},
     3),
])
def test_inverse_hours(os_model, test_input, expected):
    session = os_model.create(test_input)
    print("test_inverse_hours =============> :", session.duration, expected)
    assert session.duration == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Inevitables', 'seats': -1,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable@gmail.com'})]}, 0.0),
    ({'name': 'Inevitables', 'seats': 0,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable46@gmail.com'})]}, 0.0),
    ({'name': 'Inevitables', 'seats': 10,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable46@gmail.com'})]}, 10.0),
])
def test_compute_taken_seats(os_model, test_input, expected):
    session = os_model.create(test_input)
    print("test_compute_taken_seats ======> :", session.taken_seats, expected)
    assert session.taken_seats == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Inevitables', 'seats': -1,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable@gmail.com'})]},
     {'warning': {
         'title': 'Incorrect \'seats\' value',
         'message': 'The number of available seatsmay not be negative'
         }}),

    ({'name': 'Inevitables', 'seats': 0,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable@gmail.com'})]},
     {'warning': {
         'title': 'Too many attendees',
         'message': 'Increase seats or remove excess attendees'
         }}),

    ({'name': 'Inevitables', 'seats': 2,
      'attendee_ids': [(0, 0,
                        {'name': 'Opportunisms Redemptory',
                         'email': 'Debateable@gmail.com'}),
                       (0, 0,
                        {'name': 'Opportunismsv2 Redemptory',
                            'email': 'Debateable@gmail.com'})]},
     False),
])
def test_verify_valid_seats(os_model, test_input, expected):
    session = os_model.create(test_input)
    verify_valid_seats = session._verify_valid_seats()
    if verify_valid_seats:
        assert verify_valid_seats == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Plastic', 'seats': 10,
      'attendee_ids': []}, 'A session\'s instructor can\'t be an attendee')
])
def test_check_instructor_not_in_attendees(os_model,
                                           partner,
                                           test_input, expected):
    test_input['instructor_id'] = partner.id
    test_input['attendee_ids'].append((4, partner.id))
    with pytest.raises(exceptions.ValidationError) as excinfo:
        os_model.create(test_input)
    print("test_check_instructor_not_in_attendees ======>:", excinfo.value)
    assert excinfo.value.name == expected