"""Hong Kong specific Form helpers."""
from __future__ import unicode_literals

import re

from django.forms import CharField, ValidationError
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from localflavor.deprecation import DeprecatedPhoneNumberFormFieldMixin

hk_phone_digits_re = re.compile(r'^(?:852-?)?(\d{4})[-\.]?(\d{4})$')
hk_special_numbers = ('999', '992', '112')
hk_phone_prefixes = ('2', '3', '5', '6', '8', '9')
hk_formats = ['XXXX-XXXX', '852-XXXX-XXXX', '(+852) XXXX-XXXX',
              'XXXX XXXX', 'XXXXXXXX']


class HKPhoneNumberField(CharField, DeprecatedPhoneNumberFormFieldMixin):
    """
    A form field that validates Hong Kong phone numbers.

    The input format can be either one of the followings:
    'XXXX-XXXX', '852-XXXX-XXXX', '(+852) XXXX-XXXX',
    'XXXX XXXX', or 'XXXXXXXX'.
    The output format is 'XXXX-XXXX'.

    Note: The phone number shall not start with 999, 992, or 112.
          And, it should start with either 2, 3, 5, 6, 8, or 9.

    http://en.wikipedia.org/wiki/Telephone_numbers_in_Hong_Kong

    .. deprecated:: 1.4
        Use the django-phonenumber-field_ library instead.

    .. _django-phonenumber-field: https://github.com/stefanfoulis/django-phonenumber-field
    """

    default_error_messages = {
        'disguise': _('Phone number should not start with '
                      'one of the followings: %s.' %
                      ', '.join(hk_special_numbers)),
        'invalid': _('Phone number must be in one of the following formats: '
                     '%s.' % ', '.join(hk_formats)),
        'prefix': _('Phone number should start with '
                    'one of the followings: %s.' %
                    ', '.join(hk_phone_prefixes)),
    }

    def __init__(self, *args, **kwargs):
        super(HKPhoneNumberField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(HKPhoneNumberField, self).clean(value)

        if value in self.empty_values:
            return self.empty_value

        value = re.sub('(\(|\)|\s+|\+)', '', force_text(value))
        m = hk_phone_digits_re.search(value)
        if not m:
            raise ValidationError(self.error_messages['invalid'])

        value = '%s-%s' % (m.group(1), m.group(2))
        for special in hk_special_numbers:
            if value.startswith(special):
                raise ValidationError(self.error_messages['disguise'])

        prefix_found = map(value.startswith, hk_phone_prefixes)
        if not any(prefix_found):
            raise ValidationError(self.error_messages['prefix'])

        return value
