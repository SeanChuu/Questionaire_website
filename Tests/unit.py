import os
import unittest
from app import app, db
from app.models import User, Quiz, QuizContent, QuizStyle, Question, QuestionContent, QuestionChoice, UserAnswer
from app.forms import LoginForm, RegistrationForm, StyleOneForm, StyleTwoForm
from config import basedir

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    #Helper Functions

    def register(self, username, email, password, password2):
        return self.app.post("/register", data=dict(username=username, 
        email=email,
        password=password,
        password2=password2),
        follow_redirects = True)
    
    def  login(self, username, password):
        return self.app.post("/login", data=dict(username=username,
        password=password), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects = True)



#Registration Functionality Tests
    #tests a valid registration attempt
    def test_valid_registration(self):
        response = self.register("user", "user@email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Log In</title>', response.data)

    #Tests an invalid registration attempt where passwords do not match
    def test_invalid_registration_passwords(self):
        response = self.register("user", "grae@email.com", "password", "invalid password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)

    #Tests an invalid registration attempt where email is invalid
    def test_invalid_registration_email(self):
        #missing @ symbol
        response = self.register("user", "invalid email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)

        #missing domain
        response = self.register("user", "invalid@email", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)

        #invalid space inserted
        response = self.register("user", "invalid@ email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)

    #Tests an invalid registration where the username and/or email are already taken
    def test_invalid_registration_duplicates(self):
        u1 = User(username = "existing_user", email = "existing_user@email.com", password_hash = "User.set_password('password')")
        db.session.add(u1)
        db.session.commit()

        #duplicate username
        response = self.register("existing_user", "user@email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User name has been used', response.data)

        #duplicate email
        response = self.register("user", "existing_user@email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email has been used', response.data)
    
    #Tests an invalid registration where one of the fields has been left blank
    def test_invalid_registration_missing(self):
        response = self.register("", "user@email.com", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data) #redirected to register page
        self.assertIn(b'value=""', response.data) #at least 1 field has been left empty

        response = self.register("user", "", "password", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

        response = self.register("user", "user@email.com", "", "password")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

        response = self.register("user", "user@email.com", "password", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Register</title>', response.data)
        self.assertIn(b'value=""', response.data)

#LOGIN FUNCTIONALITY TESTS
    #Tests a valid login 
    def test_successful_login(self):
        user = User(username="bob", email="bob@email.com")
        user.set_password('password')
        self.assertTrue(user.check_password('password'))
        db.session.add(user)
        db.session.commit()

        response = self.login("bob", "password")
        self.assertIn(b'Hello bob!', response.data)
        self.assertIn(b'<title>Questionaire - How do you Compare?</title>', response.data)
    
    #Tests invalid login attempts
    def test_unsuccussful_login(self):
        user = User(username="bob", email="bob@email.com")
        user.set_password('password')
        self.assertTrue(user.check_password('password'))
        db.session.add(user)
        db.session.commit()

        #invalid username or password
        response = self.login("bob", "invalid")
        self.assertIn(b'<title>Log In</title>', response.data)

        response = self.login("invalid", "password")
        self.assertIn(b'<title>Log In</title>', response.data)
        
        #username or password missing
        response = self.login("", "password")
        self.assertIn(b'<title>Log In</title>', response.data)

        response = self.login("bob", "")
        self.assertIn(b'<title>Log In</title>', response.data)

#LOGOUT FUNCTIONALITY TESTS:
    #test logout
    def test_logout(self):
        self.app.get('/register', follow_redirects = True)
        self.register("user", "user@email.com", "password", "password")
        self.app.get('/login', follow_redirects = True)
        self.login("user", "password")
        response = self.app.get('/logout', follow_redirects = True)
        self.assertIn(b'Please Login to save your scores', response.data)

#ADMIN TESTS:
    #successful login as admin
    def test_admin_login(self):
        user = User(username="john", email="john@email.com")
        user.set_password('password')
        user.admin = True
        db.session.add(user)
        db.session.commit()

        response = self.login("john", "password")
        self.assertIn(b'Hello Admin john!', response.data)

    #unsuccessful login as admin
    def test_nonadmin_login(self):
        user = User(username="john", email="john@email.com")
        user.set_password('password')
        user.admin = False
        db.session.add(user)
        db.session.commit()

        response = self.login("john", "password")
        self.assertNotIn(b'Hello Admin john!', response.data)

    #accessing the flag quiz if not logged in
    def test_flagquiz_not_logged_in(self):
        self.app.get('/register', follow_redirects = True)
        self.register("user", "user@email.com", "password", "password")
        self.app.get('/login', follow_redirects = True)
        self.login("user", "password")
        self.app.get('/logout', follow_redirects = True)
        response = self.app.get('/quiz/flag', follow_redirects = True)
        self.assertIn(b'<title>Log In</title>', response.data)

    #accessing the language quiz if not logged in
    def test_languagequiz_not_logged_in(self):
        self.app.get('/register', follow_redirects = True)
        self.register("user", "user@email.com", "password", "password")
        self.app.get('/login', follow_redirects = True)
        self.login("user", "password")
        self.app.get('/logout', follow_redirects = True)
        response = self.app.get('/quiz/language', follow_redirects = True)
        self.assertIn(b'<title>Log In</title>', response.data)

    #access the results page test
    def test_access_results_page_logged_in(self):
        self.app.get('/register', follow_redirects = True)
        self.register("user", "user@email.com", "password", "password")
        self.app.get('/login', follow_redirects = True)
        self.login("user", "password")
        response = self.app.get('/results', follow_redirects = True)
        self.assertIn(b'<title>results</title>', response.data)
    
    #access the results page, not logged in
    def test_access_results_page_not_logged(self):
        self.app.get('/register', follow_redirects = True)
        self.register("user", "user@email.com", "password", "password")
        self.app.get('/login', follow_redirects = True)
        self.login("user", "password")
        self.app.get('/logout', follow_redirects = True)
        response = self.app.get('/results', follow_redirects = True)
        self.assertIn(b'<title>Log In</title>', response.data)

    #tests the flag quiz submit button after each question
   # def test_flag_quiz_submit(self):
    #    self.app.get('/login', follow_redirects = True)
     #   self.login("user", "password")
      #  self.app.get('/quiz/language', follow_redirects = True)



if __name__ == '__main__':
    unittest.main()
