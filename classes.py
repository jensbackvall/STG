from google.appengine.ext import db

class User(db.Model):
    """class that creates the basic database specifics for a user"""
    name = db.StringProperty(required = True)
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
    def register(cls, name, pw, email=None, phone=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
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
    owner = db.ReferenceProperty(User, collection_name='lamps')
    brand = db.StringProperty(required=True)
    model = db.StringProperty(required=True)
    watt = db.IntegerProperty(required=True)
    description = db.TextProperty()
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class Cable(db.Model):
    """class that creates the basic database structure for Cable"""
    owner = db.ReferenceProperty(User, collection_name='cables')
    connection = db.TextProperty(required=True)
    length = db.IntegerProperty(required=True)
    description = db.TextProperty()
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class Damper(db.Model):
    """class that creates the basic database structure for Damper"""
    owner = db.ReferenceProperty(User, collection_name='dampers')
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class LightMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.ReferenceProperty(User, collection_name='lightmixers')
    brand = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class SoundMixer(db.Model):
    """class that creates the basic database structure for Mixer"""
    owner = db.ReferenceProperty(User, collection_name='soundmixers')
    brand = db.StringProperty(required=True)
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class Speaker(db.Model):
    """class that creates the basic database structure for Speaker"""
    owner = db.ReferenceProperty(User, collection_name='speakers')
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class PhotoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.ReferenceProperty(User, collection_name='photocameras')
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class VideoCamera(db.Model):
    """class that creates the basic database structure for Camera"""
    owner = db.ReferenceProperty(User, collection_name='videocameras')
    brand = db.StringProperty(required=True)
    model = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class Scenography(db.Model):
    """class that creates the basic database structure for Scenography"""
    owner = db.ReferenceProperty(User, collection_name='scenography')
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()

class Costumes(object):
    """class that creates the basic database structure for Costume"""
    owner = db.ReferenceProperty(User, collection_name='costumes')
    description = db.TextProperty(required=True)
    image = db.BlobProperty()
    booked = db.BooleanProperty()







