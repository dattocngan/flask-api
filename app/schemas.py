from app import ma
from app.models import Collectors, Collections, Items, Images, Ages, Materials

from marshmallow import Schema, fields


class CollectorsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Collectors


class CollectorsDeserializingSchema(Schema):
    mobile = fields.String()
    password = fields.String()
    fullname = fields.String()
    email = fields.Email()
    description = fields.String()
    birthday = fields.Date()


class ItemsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Items


class CollectionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Collections


class ImagesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Images


class AgesSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ages


class MaterialsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Materials


