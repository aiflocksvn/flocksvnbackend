from django.db import models
import datetime
from django.utils import timezone
from django.conf import settings


def convert_tstamp(response):
    """
    Convert a Stripe API timestamp response (unix epoch) to a native datetime.
    """
    if response is None:
        # Allow passing None to convert_tstamp()
        return response

    # Overrides the set timezone to UTC - I think...
    tz = timezone.utc if settings.USE_TZ else None

    return datetime.datetime.fromtimestamp(response, tz)


class StripeDateTimeField(models.DateTimeField):
    """A field used to define a DateTimeField value according to djstripe logic."""

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if "help_text" in kwargs:
            del kwargs["help_text"]
        return name, path, args, kwargs

    def stripe_to_db(self, data):
        """Convert the raw timestamp value to a DateTime representation."""
        val = data.get(self.name)

        # Note: 0 is a possible return value, which is 'falseish'
        if val is not None:
            return convert_tstamp(val)
