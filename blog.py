
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
    booked = db.BooleanProperty()

class Cable(db.Model):
    """class that creates the basic database structure for Cable"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    connection = db.StringProperty(required=True)
    length = db.IntegerProperty(required=True)
    description = db.TextProperty()
    booked = db.BooleanProperty()

class Damper(db.Model):
    """class that creates the basic database structure for Damper"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    description = db.TextProperty()
    booked = db.BooleanProperty()

class LightMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    description = db.TextProperty()
    booked = db.BooleanProperty()

class SoundMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    description = db.TextProperty()
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
    booked = db.BooleanProperty()

class PhotoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty()
    booked = db.BooleanProperty()

class VideoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty()
    booked = db.BooleanProperty()

class Scenography(db.Model):
    """class that creates the basic database structure for Scenography"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    linktext = db.TextProperty()
    booked = db.BooleanProperty()

class Costumes(db.Model):
    """class that creates the basic database structure for Costume"""
    owner = db.StringProperty(required=True)
    contact = db.PhoneNumberProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    linktext = db.TextProperty()
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
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            sm = SoundMixer(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                description = description)
            sm.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newsoundmixer.html", brand = brand, model = model,
                description = description, error = error)

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

#Class below handles new instances of PHOTOCAMERA.
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
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            pc = PhotoCamera(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                description = description)
            pc.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newphotocamera.html", brand = brand, model = model,
                description = description, error = error)

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
        model = self.request.get("model")
        description = self.request.get("description")

        if not description:
            description = "Ingen beskrivelse er givet."

        if brand and model:
            vc = VideoCamera(parent = blog_key(), owner = owner, contact = contact, brand = brand, model = model,
                description = description)
            vc.put()
            time.sleep(0.1)
            self.redirect("/mypage/mythings")
        else:
            error = "Du skal udfylde alle obligatorisk felter!"
            return self.render("newvideocamera.html", brand = brand, model = model,
                description = description, error = error)

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


#Class below links to creating new instances of lamp, speaker etc.
class SearchType(Handler):
    """class that renders a page for creating a new instance of a lamp, cable, speaker or other."""
    def get(self):
        if self.user:
            self.render("searchtype.html")
        else:
            error = "Du skal vaere logget ind for at oprette ting!"
            self.render('login.html', error=error)


#Class for shoeing a newly created blogpost.
class PostHandler(Handler):
    """class that shows a newly created blog post"""
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if not p:
            self.error(404)
            return self.render("404.html")

        self.render("permalink.html", p = p)


#Class for editing comments on blogposts
class EditPost(Handler):
    """class that opens an existing post for editing"""
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if not p:
            self.error(404)
            return self.render("404.html")

        if self.user.name == p.author:
            self.render("edit.html", p=p, subject=p.subject, content=p.content)
        else:
            error = "You need to be logged in to edit your post!"
            return self.render('login.html', error=error)

    def post(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        subject = self.request.get("subject")
        content = self.request.get("content")

        if self.user and self.user.name == p.author:
            if subject and content:
                p.subject = subject
                p.content = content
                p.put()
                self.redirect("/mypage/%s" % str(p.key().id()))
            else:
                error = "You have to fill in both subject and content fields!"
                self.render("edit.html", p=p, subject=subject, content=content,
                             error=error)
        else:
            error = "You need to be logged in to edit your post!"
            return self.render('login.html', error=error)


#Class for creating likes on blogposts
class LikeHandler(Handler):
    """class that handles likes for a blogpost, updating the posts number of
     likes and the people who have liked it"""
    def post(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        p.likes = p.likes + 1
        p.likers.append(self.user.name)

        if self.user.name != p.author:
            p.put()
            time.sleep(0.1)
            self.redirect("/mypage")


#Class for deleting blogposts
class DeletePost(Handler):
    """class for deleting a blog post"""
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if self.user.name == p.author:
            p.delete()
            message = "Your Post has been irrevocably DELETED!"
            self.render("mypage.html", p=p, message=message)
        else:
            error = "You can only delete your own posts!"
            return self.render("login.html", error=error)


#Database class for comments
class Comment(db.Model):
    """class that creates the basic database specifics for a comment"""
    comment = db.TextProperty(required=True)
    commentauthor = db.StringProperty(required=True)
    commentid = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


#Class for creating comments on blogposts
class CreateComment(Handler):
    """class that handles a new comment"""
    def get(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        if self.user:
            self.render("newcomment.html", p=p, subject=p.subject,
                        content=p.content)
        else:
            error = "You need to be logged in to comment posts!"
            return self.render('login.html', error=error)

    def post(self, post_id):
        key = db.Key.from_path('Posts', int(post_id), parent = blog_key())
        p = db.get(key)

        commentin = self.request.get("comment")
        comment = commentin.replace('\n', '<br>')
        commentauthor = self.user.name
        commentid = int(p.key().id())

        if self.user:
            if commentauthor and comment and commentid:
                c = Comment(parent = blog_key(), comment=comment,
                            commentauthor=commentauthor, commentid = commentid)
                c.put()
                time.sleep(0.1)
                self.redirect("/mypage")
            else:
                error = "You have to enter text in the comment field!"
                return self.render("newcomment.html", p=p, subject=p.subject,
                             content=p.content, error=error)

#Class for editing comments on blogposts
class EditComment(Handler):
    """class that let's a user edit his or her own comment"""
    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent = blog_key())
        c = db.get(key)

        if not c:
            self.error(404)
            return self.render("404.html")

        commented = c.comment.replace('<br>', '')

        if self.user:
            self.render("editcomment.html", c=c, commented=commented)
        else:
            error = "You need to be logged in to comment posts!"
            return self.render('login.html', error=error)

    def post(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent = blog_key())
        c = db.get(key)

        commentin = self.request.get("comment")
        comment = commentin.replace('\n', '<br>')
        commentid = c.commentid
        commentauthor = c.commentauthor

        if self.user:
            if commentauthor and comment and commentid:
                c.comment = comment
                c.commentauthor = commentauthor
                c.put()
                time.sleep(0.1)
                self.redirect("/mypage")
            else:
                error = "You have to enter text in the comment field!"
                return self.render("editcomment.html", c=c, commented=c.comment)

