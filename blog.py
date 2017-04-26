
# -*- coding: utf-8 -*-

import os
import jinja2
import webapp2
import re
import hmac
import hashlib
import random
import time

from string import letters

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
    autoescape = True)


# The function below is a global function for rendering a string which does
# not inherit from the class Handler

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# functions for hashing and validating password hashing
# oprettelseskoden er VELKOMMEN. Hvis den fornyes skal det ske på linie 1921

secret = 'aaarfh-this_is-sooooo_secreteeeeeer-than_anything-ion'

def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class Handler(webapp2.RequestHandler):
    """class that handles rendering and writing and can be used
       in other classes that inherit from it"""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


class Entrance(Handler):
    """class that renders a start page, just for the sake of it"""
    def get(self):
        self.render("entrance.html")


# The functions below are for hashing and salting

def make_salt():
    return ''.join(random.choice(letters) for x in range(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    hashstring = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, hashstring)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

#Below are all the Database classes for the datastore

class User(db.Model):
    """class that creates the basic database specifics for a user"""
    name = db.StringProperty(required = True)
    firstname = db.StringProperty(required = True)
    surname = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()
    phone = db.PhoneNumberProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, firstname, surname, pw, email=None, phone=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    firstname = firstname,
                    surname = surname,
                    pw_hash = pw_hash,
                    email = email,
                    phone = phone)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class Lamp(db.Model):
    """class that creates the basic database structure for Lamp"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    lamptype = db.StringProperty(required=True)
    lampmodeltype = db.StringProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    watt = db.IntegerProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Cable(db.Model):
    """class that creates the basic database structure for Cable"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    connection = db.StringProperty(required=True)
    length = db.IntegerProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Damper(db.Model):
    """class that creates the basic database structure for Damper"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class LightMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class SoundMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    channels = db.IntegerProperty()
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Speaker(db.Model):
    """class that creates the basic database structure for Speaker"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    active = db.TextProperty(required=True)
    inputs = db.TextProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class PhotoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    digianal = db.StringProperty(required=True)
    vidnonvid = db.StringProperty(required=True)
    slr = db.StringProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class VideoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    resolution = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Projector(db.Model):
    """class that creates the basic database structure for Projector"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    resolution = db.StringProperty(required=True)
    lumen =db.IntegerProperty(required=True)
    model = db.TextProperty(required=True)
    input1 = db.StringProperty()
    input2 = db.StringProperty()
    input3 = db.StringProperty()
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class TV(db.Model):
    """class that creates the basic database structure for TV"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    resolution = db.StringProperty(required=True)
    screensize = db.IntegerProperty(required=True)
    model = db.TextProperty(required=True)
    input1 = db.StringProperty()
    input2 = db.StringProperty()
    input3 = db.StringProperty()
    description = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Scenography(db.Model):
    """class that creates the basic database structure for Scenography"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    linktext = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()

class Costumes(db.Model):
    """class that creates the basic database structure for Costume"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    linktext = db.TextProperty()
    borrower = db.StringProperty()
    booked = db.BooleanProperty()


def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)




#Class below links to creating new instances of lamp, speaker etc.
class NewThing(Handler):
    """class that renders a page for creating a new instance of a lamp, cable, speaker or other."""
    def get(self):
        if self.user:
            self.render("newthing.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

#Class below handles new instances of LAMP.
class NewLamp(Handler):
    """class that renders a page for creating a new Lamp instance"""
    def get(self):
        if self.user:
            self.render("newlamp.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        lamptype = self.request.get("lamptype")
        lampmodeltype = self.request.get("lampmodeltype")
        model = self.request.get("model")
        watt = int(self.request.get("watt"))
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model and watt:
            l = Lamp(parent = blog_key(), owner = owner, contact = contact, brand = brand, lamptype = lamptype,
                lampmodeltype = lampmodeltype, model = model, watt = watt, description = description)
            l.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newlamp.html", brand = brand, model = model,
                watt = watt, description = description, error = error)

#Class for editing a Lamp instance
class EditLamp(Handler):
    """class that opens a lamp for editing"""
    def get(self, lamp_id):
        key = db.Key.from_path('Lamp', int(lamp_id), parent = blog_key())
        ml = db.get(key)

        if not ml:
            self.error(404)
            return self.render("404.html")

        if self.user.name == ml.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editlamp.html", ml=ml, users = users, owner = ml.owner, contact = ml.contact, brand = ml.brand, lamptype = ml.lamptype,
                lampmodeltype = ml.lampmodeltype, model = ml.model, watt = ml.watt, borrower = ml.borrower, description = ml.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, lamp_id):
        key = db.Key.from_path('Lamp', int(lamp_id), parent = blog_key())
        ml = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        lamptype = self.request.get("lamptype")
        lampmodeltype = self.request.get("lampmodeltype")
        model = self.request.get("model")
        watt = int(self.request.get("watt"))
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == ml.owner:
            if brand and model and watt:
                ml.owner = owner
                ml.contact = contact
                ml.brand = brand
                ml.lamptype = lamptype
                ml.lampmodeltype = lampmodeltype
                ml.model = model
                ml.watt = watt
                ml.description = description
                ml.borrower = borrower
                ml.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editlamp.html", ml = ml, brand = brand, model = model,
                        lamptype = lamptype, watt = watt, lampmodeltype = lampmodeltype,
                        description = description, borrower = borrower, users = users,
                        error = error)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Lamp instance
class DeleteLamp(Handler):
    """class for deleting a Lamp"""
    def get(self, lamp_id):
        key = db.Key.from_path('Lamp', int(lamp_id), parent = blog_key())
        ml = db.get(key)

        if self.user.name == ml.owner:
            ml.delete()
            message = "Din lampe er uigenkaldeligt slettet!"
            self.render("mythings.html", ml=ml, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)


