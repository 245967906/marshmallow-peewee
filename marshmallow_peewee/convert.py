import peewee as pw
from marshmallow import fields, validate as ma_validate
from marshmallow.compat import OrderedDict

from .fields import ForeignKey


class ModelConverter(object):

    """ Convert Peewee model to Marshmallow schema."""

    TYPE_MAPPING = [
        (pw.AutoField, fields.String),
        (pw.IntegerField, fields.Integer),
        (pw.CharField, fields.String),
        (pw.BooleanField, fields.Boolean),
        (pw.DateTimeField, fields.DateTime),
        (pw.DateField, fields.Date),
        (pw.TextField, fields.String),
        (pw.ForeignKeyField, ForeignKey),
        (pw.FloatField, fields.Float),
        (pw.DecimalField, fields.Decimal),
        (pw.TimeField, fields.Time),
        (pw.BigIntegerField, fields.Integer),
        (pw.SmallIntegerField, fields.Integer),
        (pw.DoubleField, fields.Float),
        (pw.FixedCharField, fields.String),
        (pw.UUIDField, fields.UUID),
    ]

    def __init__(self, opts):
        self.opts = opts

    def fields_for_model(self, model):
        result = OrderedDict()
        for field in model._meta.sorted_fields:
            ma_field = self.convert_field(field)
            if ma_field:
                result[field.name] = ma_field
        return result

    def convert_field(self, field):
        params = {
            'allow_none': field.null,
            'attribute': field.name,
            'required': not field.null and field.default is None,
            'validate': field.python_value,
        }

        if field.default is not None:
            params['default'] = field.default

        method = getattr(self, 'convert_' + field.__class__.__name__, self.convert_default)
        return method(field, **params)

    def convert_default(self, field, **params):
        """Return raw field."""
        for klass, ma_field in self.TYPE_MAPPING:
            if isinstance(field, klass):
                return ma_field(**params)
        return fields.Raw(**params)

    def convert_AutoField(self, field, required=False, **params):
        return fields.String(dump_only=self.opts.dump_only_pk, required=False, **params)

    def convert_CharField(self, field, validate=None, **params):
        validate = ma_validate.Length(max=field.max_length)
        return fields.String(validate=validate, **params)

    def convert_BooleanField(self, field, validate=None, **params):
        return fields.Boolean(**params)