#Class for deleting comments on blogposts
class DeleteComment(Handler):
    """class for deleting a comment"""
    def get(self, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent = blog_key())
        c = db.get(key)

        if self.user.name == c.commentauthor:
            c.delete()
            message = "Your Comment has been irrevocably DELETED!"
            self.render("mypage.html", c=c, message = message)
        else:
            error = "You can only delete your own posts!"
            return self.render("login.html", error=error)

#class that handles personal page with all things ie lamps, cables etc
class MyThings(Handler):
    """class that handles users own posts, to show them all on one page"""
    def render_posts(self):
        u = self.user.name
        my_lamps = db.GqlQuery("""SELECT * FROM Lamp WHERE owner = :u ORDER BY watt ASC""", u=u)
        my_cables = db.GqlQuery("""SELECT * FROM Cable WHERE owner = :u""", u=u)
        my_dampers = db.GqlQuery("""SELECT * FROM Damper WHERE owner = :u""", u=u)
        my_lightmixers = db.GqlQuery("""SELECT * FROM LightMixer WHERE owner = :u""", u=u)
        my_soundmixers = db.GqlQuery("""SELECT * FROM SoundMixer WHERE owner = :u""", u=u)
        my_speakers = db.GqlQuery("""SELECT * FROM Speaker WHERE owner = :u""", u=u)
        my_photocameras = db.GqlQuery("""SELECT * FROM PhotoCamera WHERE owner = :u""", u=u)
        my_videocameras = db.GqlQuery("""SELECT * FROM VideoCamera WHERE owner = :u""", u=u)
        my_scenography = db.GqlQuery("""SELECT * FROM Scenography WHERE owner = :u""", u=u)
        my_costumes = db.GqlQuery("""SELECT * FROM Costumes WHERE owner = :u""", u=u)
        self.render("mythings.html", my_lamps = my_lamps, my_cables = my_cables, my_dampers = my_dampers,
            my_lightmixers = my_lightmixers, my_soundmixers = my_soundmixers, my_speakers = my_speakers,
            my_photocameras = my_photocameras, my_videocameras = my_videocameras, my_scenography = my_scenography,
            my_costumes = my_costumes)

    def get(self):
        self.render_posts()


#class that handles a page with all lamps
class AllLamps(Handler):
    """class that handles all lamps, showing them all on one page"""
    def render_posts(self):
        all_lamps = db.GqlQuery("""SELECT * FROM Lamp ORDER BY lamptype ASC""")
        self.render("alllamps.html", all_lamps = all_lamps)

    def get(self):
        self.render_posts()

