from app import db, jwt
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@jwt.user_lookup_loader
def user_loader_callback(jwt_header: dict, jwt_data: dict) -> object:
    """
    HUser loader function which uses the JWT identity to retrieve a user object.
    Method is called on protected routes

    Parameters
    ----------
    jwt_header : dictionary
        header data of the JWT
    jwt_data : dictionary
        payload data of the JWT

    Returns
    -------
    object
        Returns a Collectors object containing the user information
    """
    return Collectors.query.filter_by(id=jwt_data["sub"]).first()


# defines the Collectors database table
class Collectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    mobile=db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), unique=False, nullable=False)
    gender = db.Column(db.Integer, default=0)
    introduction = db.Column(db.String(256))
    collections = db.relationship("Collections", backref="user", lazy="dynamic")
    comments = db.relationship("Comments", backref="user", lazy="dynamic")
    tasks = db.relationship("Tasks", backref="user", lazy="dynamic")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
        """
        Helper function to launch a background task

        Parameters
        ----------
        name : str
            Name of the task to launch
        description : str
            Description of the task to launch

        Returns
        -------
        object
            A Tasks object containing the task information
        """
        rq_job = current_app.task_queue.enqueue(
            "app.tasks.long_running_jobs" + name, **kwargs
        )
        task = Tasks(
            task_id=rq_job.get_id(), name=name, description=description, user=self
        )
        db.session.add(task)

        return task

    def get_items(self) -> list:
        return Items.query.filter_by(user=self, is_deleted=False).all()

    def get_collections(self) -> list:
        return Collections.query.filter_by(user=self, is_deleted=False).all()

class Collections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.String(140))
    image = db.Column(db.String(140))
    type=db.Column(db.Integer)
    status=db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    items = db.relationship("Items", backref="collections", lazy="dynamic")
    collector_id = db.Column(db.Integer, db.ForeignKey("collectors.id"))


class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    original = db.Column(db.String(50))
    dimension = db.Column(db.String(50))
    weight = db.Column(db.Float)
    status = db.Column(db.Integer, default=0)
    description = db.Column(db.String(2000))
    collected_date = db.Column(db.Date)
    is_deleted = db.Column(db.Boolean)
    age_id = db.Column(db.Integer, db.ForeignKey("ages.id"))
    material_id = db.Column(db.Integer, db.ForeignKey("materials.id"))
    collection_id = db.Column(db.Integer, db.ForeignKey("collections.id"))
    collector_id = db.Column(db.Integer, db.ForeignKey("collectors.id"))
    images =  db.relationship("Images", backref="items", lazy="dynamic")
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Ages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Materials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))
    name = db.Column(db.String(500))
    is_deleted = db.Column(db.Boolean)