#Class below handles new instances of CABLE.
class NewCable(Handler):
    """class that renders a page for creating a new Cable instance"""
    def get(self):
        if self.user:
            self.render("newcable.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        connection = self.request.get("connection")
        length = int(self.request.get("length"))
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if connection and length:
            c = Cable(parent = blog_key(), owner = owner, contact = contact, connection = connection,
                length = length, description = description)
            c.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newcable.html", connection = connection,
                length = length, description = description, error = error)

#Class for editing a Cable instance
class EditCable(Handler):
    """class that opens a Cable for editing"""
    def get(self, cable_id):
        key = db.Key.from_path('Cable', int(cable_id), parent = blog_key())
        mc = db.get(key)

        if not mc:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mc.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editcable.html", mc=mc, users = users, owner = mc.owner, contact = mc.contact,
                connection = mc.connection, length = mc.length, borrower = mc.borrower, description = mc.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, cable_id):
        key = db.Key.from_path('Cable', int(cable_id), parent = blog_key())
        mc = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        connection = self.request.get("connection")
        length = int(self.request.get("length"))
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mc.owner:
            if connection and length:
                mc.owner = owner
                mc.contact = contact
                mc.connection = connection
                mc.length = length
                mc.description = description
                mc.borrower = borrower
                mc.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editcable.html", mc = mc, connection = connection, length = length,
                        description = description, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Cable instance
class DeleteCable(Handler):
    """class for deleting a Cable"""
    def get(self, cable_id):
        key = db.Key.from_path('Cable', int(cable_id), parent = blog_key())
        mc = db.get(key)

        if self.user.name == mc.owner:
            mc.delete()
            message = "Dit kabel er uigenkaldeligt slettet!"
            self.render("mythings.html", mc=mc, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of DAMPER.
class NewDamper(Handler):
    """class that renders a page for creating a new Damper instance"""
    def get(self):
        if self.user:
            self.render("newdamper.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            d = Damper(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                description = description)
            d.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newdamper.html", brand = brand, model = model,
                description = description, error = error)

#Class for editing a Damper instance
class EditDamper(Handler):
    """class that opens a Damper for editing"""
    def get(self, damper_id):
        key = db.Key.from_path('Damper', int(damper_id), parent = blog_key())
        md = db.get(key)

        if not md:
            self.error(404)
            return self.render("404.html")

        if self.user.name == md.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editdamper.html", md=md, users = users, owner = md.owner, contact = md.contact,
                brand = md.brand, model = md.model, borrower = md.borrower, description = md.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, damper_id):
        key = db.Key.from_path('Damper', int(damper_id), parent = blog_key())
        md = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == md.owner:
            if brand and model:
                md.owner = owner
                md.contact = contact
                md.brand = brand
                md.model = model
                md.description = description
                md.borrower = borrower
                md.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editdamper.html", md = md, brand = brand, model = model,
                        description = description, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Damper instance
class DeleteDamper(Handler):
    """class for deleting a Damper"""
    def get(self, damper_id):
        key = db.Key.from_path('Damper', int(damper_id), parent = blog_key())
        md = db.get(key)

        if self.user.name == md.owner:
            md.delete()
            message = "Din daemper er uigenkaldeligt slettet!"
            self.render("mythings.html", md=md, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of LIGHTMIXER.
class NewLightMixer(Handler):
    """class that renders a page for creating a new LightMixer instance"""
    def get(self):
        if self.user:
            self.render("newlightmixer.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            lm = LightMixer(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                description = description)
            lm.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newlightmixer.html", brand = brand, model = model,
                description = description, error = error)

#Class for editing a LightMixer instance
class EditLightMixer(Handler):
    """class that opens a LightMixer for editing"""
    def get(self, lightmixer_id):
        key = db.Key.from_path('LightMixer', int(lightmixer_id), parent = blog_key())
        mlm = db.get(key)

        if not mlm:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mlm.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editlightmixer.html", mlm=mlm, users = users, owner = mlm.owner, contact = mlm.contact,
                brand = mlm.brand, model = mlm.model, borrower = mlm.borrower, description = mlm.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, lightmixer_id):
        key = db.Key.from_path('LightMixer', int(lightmixer_id), parent = blog_key())
        mlm = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mlm.owner:
            if brand and model:
                mlm.owner = owner
                mlm.contact = contact
                mlm.brand = brand
                mlm.model = model
                mlm.description = description
                mlm.borrower = borrower
                mlm.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editlightmixer.html", mlm = mlm, brand = brand, model = model,
                        description = description, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a LightMixer instance
class DeleteLightMixer(Handler):
    """class for deleting a LightMixer"""
    def get(self, lightmixer_id):
        key = db.Key.from_path('LightMixer', int(lightmixer_id), parent = blog_key())
        mlm = db.get(key)

        if self.user.name == mlm.owner:
            mlm.delete()
            message = "Din lysmixer er uigenkaldeligt slettet!"
            self.render("mythings.html", mlm=mlm, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of SOUNDMIXER.
class NewSoundMixer(Handler):
    """class that renders a page for creating a new SoundMixer instance"""
    def get(self):
        if self.user:
            self.render("newsoundmixer.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        channels = int(self.request.get("channels"))
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            sm = SoundMixer(parent = blog_key(), owner = owner, contact = contact, brand = brand,
                 model = model, channels = channels, description = description)
            sm.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newsoundmixer.html", brand = brand, model = model,
                description = description, error = error)

#Class for editing a SoundMixer instance
class EditSoundMixer(Handler):
    """class that opens a SoundMixer for editing"""
    def get(self, soundmixer_id):
        key = db.Key.from_path('SoundMixer', int(soundmixer_id), parent = blog_key())
        msm = db.get(key)

        if not msm:
            self.error(404)
            return self.render("404.html")

        if self.user.name == msm.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editsoundmixer.html", msm=msm, users = users, owner = msm.owner, contact = msm.contact,
                brand = msm.brand, model = msm.model, channels = msm.channels, borrower = msm.borrower, description = msm.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, soundmixer_id):
        key = db.Key.from_path('SoundMixer', int(soundmixer_id), parent = blog_key())
        msm = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        channels = int(self.request.get("channels"))
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == msm.owner:
            if brand and model:
                msm.owner = owner
                msm.contact = contact
                msm.brand = brand
                msm.model = model
                msm.description = description
                msm.borrower = borrower
                msm.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editsoundmixer.html", msm = msm, brand = brand, model = model,
                        description = description, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a SoundMixer instance