#class that handles a page with all cables
class AllCables(Handler):
    """class that handles all cables, showing them all on one page"""
    def render_posts(self):
        all_cables = db.GqlQuery("""SELECT * FROM Cable ORDER BY connection""")
        self.render("allcables.html", all_cables = all_cables)

    def get(self):
        self.render_posts()

#class that handles a page with all dampers
class AllDampers(Handler):
    """class that handles all dampers, showing them all on one page"""
    def render_posts(self):
        all_dampers = db.GqlQuery("""SELECT * FROM Damper ORDER BY model ASC""")
        self.render("alldampers.html", all_dampers = all_dampers)

    def get(self):
        self.render_posts()

#class that handles a page with all lightmixers
class AllLightMixers(Handler):
    """class that handles all lightmixers, showing them all on one page"""
    def render_posts(self):
        all_lightmixers = db.GqlQuery("""SELECT * FROM LightMixer ORDER BY model ASC""")
        self.render("alllightmixers.html", all_lightmixers = all_lightmixers)

    def get(self):
        self.render_posts()

#class that handles a page with all soundmixers
class AllSoundMixers(Handler):
    """class that handles all soundmixers, showing them all on one page"""
    def render_posts(self):
        all_soundmixers = db.GqlQuery("""SELECT * FROM SoundMixer ORDER BY model ASC""")
        self.render("allsoundmixers.html", all_soundmixers = all_soundmixers)

    def get(self):
        self.render_posts()

#class that handles a page with all speakers
class AllSpeakers(Handler):
    """class that handles all speakers, showing them all on one page"""
    def render_posts(self):
        all_speakers = db.GqlQuery("""SELECT * FROM Speaker""")
        self.render("allspeakers.html", all_speakers = all_speakers)

    def get(self):
        self.render_posts()


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
        self.username = self.request.get('username')
        self.firstname = self.request.get('firstname')
        self.surname = self.request.get('surname')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.phone = self.request.get('phone')

        params = dict(username = self.username, firstname = self.firstname, surname = self.surname,
                email = self.email, phone = self.phone)

        if not valid_username(self.username):
            params['username_error'] = "Username is invalid."
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
    def render_posts(self):
        members = db.GqlQuery("""SELECT * FROM User ORDER BY firstname ASC""")
        self.render("members.html", members = members)

    def get(self):
        self.render_posts()



app = webapp2.WSGIApplication([('/', Entrance),
                               ('/mypage', MainPage),
                               ('/mypage/newthing', NewThing),
                               ('/mypage/edit/([0-9]+)', EditPost),
                               ('/mypage/([0-9]+)', PostHandler),
                               ('/mypage/signup', Register),
                               ('/mypage/welcome', WelcomeHandler),
                               ('/mypage/login', Login),
                               ('/mypage/logout', Logout),
                               ('/mypage/deleted/([0-9]+)', DeletePost),
                               ('/mypage/newcomment/([0-9]+)', CreateComment),
                               ('/mypage/editcomment/([0-9]+)',EditComment),
                               ('/mypage/deletecomment/([0-9]+)', DeleteComment),
                               ('/mypage/newlike/([0-9]+)', LikeHandler),
                               ('/mypage/mythings', MyThings),
                               ('/mypage/myprofile', MyProfile),
                               ('/mypage/newlamp', NewLamp),
                               ('/mypage/newcable', NewCable),
                               ('/mypage/newdamper', NewDamper),
                               ('/mypage/newlightmixer', NewLightMixer),
                               ('/mypage/newsoundmixer', NewSoundMixer),
                               ('/mypage/newspeaker', NewSpeaker),
                               ('/mypage/newphotocamera', NewPhotoCamera),
                               ('/mypage/newvideocamera', NewVideoCamera),
                               ('/mypage/newscenography', NewScenography),
                               ('/mypage/newcostume', NewCostume),
                               ('/mypage/members', Members),
                               ('/mypage/searchtype', SearchType),
                               ('/mypage/alllamps', AllLamps),
                               ('/mypage/allcables', AllCables),
                               ('/mypage/alldampers', AllDampers),
                               ('/mypage/alllightmixers', AllLightMixers),
                               ('/mypage/allsoundmixers', AllSoundMixers),
                               ('/mypage/allspeakers', AllSpeakers)
                             ],
                             debug=True)

