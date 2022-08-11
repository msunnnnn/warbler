"""Message model tests"""

import os
from unittest import TestCase

from models import db, User, Message, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        msg1 = Message(text = "Msg1", user_id = 1)
        msg2 = Message(text = "Msg2", user_id = 2)

        db.session.add_all([msg1, msg2])
        db.session.commit()

        self.msg1_id = msg1.id
        self.msg2_id = msg2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        msg1 = Message.query.get(self.msg1_id)

        self.assertEqual(msg1.user_id, self.u1_id)
        self.assertIn("Msg1", msg1.text)