class DeleteSoundMixer(Handler):
    """class for deleting a SoundMixer"""
    def get(self, soundmixer_id):
        key = db.Key.from_path('SoundMixer', int(soundmixer_id), parent = blog_key())
        msm = db.get(key)

        if self.user.name == msm.owner:
            msm.delete()
            message = "Din lydmixer er uigenkaldeligt slettet!"
            self.render("mythings.html", msm=msm, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of SPEAKER.
class NewSpeaker(Handler):
    """class that renders a page for creating a new Speaker instance"""
    def get(self):
        if self.user:
            self.render("newspeaker.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        inputs = self.request.get("inputs")
        active = self.request.get("active")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            sp = Speaker(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                inputs = inputs, active = active, description = description)
            sp.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newspeaker.html", brand = brand, model = model,
                inputs = inputs, active = active, description = description, error = error)

#Class for editing a Speaker instance
class EditSpeaker(Handler):
    """class that opens a Speaker for editing"""
    def get(self, speaker_id):
        key = db.Key.from_path('Speaker', int(speaker_id), parent = blog_key())
        msp = db.get(key)

        if not msp:
            self.error(404)
            return self.render("404.html")

        if self.user.name == msp.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editspeaker.html", msp=msp, users = users, owner = msp.owner, contact = msp.contact,
                brand = msp.brand, inputs = msp.inputs, active = msp.active, borrower = msp.borrower,
                model = msp.model, description = msp.description)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, speaker_id):
        key = db.Key.from_path('Speaker', int(speaker_id), parent = blog_key())
        msp = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        model = self.request.get("model")
        inputs = self.request.get("inputs")
        active = self.request.get("active")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == msp.owner:
            if brand and model:
                msp.owner = owner
                msp.contact = contact
                msp.brand = brand
                msp.model = model
                msp.active = active
                msp.inputs = inputs
                msp.description = description
                msp.borrower = borrower
                msp.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editspeaker.html", msp = msp, brand = brand, model = model, active = active,
                        inputs = inputs, description = description, borrower = borrower, error = error, users =users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Speaker instance
class DeleteSpeaker(Handler):
    """class for deleting a Speaker"""
    def get(self, speaker_id):
        key = db.Key.from_path('Speaker', int(speaker_id), parent = blog_key())
        msp = db.get(key)

        if self.user.name == msp.owner:
            msp.delete()
            message = "Din lydmixer er uigenkaldeligt slettet!"
            self.render("mythings.html", msp=msp, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of PhotoCamera.
class NewPhotoCamera(Handler):
    """class that renders a page for creating a new PhotoCamera instance"""
    def get(self):
        if self.user:
            self.render("newphotocamera.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        digianal = self.request.get("digianal")
        vidnonvid = self.request.get("vidnonvid")
        slr = self.request.get("slr")
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            pc = PhotoCamera(parent = blog_key(), owner = owner, contact = contact, brand = brand,
                model = model, digianal = digianal, slr = slr, vidnonvid = vidnonvid, description = description)
            pc.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newphotocamera.html", brand = brand, model = model, slr = slr,
                digianal = digianal, vidnonvid = vidnonvid, description = description, error = error)

#Class for editing a PhotoCamera instance
class EditPhotoCamera(Handler):
    """class that opens a PhotoCamera for editing"""
    def get(self, photocamera_id):
        key = db.Key.from_path('PhotoCamera', int(photocamera_id), parent = blog_key())
        mpc = db.get(key)

        if not mpc:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mpc.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editphotocamera.html", mpc=mpc, users = users, owner = mpc.owner, contact = mpc.contact,
                brand = mpc.brand, digianal = mpc.digianal, vidnonvid = mpc.vidnonvid, borrower = mpc.borrower,
                slr = mpc.slr, model = mpc.model, description = mpc.description,)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, photocamera_id):
        key = db.Key.from_path('PhotoCamera', int(photocamera_id), parent = blog_key())
        mpc = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        digianal = self.request.get("digianal")
        vidnonvid = self.request.get("vidnonvid")
        slr = self.request.get("slr")
        model = self.request.get("model")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mpc.owner:
            if brand and model:
                mpc.owner = owner
                mpc.contact = contact
                mpc.brand = brand
                mpc.model = model
                mpc.digianal = digianal
                mpc.slr = slr
                mpc.vidnonvid = vidnonvid
                mpc.description = description
                mpc.borrower = borrower
                mpc.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editphotocamera.html", mpc = mpc, brand = brand, model = model, digianal = digianal,
                        slr = slr, vidnonvid = vidnonvid, description = description, borrower = borrower, error = error,
                        users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a PhotoCamera instance
class DeletePhotoCamera(Handler):
    """class for deleting a PhotoCamera"""
    def get(self, photocamera_id):
        key = db.Key.from_path('PhotoCamera', int(photocamera_id), parent = blog_key())
        mpc = db.get(key)

        if self.user.name == mpc.owner:
            mpc.delete()
            message = "Dit fotokamera er uigenkaldeligt slettet!"
            self.render("mythings.html", mpc=mpc, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of VIDEOCAMERA.
class NewVideoCamera(Handler):
    """class that renders a page for creating a new VideoCamera instance"""
    def get(self):
        if self.user:
            self.render("newvideocamera.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            vc = VideoCamera(parent = blog_key(), owner = owner, contact = contact, brand = brand,
                 model = model, resolution = resolution, description = description)
            vc.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newvideocamera.html", brand = brand, model = model,
                description = description, resolution = resolution, error = error)

