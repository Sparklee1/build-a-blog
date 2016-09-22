#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler (webapp2.RequestHandler):
    def write (self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

class Body (db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
        #t = jinja_env.get_template("NewPost.html")
    def render_NewPost(self, title="", body="", error=""):
        bodys = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title=title, body=body, error=error, bodys=bodys)
    def get(self):
        self.render_NewPost()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")
        if title and body:
            a=Body(title=title, body=body)
            a.put()
            id = a.key().id()
            self.redirect("/newpost")
        else:
            error="We need both a title and body!"
            self.render_NewPost(title, body, error)

class NewPostHandler(Handler):
    def render_NewPost(self, title="", body="", error=""):
        bodys = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, body=body, error=error, bodys=bodys)
    def get(self):
        self.render_NewPost()
    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            post=Body(title=title, body=body , error=error)
            post.put()
            id = post.key().id()
            self.redirect("/newpost/%s" %d)
        else:
            error="We need both a title and body!"
            self.render_NewPost(title, body, error)

class ViewPostHandler(Handler):
    def get (self, id):
        post = Body.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("post.html")
            response = t.render(post=post)
        else:
            error = "There is not a post with id %s" % id
            t = jinja_env.get_template("404.html")
            response = t.render(error=error)

        self.response.out.write(response)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPostHandler),
    webapp2.Route('/newpost/<id:\d+>', ViewPostHandler)
], debug=True)
