import pytest
from datetime import datetime
from pytest_tr_odoo.fixtures import env
from pytest_tr_odoo import utils
from .test_openacademy import session_model, session


@pytest.fixture
def wizard_model(env):
    return env['openacademy.wizard']


'''
openacademy.wizard
'''


def test_default_session(wizard_model, session):
    wizard = wizard_model.with_context({'active_id': session.id}).create({})
    assert wizard.session_id == session


@pytest.mark.parametrize('test_input,expected', [
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'})]},
     ['liana46@gmail.com']),
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'liana46@gmail.com'}),
                       (0, 0,
                        {'name': 'Elsie Gulgowski',
                         'email': 'kirstin8@hotmail.com'})]},
     ['liana46@gmail.com', 'kirstin8@hotmail.com']),
])
def test_subscribe(wizard_model, session, test_input, expected):
    wizard = wizard_model\
        .with_context({'active_id': session.id})\
        .create(test_input)
    wizard.subscribe()

    def validate(value):
        assert value in expected
    map(validate, session.attendee_ids.mapped('email'))