#Class for editing a VideoCamera instance
class EditVideoCamera(Handler):
    """class that opens a VideoCamera for editing"""
    def get(self, videocamera_id):
        key = db.Key.from_path('VideoCamera', int(videocamera_id), parent = blog_key())
        mvc = db.get(key)

        if not mvc:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mvc.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editvideocamera.html", mvc=mvc, users = users, owner = mvc.owner, contact = mvc.contact,
                brand = mvc.brand, resolution = mvc.resolution, borrower = mvc.borrower, model = mvc.model,
                description = mvc.description,)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, videocamera_id):
        key = db.Key.from_path('VideoCamera', int(videocamera_id), parent = blog_key())
        mvc = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        model = self.request.get("model")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mvc.owner:
            if brand and model:
                mvc.owner = owner
                mvc.contact = contact
                mvc.brand = brand
                mvc.resolution = resolution
                mvc.model = model
                mvc.description = description
                mvc.borrower = borrower
                mvc.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editvideocamera.html", mvc = mvc, brand = brand, model = model, resolution = resolution,
                        description = description, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a VideoCamera instance
class DeleteVideoCamera(Handler):
    """class for deleting a VideoCamera"""
    def get(self, videocamera_id):
        key = db.Key.from_path('VideoCamera', int(videocamera_id), parent = blog_key())
        mvc = db.get(key)

        if self.user.name == mvc.owner:
            mvc.delete()
            message = "Dit videokamera er uigenkaldeligt slettet!"
            self.render("mythings.html", mvc=mvc, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of Projector.
class NewProjector(Handler):
    """class that renders a page for creating a new Projector instance"""
    def get(self):
        if self.user:
            self.render("newprojector.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        lumen = int(self.request.get("lumen"))
        model = self.request.get("model")
        input1 = self.request.get("input1")
        input2 = self.request.get("input2")
        input3 = self.request.get("input3")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model and owner and contact and resolution and lumen:
            pc = Projector(parent = blog_key(), owner = owner, contact = contact, brand = brand,
                    model = model, input1 = input1, input2 = input2, input3 = input3,
                    resolution = resolution, lumen = lumen, description = description)
            pc.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newprojector.html", brand = brand, model = model,
                description = description, resolution = resolution, error = error)

#Class for editing a Projector instance
class EditProjector(Handler):
    """class that opens a Projector for editing"""
    def get(self, projector_id):
        key = db.Key.from_path('Projector', int(projector_id), parent = blog_key())
        mp = db.get(key)

        if not mp:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mp.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editprojector.html", mp=mp, users = users, owner = mp.owner, contact = mp.contact,
                brand = mp.brand, resolution = mp.digianal, lumen = mp.lumen, borrower = mp.borrower,
                model = mp.model, input1 = mp.input1, input2 = mp.input2, input3 = mp.input3,
                description = mp.description,)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, projector_id):
        key = db.Key.from_path('Projector', int(projector_id), parent = blog_key())
        mp = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        lumen = int(self.request.get("lumen"))
        model = self.request.get("model")
        input1 = self.request.get("input1")
        input2 = self.request.get("input2")
        input3 = self.request.get("input3")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mp.owner:
            if brand and model and owner and contact and resolution and lumen:
                mp.owner = owner
                mp.contact = contact
                mp.brand = brand
                mp.resolution = resolution
                mp.lumen = lumen
                mp.model = model
                mp.input1 = input1
                mp.input2 = input2
                mp.input3 = input3
                mp.description = description
                mp.borrower = borrower
                mp.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editprojector.html", mp = mp, brand = brand, model = model, resolution = resolution,
                        lumen = lumen, description = description, borrower = borrower, error = error,
                        users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Projector instance
