"""User View tests"""


from codecs import utf_32_be_decode
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

class GeneralUserRoutesTestCase(UserBaseViewTestCase):
    def test_list_users(self):
        """Tests list users page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.get('/users')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test list users", html)

    def test_show_user(self):
        """Tests showing in session user's profile page and showing
        for user not in session"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            in_session_resp = c.get(f'/users/{self.u1_id}')
            in_session_html = in_session_resp.get_data(as_text = True)

            not_in_session_resp = c.get(f'/users/{self.u2_id}')
            not_in_session_html = not_in_session_resp.get_data(as_text = True)

            self.assertEqual(in_session_resp.status_code, 200)
            self.assertIn("Edit Profile", in_session_html)

            self.assertEqual(not_in_session_resp.status_code, 200)
            self.assertIn("Follow", not_in_session_html)

    def test_show_following(self):
        """Tests if user in session and not in session,
        show any user's following page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            in_session_resp = c.get(f'/users/{self.u1_id}/following')
            in_session_html = in_session_resp.get_data(as_text = True)

            not_in_session_resp = c.get(f'/users/{self.u2_id}/following')
            not_in_session_html = not_in_session_resp.get_data(as_text = True)

            self.assertEqual(in_session_resp.status_code, 200)
            self.assertIn("Test Following Page", in_session_html)

            self.assertEqual(not_in_session_resp.status_code, 200)
            self.assertIn("Test Following Page", not_in_session_html)

    def test_show_followers(self):
        """Tests if user in session and not in session,
        show any user's folowers page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            in_session_resp = c.get(f'/users/{self.u1_id}/followers')
            in_session_html = in_session_resp.get_data(as_text = True)

            not_in_session_resp = c.get(f'/users/{self.u2_id}/followers')
            not_in_session_html = not_in_session_resp.get_data(as_text = True)

            self.assertEqual(in_session_resp.status_code, 200)
            self.assertIn("Test Followers Page", in_session_html)

            self.assertEqual(not_in_session_resp.status_code, 200)
            self.assertIn("Test Followers Page", not_in_session_html)

    def test_handle_following(self):
        """Tests in session user start and stop following another user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            u1 = User.query.get(self.u1_id)
            u2 = User.query.get(self.u2_id)
            u2_username = u2.username

            resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Following Page", html)
            self.assertIn(f'{u2_username}', html)

            resp = c.post(f'/users/stop-following/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Following Page", html)
            self.assertNotIn(f'{u2_username}', html)

    # def test_stop_following(self):
    #     """Tests in session user stop following another user"""


    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.u1_id

    #         u1 = User.query.get(self.u1_id)
    #         u2 = User.query.get(self.u2_id)
    #         u3 = User.query.get(self.u3_id)
    #         u3_username = u3.username


    #         resp = c.post(f'/users/stop-following/{self.u3_id}', follow_redirects=True)
    #         html = resp.get_data(as_text = True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Test Following Page", html)
    #         self.assertNotIn(f'{u3_username}', html)

    def test_edit_user(self):
        """Tests edit in session user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            good_resp = c.post('/users/profile',
                            data={"username":"newusername",
                                  "email": "u1@email.com",
                                  "image_url": "/static/images/default-pic.png",
                                  "header_image_url": None,
                                  "bio": "new bio",
                                  "password": "password"},
                            follow_redirects=True)
            bad_resp = c.post('/users/profile',
                            data={"username":"newusername",
                                  "email": "u1@email.com",
                                  "image_url": "/static/images/default-pic.png",
                                  "header_image_url": None,
                                  "bio": "new bio",
                                  "password": "invalidpassword"},
                            follow_redirects=True)

            good_html = good_resp.get_data(as_text = True)
            bad_html = bad_resp.get_data(as_text = True)

            self.assertEqual(good_resp.status_code, 200)
            self.assertIn("test show user", good_html)

            self.assertEqual(bad_resp.status_code, 200)
            self.assertIn("test edit form", bad_html)
            self.assertIn("wrong password", bad_html)
