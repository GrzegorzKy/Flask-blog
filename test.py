# -*- coding: utf-8 -*-
from flaskblog import create_app, db
from flask_testing import TestCase
import unittest
from flask import url_for
from bs4 import BeautifulSoup as bs


class Tests(TestCase):
    # helper functions
    def login(self, tester, creds: dict):
        # test GET /login
        response = tester.get('/login', content_type='html/text')
        if response.status_code != 200:
            return None
        
        # cut out csfr_token
        soup = bs(response.data, 'html.parser')
        csrf_token = soup.find(id='csrf_token')["value"]
        creds["csrf_token"] = csrf_token
        
        # post data with creds
        response = tester.post('/login', data=creds)
        return response
        
    def logout(self, tester):
        return tester.get("/logout", content_type="html/text")
    
    def register(self, tester, creds: dict):
        response = tester.get('/register', content_type='html/text')
        if response.status_code != 200:
            return None
        
        # cut out csfr_token
        soup = bs(response.data, 'html.parser')
        csrf_token = soup.find(id='csrf_token')["value"]
        creds["csrf_token"] = csrf_token
        
        # register user with creds
        response = tester.post('/register', data=creds)
        return response
    
    # required TestCase methods
    def create_app(self):     
        return create_app()
    
    def setUp(self):
        self.app = self.create_app()
        self.creds = {"email": "ab@abc.com", "password": "1"}
        self.new_user_creds = {"email": "abc@abc.com", "password": "1",
                               "username": "abc", "confirm_password": "1"}
    
    def tearDown(self):
        # todo: remove test user
        pass
    
    # test methods
    # test register
    def test_register(self):
        print("\nTest Login")
        tester = self.app.test_client(self)
        
        # unlogged
        # blank creds
        response = tester.post('/register', data={})
        self.assert200(response)
        # ...
        
        # valid creds
        response = tester.post('/register', data=self.new_user_creds)
        self.assertRedirects(response, url_for('users.login'))
        
    def test_login(self):
        print("\nTest Login")
        tester = self.app.test_client(self)
        
        # check get 200
        response = tester.get('/login', content_type='html/text')
        self.assert200(response)
        
        # login with wrong credentials
        # send empty form
        response = tester.post('/login', data={})
        self.assert200(response)
        # send wrong credentials
        response = self.login(tester, creds={"email": "email@email", "password": "15"})
        self.assert200(response)
        # correct user wrong password
        response = self.login(tester, creds={"email": self.creds["email"], "password": "15"})
        self.assert200(response)
        
        # log with user credentials
        response = self.login(tester, creds=self.creds)
        self.assertRedirects(response, url_for('main.home'))
        
        # logout
        self.logout(tester)
        
    def test_home(self):
        print("\nTest Home")
        tester = self.app.test_client(self)
        
        # unlogged user
        # /home
        response = tester.get('/home', content_type='html/text')
        self.assert200(response)
        
        # /
        response = tester.get('/', content_type='html/text')
        self.assert200(response)
        
        # logged user
        self.login(tester, creds=self.creds)
        
        # /home
        response = tester.get('/home', content_type='html/text')
        self.assert200(response)
        
        # /
        response = tester.get('/', content_type='html/text')
        self.assert200(response)
        
        # logout
        self.logout(tester)
    
    def test_about(self):
        print("\nTest About")
        tester = self.app.test_client(self)
        # unlogged user
        response = tester.get('/about', content_type='html/text')
        self.assert200(response)
        
        # logged user
        self.login(tester, creds=self.creds)
        response = tester.get('/about', content_type='html/text')
        self.assert200(response)
        
        


if __name__ == '__main__':
    unittest.main()


