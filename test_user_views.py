"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, connect_db, Message, User, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Set up test client and seed the database."""

        self.client = app.test_client()

        db.drop_all()
        db.create_all()

        self.user1 = User.signup(username="testuser1",
                                 email="test1@test.com",
                                 password="password",
                                 image_url=None)

        self.user2 = User.signup(username="testuser2",
                                 email="test2@test.com",
                                 password="password",
                                 image_url=None)

        db.session.commit()

        followee = Follows(user_being_followed_id=self.user2.id,
                           user_following_id=self.user1.id)
        db.session.add(followee)
        db.session.commit()

        message = Message(text="test message", user_id=self.user1.id)
        db.session.add(message)
        db.session.commit()

        like = Likes(user_id=self.user1.id, message_id=1)
        db.session.add(like)
        db.session.commit()

        self.user1_id = self.user1.id
        self.user2_id = self.user2.id

        self.message_id = message.id
        self.like_id = like.id

        self.message = message

        self.followee_id = followee.user_being_followed_id

        self.user1 = User.query.get(self.user1_id)
        self.user2 = User.query.get(self.user2_id)
        self.followee = User.query.get(self.followee_id)

        self.message = Message.query.get(self.message_id)
        self.like = Likes.query.get(self.like_id)

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_list_users(self):
        """Can we retrieve a list of all users?"""

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))

    def test_users_show(self):
        """Can we retrieve a page with a specific user's details?"""

        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}")

            self.assertIn("@testuser1", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))

    def test_users_show_following(self):
        """Can we retrieve a page with a specific user's details?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/users/{self.user1.id}/following")

            self.assertIn("@testuser2", str(resp.data))

    def test_users_show_followers(self):
        """Can we retrieve a page with a specific user's details?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/users/{self.user1.id}/followers")

            self.assertIn("@testuser1", str(resp.data))

    def test_users_show_likes(self):
        """Can we retrieve a page with a specific user's details?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            resp = c.get(f"/users/{self.user1.id}/likes")

            self.assertIn("@testuser1", str(resp.data))

    def test_users_show_likes_logged_out(self):
        """Can we retrieve a page with a specific user's details?"""

        with self.client as c:

            resp = c.get(f"/users/{self.user1.id}/likes",
                         follow_redirects=True)

            self.assertNotIn("@testuser1", str(resp.data))
    
    def test_add_like(self):
        m = Message(id=1984, text="The earth is round", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()
    
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
    
            resp = c.post("/messages/1984/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            AssertionError: 404 != 200
