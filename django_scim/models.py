import pytz
from django.conf import settings
from django.core.urlresolvers import reverse


def to_utc(date):
    local_tz = pytz.timezone(settings.TIME_ZONE)
    return local_tz.localize(date).astimezone(pytz.utc)


class SCIMUser(object):
    def __init__(self, user):
        self.user = user

    @property
    def display_name(self):
        if self.user.first_name and self.user.last_name:
            return u'{0.first_name} {0.last_name}'.format(self.user)
        return self.user.username

    @property
    def emails(self):
        return {self.user.email: True}

    @property
    def locale(self):
        return self.preferred_language

    @property
    def preferred_language(self):
        """SCIM 1.1 has a stricter definition of locale and language code than
        used in most Django applications:

        preferredLanguage: "Valid values are concatenation of the ISO 639-1 two
                            letter language code, an underscore, and the ISO
                            3166-1 2 letter country code; e.g., 'en_US'
                            specifies the language English and country US."

        locale:            "A locale value is a concatenation of the ISO 639-1
                            two letter language code, an underscore, and the
                            ISO 3166-1 2 letter country code; e.g., 'en_US'
                            specifies the language English and country US."

        Since we don't have country codes, we're just going to pretend each
        language is following its most influential country.
        """
        country = {
            'en': 'US',
            'zh-cn': 'CN',
            'fr': 'FR',
            'de': 'DE',
            'hi': 'IN',
            'ja': 'JP',
            'pt-br': 'BR',
            'ru': 'RU',
            'es': 'ES',
        }
        lc = self.user.get_profile().language_code
        if lc in country:
            return '%s_%s' % (lc[:2], country[lc])

    def to_dict(self):
        d = {
            'schemas': ['urn:scim:schemas:core:1.0'],
            'id': str(self.user.id),
            'userName': self.user.username,
            'name': {
                'formatted': self.display_name,
                'familyName': self.user.last_name,
                'givenName': self.user.first_name,
            },
            'displayName': self.display_name,
            'emails': [{'value': email, 'primary': primary}
                       for email, primary in self.emails.iteritems()],
            'active': self.user.is_active,
            'groups': [],
            'meta': {
                'created': to_utc(self.user.date_joined).isoformat(),
                'lastModified': to_utc(self.user.date_joined).isoformat(),
                'location': reverse('scim-user', args=(self.user.id,))
            }
        }
    
        if self.preferred_language:
            d['preferredLanguage'] = self.preferred_language
        if self.locale:
            d['locale'] = self.locale
    
        return d
