import pytest
from odoo import exceptions
from pytest_tr_odoo.fixtures import env
from pytest_tr_odoo import utils


@pytest.fixture
def openacademy_model(env):
    return env['openacademy.openacademy']


@pytest.fixture
def session_model(env):
    return env['openacademy.session']


@pytest.fixture
def session(session_model):
    return session_model.create({
        'name': 'bypass'
    })


@pytest.fixture
def partner(env):
    return env['res.partner'].create({
        'name': 'Joey Cronin III'
    })

'''
openacademy.openacademy
'''


@pytest.mark.parametrize('test_input,expected', [
    ({'first_name': 'Kyle', 'last_name': 'Bogan', 'value': 10}, 'Kyle Bogan'),
    ({'first_name': 'Nickolas', 'last_name': 'Pacocha', 'value': 2},
     'Nickolas Pacocha'),
    ({'first_name': 'Keon', 'last_name': 'Lemke', 'value': 4}, 'Keon Lemke')
])
def test_compute_full_name(openacademy_model, test_input, expected):
    openacademy = openacademy_model.create(test_input)
    assert openacademy.full_name == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'first_name': 'Kyle', 'last_name': 'Bogan', 'value': 10, 'repeat': 0},
     'Copy of Bogan'),
    ({'first_name': 'Kyle', 'last_name': 'Bogan', 'value': 4, 'repeat': 1},
     'Copy of Bogan (1)'),
    ({'first_name': 'Kyle', 'last_name': 'Bogan', 'value': 1, 'repeat': 2},
     'Copy of Bogan (2)'),
    ({'first_name': 'Dino', 'last_name': 'Green', 'value': 7, 'repeat': 0},
     'Copy of Green'),
    ({'first_name': 'Aliza', 'last_name': 'Green', 'value': 4, 'repeat': 1},
     'Copy of Green (1)'),
    ({'first_name': 'Hugh', 'last_name': 'Green', 'value': 32, 'repeat': 2},
     'Copy of Green (2)')
])
def test_copy_last_name(openacademy_model, test_input, expected):
    repeat = test_input['repeat']
    del test_input['repeat']
    openacademy = openacademy_model.create(test_input)
    for i in range(repeat):
        openacademy.copy()
    copy_last_name = openacademy._copy_last_name()
    assert copy_last_name == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'first_name': 'Kyle', 'last_name': 'Bogan', 'value': 10},
     {'first_name': 'Kyle', 'last_name': 'Copy of Bogan', 'value': 10}),
    ({'first_name': 'Cheyenne', 'last_name': 'Erdman', 'value': 2},
     {'first_name': 'Cheyenne', 'last_name': 'Copy of Erdman', 'value': 2})
])
def test_copy(monkeypatch, openacademy_model, test_input, expected):
    monkeypatch.setattr(type(openacademy_model), '_copy_last_name',
                        lambda x: 'Copy of %s' % test_input['last_name'])
    openacademy = openacademy_model.create(test_input)
    copy_openacademy = openacademy.copy()

    def validate_value(key):
        assert getattr(copy_openacademy, key, False) == expected[key]
    map(validate_value, expected.keys())


'''
openacademy.session
'''


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'bypass', 'start_date': '2020-01-01'},
     '2020-01-01'),
    ({'name': 'Lead', 'start_date': '2020-01-01', 'duration': 1},
     '2020-01-01'),
    ({'name': 'Loan', 'start_date': '2020-01-01', 'duration': 2},
     '2020-01-02'),
    ({'name': 'Direct', 'start_date': '2020-01-01', 'duration': 10},
     '2020-01-10'),
])
def test_compute_end_date(session_model, test_input, expected):
    session = session_model.create(test_input)
    assert session.end_date.strftime('%Y-%m-%d') == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Plastic', 'start_date': False, 'end_date': '2020-01-01'},
     False),
    ({'name': 'Bedfordshire', 'start_date': '2020-01-01',
      'end_date': '2020-01-01'},
     1),
    ({'name': 'Bedfordshire', 'start_date': '2020-01-01',
      'end_date': '2020-01-02'},
     2),
    ({'name': 'Bedfordshire', 'start_date': '2020-01-01',
      'end_date': '2020-01-10'},
     10),
])
def test_inverse_end_date(session_model, test_input, expected):
    session = session_model.create(test_input)
    assert session.duration == expected


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Plastic', 'seats': -10,
      'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'})]},
     {'warning': {
         'title': 'Incorrect \'seats\' value',
         'message': 'The number of available seatsmay not be negative'
         }}),
    ({'name': 'Plastic', 'seats': 0,
      'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'})]},
     {'warning': {
         'title': 'Too many attendees',
         'message': 'Increase seats or remove excess attendees'
         }}),
    ({'name': 'Plastic', 'seats': 1,
      'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'})]},
     False),
    ({'name': 'Plastic', 'seats': 12,
      'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'})]},
     False),
])
def test_verify_valid_seats(session_model, test_input, expected):
    session = session_model.create(test_input)
    verify = session._verify_valid_seats()

    if expected:
        assert verify == expected
    else:
        assert not verify


@pytest.mark.parametrize('test_input,expected', [
    ({'name': 'Plastic', 'seats': 12,
      'attendee_ids': []}, 'A session\'s instructor can\'t be an attendee')
])
def test_check_instructor_not_in_attendees(session_model,
                                           partner,
                                           test_input, expected):
    test_input['instructor_id'] = partner.id
    test_input['attendee_ids'].append((4, partner.id))
    with pytest.raises(exceptions.ValidationError) as excinfo:
        session_model.create(test_input)
    assert excinfo.value.name == expected
