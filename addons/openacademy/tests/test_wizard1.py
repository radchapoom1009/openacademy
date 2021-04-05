import pytest
from datetime import datetime
from pytest_tr_odoo.fixtures import env
from pytest_tr_odoo import utils
from .test_openacademy1 import os_model, session


@pytest.fixture
def ow_model(env):
    return env['openacademy.wizard']

def test_default_session(ow_model, session):
    wizard = ow_model.with_context({'active_id': session.id}).create({})
    assert wizard.session_id == session


@pytest.mark.parametrize('test_input,expected', [
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'Debateable@gmail.com'})]},
     ['Debateable@gmail.com']),
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'Debateable@gmail.com'}),
                       (0, 0,
                        {'name': 'Rough Secretaries',
                         'email': 'Secretaries.com'})]},
     ['Debateable@gmail.com', 'Secretaries.com']),
])
def test_subscribe(ow_model, session, test_input, expected):
    wizard = ow_model\
        .with_context({'active_id': session.id})\
        .create(test_input)
    wizard.subscribe()
    for value in session.attendee_ids.mapped('email'):
        assert value in expected


@pytest.fixture
def omw_model(env):
    return env['openacademy.multi_wizard']


def test_omw_default_session(omw_model, session):
    wizard = omw_model.with_context({'active_ids': session.id}).create({})
    assert wizard.session_ids == session


@pytest.mark.parametrize('test_input,expected', [
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'Debateable@gmail.com'})]},
     {}),
    ({'attendee_ids': [(0, 0,
                        {'name': 'Grant Ritchie',
                         'email': 'Debateable@gmail.com'}),
                       (0, 0,
                        {'name': 'Rough Secretaries',
                         'email': 'Secretaries.com'})]},
     {}),
])
def test_omw_subscribe(omw_model, session, test_input, expected):
    wizard = omw_model\
        .with_context({'active_ids': session.id})\
        .create(test_input)
    subscribe = wizard.subscribe()
    print('test_omw_subscribe =====>',wizard.subscribe())
    assert subscribe == expected
