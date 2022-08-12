"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.u3_id = u3.id

        u1.following.append(u3)
        db.session.commit()

        m1 = Message(text="m1-text", user_id=u1.id)
        m2 = Message(text="m1-text", user_id=u2.id)
        db.session.add_all([m1,m2])
        db.session.commit()

        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()


class MessageAddViewTestCase(MessageBaseViewTestCase):
    def test_add_message(self):
        """Tests add message if user is in session"""
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            good_resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(good_resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()

    def test_invalid_add_message(self):
        """Tests add message if user is not in session"""
        with self.client as c:
            bad_resp = c.post("/messages/new",
                data={"text": "Hello", "user_id" : self.u2_id},
                follow_redirects = True)
            bad_html = bad_resp.get_data(as_text = True)

            self.assertEqual(bad_resp.status_code, 200)
            self.assertIn("Access unauthorized.", bad_html)

    def test_show_message(self):
        """Tests show messages"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp= c.get(f'/messages/{self.m1_id}')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("m1-text", html)

    def test_delete_message(self):
        """Tests delete message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp= c.post(f'/messages/{self.m1_id}/delete',
                        follow_redirects= True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show user", html)

    def test_like_message(self):
        """Tests liking message"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            liked_resp= c.post(f'/messages/{self.m2_id}/like',
                                follow_redirects= True)
            liked_html = liked_resp.get_data(as_text = True)

            self.assertEqual(liked_resp.status_code, 200)
            self.assertIn("test homepage", liked_html)

            u1 = User.query.get(self.u1_id)
            msg2 = Message.query.get(self.m2_id)
            self.assertIn(msg2, u1.likes)


            unliked_resp = c.post(f'/messages/{self.m2_id}/like',
                               follow_redirects= True)
            unliked_html = unliked_resp.get_data(as_text = True)

            self.assertEqual(unliked_resp.status_code, 200)
            self.assertIn("test homepage", unliked_html)

# is the query frozen in time from line 133/134
            u1 = User.query.get(self.u1_id)
            msg2 = Message.query.get(self.m2_id)

            self.assertNotIn(msg2, u1.likes)