class DeleteProjector(Handler):
    """class for deleting a Projector"""
    def get(self, projector_id):
        key = db.Key.from_path('Projector', int(projector_id), parent = blog_key())
        mp = db.get(key)

        if self.user.name == mp.owner:
            mp.delete()
            message = "Din projektor er uigenkaldeligt slettet!"
            self.render("mythings.html", mp=mp, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of TV.
class NewTV(Handler):
    """class that renders a page for creating a new TV instance"""
    def get(self):
        if self.user:
            self.render("newtv.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        screensize = int(self.request.get("screensize"))
        model = self.request.get("model")
        input1 = self.request.get("input1")
        input2 = self.request.get("input2")
        input3 = self.request.get("input3")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model and owner and contact and resolution and screensize:
            tv = TV(parent = blog_key(), owner = owner, contact = contact, brand = brand,
                    model = model, input1 = input1, input2 = input2, input3 = input3,
                    resolution = resolution, screensize = screensize, description = description)
            tv.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newtv.html", brand = brand, model = model,
                description = description, resolution = resolution, screensize = screensize, error = error)

#Class for editing a TV instance
class EditTV(Handler):
    """class that opens a TV for editing"""
    def get(self, tv_id):
        key = db.Key.from_path('TV', int(tv_id), parent = blog_key())
        mtv = db.get(key)

        if not mtv:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mtv.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("edittv.html", mtv=mtv, users = users, owner = mtv.owner, contact = mtv.contact,
                brand = mtv.brand, resolution = mtv.resolution, screensize = mtv.screensize, borrower = mtv.borrower,
                model = mtv.model, input1 = mtv.input1, input2 = mtv.input2, input3 = mtv.input3,
                description = mtv.description,)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, tv_id):
        key = db.Key.from_path('TV', int(tv_id), parent = blog_key())
        mtv = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        brand = self.request.get("brand")
        resolution = self.request.get("resolution")
        screensize = int(self.request.get("screensize"))
        model = self.request.get("model")
        input1 = self.request.get("input1")
        input2 = self.request.get("input2")
        input3 = self.request.get("input3")
        description = self.request.get("description")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mtv.owner:
            if brand and model and owner and contact and resolution and screensize:
                mtv.owner = owner
                mtv.contact = contact
                mtv.brand = brand
                mtv.resolution = resolution
                mtv.screensize = screensize
                mtv.model = model
                mtv.input1 = input1
                mtv.input2 = input2
                mtv.input3 = input3
                mtv.description = description
                mtv.borrower = borrower
                mtv.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("edittv.html", mtv = mtv, brand = brand, model = model, resolution = resolution,
                        screensize = screensize, description = description, borrower = borrower, error = error,
                        users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a TV instance
class DeleteTV(Handler):
    """class for deleting a TV"""
    def get(self, tv_id):
        key = db.Key.from_path('TV', int(tv_id), parent = blog_key())
        mtv = db.get(key)

        if self.user.name == mtv.owner:
            mtv.delete()
            message = "Dit TV er uigenkaldeligt slettet!"
            self.render("mythings.html", mtv=mtv, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of SCENOGRAPHY.
class NewScenography(Handler):
    """class that renders a page for creating a new Scenography instance"""
    def get(self):
        if self.user:
            self.render("newscenography.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        model = self.request.get("model")
        description = self.request.get("description")
        linktext = self.request.get("linktext")

        if not description:
            description = "Ingen beskrivelse er givet."

        if model and description:
            scy = Scenography(parent = blog_key(), owner = owner, contact = contact, model = model,
                description = description, linktext = linktext)
            scy.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newscenography.html", model = model,
                description = description, error = error)

#Class for editing a Scenography instance
class EditScenography(Handler):
    """class that opens a Scenography for editing"""
    def get(self, scenography_id):
        key = db.Key.from_path('Scenography', int(scenography_id), parent = blog_key())
        msc = db.get(key)

        if not msc:
            self.error(404)
            return self.render("404.html")

        if self.user.name == msc.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editscenography.html", msc=msc, users = users, owner = msc.owner, contact = msc.contact,
                borrower = msc.borrower, model = msc.model, description = msc.description, linktext = msc.linktext)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, scenography_id):
        key = db.Key.from_path('Scenography', int(scenography_id), parent = blog_key())
        msc = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        model = self.request.get("model")
        description = self.request.get("description")
        linktext = self.request.get("linktext")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == msc.owner:
            if model and description:
                msc.owner = owner
                msc.contact = contact
                msc.model = model
                msc.description = description
                msc.linktext = linktext
                msc.borrower = borrower
                msc.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editscenography.html", msc = msc, model = model, description = description,
                                    linktext = linktext, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Scenography instance
class DeleteScenography(Handler):
    """class for deleting a Scenography"""
    def get(self, scenography_id):
        key = db.Key.from_path('Scenography', int(scenography_id), parent = blog_key())
        msc = db.get(key)

        if self.user.name == msc.owner:
            msc.delete()
            message = "Din scenografi er uigenkaldeligt slettet!"
            self.render("mythings.html", msc=msc, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)



#Class below handles new instances of COSTUMES.
class NewCostume(Handler):
    """class that renders a page for creating a new Costumes instance"""
    def get(self):
        if self.user:
            self.render("newcostume.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)

    def post(self):
        if not self.user:
            return self.redirect("/mypage/login")

        owner = self.user.name
        contact = self.user.phone
        model = self.request.get("model")
        description = self.request.get("description")
        linktext = self.request.get("linktext")

        if not description:
            description = "Ingen beskrivelse er givet."

        if model and description:
            cos = Costumes(parent = blog_key(), owner = owner, contact = contact, model = model,
                description = description, linktext = linktext)
            cos.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newcostume.html", model = model,
                description = description, error = error)

#Class for editing a Costume instance
class EditCostume(Handler):
    """class that opens a Costume for editing"""
    def get(self, costume_id):
        key = db.Key.from_path('Costumes', int(costume_id), parent = blog_key())
        mcs = db.get(key)

        if not mcs:
            self.error(404)
            return self.render("404.html")

        if self.user.name == mcs.owner:
            u = self.user.name
            users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
            self.render("editcostume.html", mcs=mcs, users = users, owner = mcs.owner, contact = mcs.contact,
                borrower = mcs.borrower, model = mcs.model, description = mcs.description, linktext = mcs.linktext)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

    def post(self, costume_id):
        key = db.Key.from_path('Costumes', int(costume_id), parent = blog_key())
        mcs = db.get(key)

        owner = self.user.name
        contact = self.user.phone
        model = self.request.get("model")
        description = self.request.get("description")
        linktext = self.request.get("linktext")
        borrower = self.request.get("borrower")

        if self.user and self.user.name == mcs.owner:
            if model and description:
                mcs.owner = owner
                mcs.contact = contact
                mcs.model = model
                mcs.description = description
                mcs.linktext = linktext
                mcs.borrower = borrower
                mcs.put()
                time.sleep(0.1)
                self.redirect("/mypage/mythings")
            else:
                error = "Du skal udfylde alle obligatorisk felter!"
                u = self.user.name
                users = db.GqlQuery("""SELECT * FROM User where name != :u""", u = u)
                return self.render("editcostume.html", mcs = mcs, model = model, description = description,
                                    linktext = linktext, borrower = borrower, error = error, users = users)
        else:
            error = "Du skal logge ind for at redigere en genstand!"
            return self.render('login.html', error=error)

