"""Message model tests"""

import os
from unittest import TestCase

from models import db, User, Message, Like


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

        msg1 = Message(text = "Msg1", user_id = self.u1_id)
        msg2 = Message(text = "Msg2", user_id = self.u2_id)

        db.session.add(msg1)
        db.session.add(msg2)
        db.session.commit()

        self.msg1_id = msg1.id
        self.msg2_id = msg2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Test Message is created"""
        msg1 = Message.query.get(self.msg1_id)

        self.assertEqual(msg1.user_id, self.u1_id)
        self.assertIn("Msg1", msg1.text)

    def test_is_liked(self):
        """Test is_liked function"""
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        msg1 = Message.query.get(self.msg1_id)
        msg2 = Message.query.get(self.msg2_id)

        u1.likes.append(msg2)
        db.session.commit()

        liked_msg = msg2.is_liked(u1)
        unliked_msg = msg1.is_liked(u2)

        self.assertTrue(liked_msg)
        self.assertFalse(unliked_msg)

    def test_message_liked(self):

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        msg1 = Message.query.get(self.msg1_id)
        msg2 = Message.query.get(self.msg2_id)

        # are we making a new instance of Like?
        u1.likes.append(msg2)
        db.session.commit()

        fav_list = msg2.users

        self.assertIsInstance(fav_list, list)
        self.assertIn(u1, fav_list)

