"""User View tests"""


import os
from unittest import TestCase

from models import db, User, Message, Like


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


from app import app, CURR_USER_KEY
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserBaseViewTestCase(TestCase):
    def setUp(self):
        """Set up: delete all users, create user and message"""
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.add(u1)

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.m1_id = m1.id

        self.client = app.test_client()
        print("u1id =", self.u1_id)


class UserLoginSignupTestCase(UserBaseViewTestCase):
    def test_login(self):
        """Test login route"""
        with self.client as c:
            # with c.session_transaction() as sess:
            #     sess[CURR_USER_KEY] = self.u1_id
            u1 = User.query.get(self.u1_id)

            resp = c.post("/login",
                data={"username" : u1.username, "password" : "password"},
                follow_redirects = True)

            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test login", html)

            # session_transactions