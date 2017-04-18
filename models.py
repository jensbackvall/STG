from google.appengine.ext import db

from blog.py import users_key, make_pw_hash


class User(db.Model):
    """class that creates the basic database specifics for a user"""
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class Posts(db.Model):
    """class that creates the basic database specifics for a blog post"""
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    likes = db.IntegerProperty()
    likers = db.StringListProperty()
    created = db.DateTimeProperty(auto_now_add=True)

    def render(self):
        self.render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class Comment(db.Model):
    """class that creates the basic database specifics for a comment"""
    comment = db.TextProperty(required=True)
    commentauthor = db.StringProperty(required=True)
    commentid = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