#Class for deleting a Costume instance
class DeleteCostume(Handler):
    """class for deleting a Costume"""
    def get(self, costume_id):
        key = db.Key.from_path('Costumes', int(costume_id), parent = blog_key())
        mcs = db.get(key)

        if self.user.name == mcs.owner:
            mcs.delete()
            message = "Dit kostume er uigenkaldeligt slettet!"
            self.render("mythings.html", mcs=mcs, message=message)
        else:
            error = "Du kan kun slette dine egne ting!"
            return self.render("login.html", error=error)




#Class below links to creating new instances of lamp, speaker etc.
class SearchType(Handler):
    """class that renders a page for creating a new instance of a lamp, cable, speaker or other."""
    def get(self):
        if self.user:
            self.render("searchtype.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)


#class that handles personal page with all things ie lamps, cables etc
class MyThings(Handler):
    """class that handles users things, showing them all on one page"""
    def render_things(self):
        u = self.user.name
        my_lamps = db.GqlQuery("""SELECT * FROM Lamp WHERE owner = :u ORDER BY watt ASC""", u=u)
        my_cables = db.GqlQuery("""SELECT * FROM Cable WHERE owner = :u""", u=u)
        my_dampers = db.GqlQuery("""SELECT * FROM Damper WHERE owner = :u""", u=u)
        my_lightmixers = db.GqlQuery("""SELECT * FROM LightMixer WHERE owner = :u""", u=u)
        my_soundmixers = db.GqlQuery("""SELECT * FROM SoundMixer WHERE owner = :u""", u=u)
        my_speakers = db.GqlQuery("""SELECT * FROM Speaker WHERE owner = :u""", u=u)
        my_photocameras = db.GqlQuery("""SELECT * FROM PhotoCamera WHERE owner = :u""", u=u)
        my_videocameras = db.GqlQuery("""SELECT * FROM VideoCamera WHERE owner = :u""", u=u)
        my_projectors = db.GqlQuery("""SELECT * FROM Projector WHERE owner = :u""", u=u)
        my_tvs = db.GqlQuery("""SELECT * FROM TV WHERE owner = :u""", u=u)
        my_scenography = db.GqlQuery("""SELECT * FROM Scenography WHERE owner = :u""", u=u)
        my_costumes = db.GqlQuery("""SELECT * FROM Costumes WHERE owner = :u""", u=u)
        self.render("mythings.html", my_lamps = my_lamps, my_cables = my_cables, my_dampers = my_dampers,
            my_lightmixers = my_lightmixers, my_soundmixers = my_soundmixers, my_speakers = my_speakers,
            my_photocameras = my_photocameras, my_videocameras = my_videocameras, my_scenography = my_scenography,
            my_costumes = my_costumes, my_projectors = my_projectors, my_tvs = my_tvs)

    def get(self):
        self.render_things()


#class that handles personal page with all things ie lamps, cables etc a user has borrowed
class Borrowed(Handler):
    """class that handles all things a user has borrowed, showing them all on one page"""
    def render_things(self):
        u = self.user.name
        borrowed_lamps = db.GqlQuery("""SELECT * FROM Lamp WHERE borrower = :u ORDER BY watt ASC""", u=u)
        borrowed_cables = db.GqlQuery("""SELECT * FROM Cable WHERE borrower = :u""", u=u)
        borrowed_dampers = db.GqlQuery("""SELECT * FROM Damper WHERE borrower = :u""", u=u)
        borrowed_lightmixers = db.GqlQuery("""SELECT * FROM LightMixer WHERE borrower = :u""", u=u)
        borrowed_soundmixers = db.GqlQuery("""SELECT * FROM SoundMixer WHERE borrower = :u""", u=u)
        borrowed_speakers = db.GqlQuery("""SELECT * FROM Speaker WHERE borrower = :u""", u=u)
        borrowed_photocameras = db.GqlQuery("""SELECT * FROM PhotoCamera WHERE borrower = :u""", u=u)
        borrowed_videocameras = db.GqlQuery("""SELECT * FROM VideoCamera WHERE borrower = :u""", u=u)
        borrowed_projectors = db.GqlQuery("""SELECT * FROM Projector WHERE borrower = :u""", u=u)
        borrowed_tvs = db.GqlQuery("""SELECT * FROM TV WHERE borrower = :u""", u=u)
        borrowed_scenography = db.GqlQuery("""SELECT * FROM Scenography WHERE borrower = :u""", u=u)
        borrowed_costumes = db.GqlQuery("""SELECT * FROM Costumes WHERE borrower = :u""", u=u)
        self.render("borrowed.html", borrowed_lamps = borrowed_lamps, borrowed_cables = borrowed_cables,
            borrowed_dampers = borrowed_dampers, borrowed_lightmixers = borrowed_lightmixers,
            borrowed_soundmixers = borrowed_soundmixers, borrowed_speakers = borrowed_speakers,
            borrowed_photocameras = borrowed_photocameras, borrowed_videocameras = borrowed_videocameras,
            borrowed_scenography = borrowed_scenography, borrowed_costumes = borrowed_costumes,
            borrowed_projectors = borrowed_projectors, borrowed_tvs = borrowed_tvs)

    def get(self):
        self.render_things()


#class that handles a page with all lamps
class AllLamps(Handler):
    """class that handles all lamps, showing them all on one page"""
    def render_things(self):
        all_lamps = db.GqlQuery("""SELECT * FROM Lamp ORDER BY lamptype ASC""")
        self.render("alllamps.html", all_lamps = all_lamps)

    def get(self):
        self.render_things()

#class that handles a page with all cables
class AllCables(Handler):
    """class that handles all cables, showing them all on one page"""
    def render_things(self):
        all_cables = db.GqlQuery("""SELECT * FROM Cable ORDER BY connection""")
        self.render("allcables.html", all_cables = all_cables)

    def get(self):
        self.render_things()

#class that handles a page with all dampers
class AllDampers(Handler):
    """class that handles all dampers, showing them all on one page"""
    def render_things(self):
        all_dampers = db.GqlQuery("""SELECT * FROM Damper ORDER BY model ASC""")
        self.render("alldampers.html", all_dampers = all_dampers)

    def get(self):
        self.render_things()

#class that handles a page with all lightmixers
class AllLightMixers(Handler):
    """class that handles all lightmixers, showing them all on one page"""
    def render_things(self):
        all_lightmixers = db.GqlQuery("""SELECT * FROM LightMixer ORDER BY model ASC""")
        self.render("alllightmixers.html", all_lightmixers = all_lightmixers)

    def get(self):
        self.render_things()

#class that handles a page with all soundmixers
class AllSoundMixers(Handler):
    """class that handles all soundmixers, showing them all on one page"""
    def render_things(self):
        all_soundmixers = db.GqlQuery("""SELECT * FROM SoundMixer ORDER BY model ASC""")
        self.render("allsoundmixers.html", all_soundmixers = all_soundmixers)

    def get(self):
        self.render_things()

#class that handles a page with all speakers
class AllSpeakers(Handler):
    """class that handles all speakers, showing them all on one page"""
    def render_things(self):
        all_speakers = db.GqlQuery("""SELECT * FROM Speaker""")
        self.render("allspeakers.html", all_speakers = all_speakers)

    def get(self):
        self.render_things()

#class that handles a page with all photocameras
class AllPhotoCameras(Handler):
    """class that handles all photocameras, showing them all on one page"""
    def render_things(self):
        all_photocameras = db.GqlQuery("""SELECT * FROM PhotoCamera ORDER BY digianal""")
        self.render("allphotocameras.html", all_photocameras = all_photocameras)

    def get(self):
        self.render_things()

#class that handles a page with all videocameras
class AllVideoCameras(Handler):
    """class that handles all videocameras, showing them all on one page"""
    def render_things(self):
        all_videocameras = db.GqlQuery("""SELECT * FROM VideoCamera ORDER BY resolution""")
        self.render("allvideocameras.html", all_videocameras = all_videocameras)

    def get(self):
        self.render_things()

#class that handles a page with all projectors
class AllProjectors(Handler):
    """class that handles all projectors, showing them all on one page"""
    def render_things(self):
        all_projectors = db.GqlQuery("""SELECT * FROM Projector ORDER BY resolution""")
        self.render("allprojectors.html", all_projectors = all_projectors)

    def get(self):
        self.render_things()

#class that handles a page with all tvs
class AllTVs(Handler):
    """class that handles all tvs, showing them all on one page"""
    def render_things(self):
        all_tvs = db.GqlQuery("""SELECT * FROM TV ORDER BY resolution""")
        self.render("alltvs.html", all_tvs = all_tvs)

    def get(self):
        self.render_things()

#class that handles a page with all scenography
class AllScenography(Handler):
    """class that handles all scenography, showing them all on one page"""
    def render_things(self):
        all_scenography = db.GqlQuery("""SELECT * FROM Scenography""")
        self.render("allscenography.html", all_scenography = all_scenography)

    def get(self):
        self.render_things()

#class that handles a page with all costumes
class AllCostumes(Handler):
    """class that handles all costumes, showing them all on one page"""
    def render_things(self):
        all_costumes = db.GqlQuery("""SELECT * FROM Costumes""")
        self.render("allcostumes.html", all_costumes = all_costumes)

    def get(self):
        self.render_things()


#class that handles and renders personal page
class MyProfile(Handler):
    """docstring for MyProfile"""
    def render_profile(self):
        u = self.user.name
        my_profile = db.GqlQuery("""SELECT * FROM User WHERE name = :u""", u=u)
        self.render("myprofile.html", my_profile=my_profile)

    def get(self):
        self.render_profile()



# The functions below check username, password and email for correct syntax in
# the signup form

def valid_username(username):
    username_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return username and username_RE.match(username)

def valid_firstname(firstname):
    firstname_RE = re.compile(r"^[a-zA-Z0-9_-]{2,20}$")
    return firstname and firstname_RE.match(firstname)

def valid_surname(surname):
    surname_RE = re.compile(r"^[a-zA-Z0-9_-]{2,20}$")
    return surname and surname_RE.match(surname)

def valid_password(password):
    password_RE = re.compile(r"^.{3,20}$")
    return password and password_RE.match(password)

def valid_email(email):
    email_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
    return not email or email_RE.match(email)

def valid_phone(phone):
    phone_RE = re.compile(r'^[0-9]{8}$')
    return not phone or phone_RE.match(phone)

#class that handles creating a user
class SignUpHandler(Handler):
    """class that renders the signup form and uses
       the functions above to check signup syntax"""
    def get(self):
        self.render('signup.html')

    def post(self):
        error_msg = False
        suc = self.request.get('signupcode')
        self.username = self.request.get('username')
        self.firstname = self.request.get('firstname')
        self.surname = self.request.get('surname')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.phone = self.request.get('phone')

        params = dict(suc = suc, username = self.username, firstname = self.firstname, surname = self.surname,
                email = self.email, phone = self.phone)

        if suc != "VELKOMMEN":
            params['signupcode_error'] = "Oprettelseskoden er ugyldig."
            error_msg = True

        if not valid_username(self.username):
            params['username_error'] = "Brugernavnet er ugyldigt."
            error_msg = True

        if not valid_firstname(self.firstname):
            params['firstname_error'] = "Du skal angive et navn, mellem 2 og 20 bogstaver."
            error_msg = True

        if not valid_surname(self.surname):
            params['surname_error'] = "Du skal angive et efternavn, mellem 2 og 20 bogstaver."
            error_msg = True

        if not valid_password(self.password):
            params['password_error'] = "Password is invalid."
            error_msg = True
        elif self.password != self.verify:
            params['verify_error'] = "Passwords didn't match."
            error_msg = True

        if not valid_email(self.email):
            params['email_error'] = "Email is invalid."
            error_msg = True

        if not valid_phone(self.phone):
            params['phone_error'] = "telefonnummer skal indeholde 8 tal."
            error_msg = True

        if error_msg:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

#class that handles signing up
class Register(SignUpHandler):
    """class for registering a user, if the user is new and unique"""
    def done(self):
        u = User.by_name(self.username)
        if u:
            message = 'Dette brugernavn er optaget. Vaelg venligst et andet.'
            self.render('signup.html', username_error = message)
        else:
            u = User.register(self.username, self.firstname, self.surname, self.password, self.email, self.phone)
            u.put()

            self.login(u)
            self.redirect('/mypage/welcome')

#class that handles logging in
class Login(Handler):
    """login class"""
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/mypage/welcome')
        else:
            message = 'Invalid login'
            self.render('login.html', error = message)

#class that handles logging out
class Logout(Handler):
    """logout class"""
    def get(self):
        self.logout()
        self.redirect('/mypage/signup')

#class that renders welcome page
class WelcomeHandler(Handler):
    """class that renders a welcome page when a new user has signed up"""
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/mypage/signup')

#class that handles the main page
class MainPage(Handler):
    """class that renders the main page"""
    def get(self):
        if self.user:
            self.render("mypage.html", username = self.user.name)
        else:
            self.redirect('/mypage/login')

#class that handles a list of all members
class Members(Handler):
    """Class that renders a list of members"""
    def render_members(self):
        members = db.GqlQuery("""SELECT * FROM User ORDER BY firstname ASC""")
        self.render("members.html", members = members)

    def get(self):
        self.render_members()



app = webapp2.WSGIApplication([('/', Entrance),
                               ('/mypage', MainPage),
                               ('/mypage/newthing', NewThing),
                               ('/mypage/([0-9]+)', PostHandler),
                               ('/mypage/signup', Register),
                               ('/mypage/welcome', WelcomeHandler),
                               ('/mypage/login', Login),
                               ('/mypage/logout', Logout),
                               ('/mypage/mythings', MyThings),
                               ('/mypage/myprofile', MyProfile),
                               ('/mypage/newlamp', NewLamp),
                               ('/mypage/editlamp/([0-9]+)', EditLamp),
                               ('/mypage/deletelamp/([0-9]+)', DeleteLamp),
                               ('/mypage/newcable', NewCable),
                               ('/mypage/editcable/([0-9]+)', EditCable),
                               ('/mypage/deletecable/([0-9]+)', DeleteCable),
                               ('/mypage/newdamper', NewDamper),
                               ('/mypage/editdamper/([0-9]+)', EditDamper),
                               ('/mypage/deletedamper/([0-9]+)', DeleteDamper),
                               ('/mypage/newlightmixer', NewLightMixer),
                               ('/mypage/editlightmixer/([0-9]+)', EditLightMixer),
                               ('/mypage/deletelightmixer/([0-9]+)', DeleteLightMixer),
                               ('/mypage/newsoundmixer', NewSoundMixer),
                               ('/mypage/editsoundmixer/([0-9]+)', EditSoundMixer),
                               ('/mypage/deletesoundmixer/([0-9]+)', DeleteSoundMixer),
                               ('/mypage/newspeaker', NewSpeaker),
                               ('/mypage/editspeaker/([0-9]+)', EditSpeaker),
                               ('/mypage/deletespeaker/([0-9]+)', DeleteSpeaker),
                               ('/mypage/newphotocamera', NewPhotoCamera),
                               ('/mypage/editphotocamera/([0-9]+)', EditPhotoCamera),
                               ('/mypage/deletephotocamera/([0-9]+)', DeletePhotoCamera),
                               ('/mypage/newvideocamera', NewVideoCamera),
                               ('/mypage/editvideocamera/([0-9]+)', EditVideoCamera),
                               ('/mypage/deletevideocamera/([0-9]+)', DeleteVideoCamera),
                               ('/mypage/newprojector', NewProjector),
                               ('/mypage/editprojector/([0-9]+)', EditProjector),
                               ('/mypage/deleteprojector/([0-9]+)', DeleteProjector),
                               ('/mypage/newtv', NewTV),
                               ('/mypage/edittv/([0-9]+)', EditTV),
                               ('/mypage/deletetv/([0-9]+)', DeleteTV),
                               ('/mypage/newscenography', NewScenography),
                               ('/mypage/editscenography/([0-9]+)', EditScenography),
                               ('/mypage/deletescenography/([0-9]+)', DeleteScenography),
                               ('/mypage/newcostume', NewCostume),
                               ('/mypage/editcostume/([0-9]+)', EditCostume),
                               ('/mypage/deletecostume/([0-9]+)', DeleteCostume),
                               ('/mypage/members', Members),
                               ('/mypage/searchtype', SearchType),
                               ('/mypage/alllamps', AllLamps),
                               ('/mypage/allcables', AllCables),
                               ('/mypage/alldampers', AllDampers),
                               ('/mypage/alllightmixers', AllLightMixers),
                               ('/mypage/allsoundmixers', AllSoundMixers),
                               ('/mypage/allspeakers', AllSpeakers),
                               ('/mypage/allphotocameras', AllPhotoCameras),
                               ('/mypage/allvideocameras', AllVideoCameras),
                               ('/mypage/allprojectors', AllProjectors),
                               ('/mypage/alltvs', AllTVs),
                               ('/mypage/allscenography', AllScenography),
                               ('/mypage/allcostumes', AllCostumes),
                               ('/mypage/borrowed', Borrowed)
                             ],
                             debug=True)

