from settings.default import *
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

# neonion specific
ANNOTATION_STORE_URL = "http://127.0.0.1:5000"
ELASTICSEARCH_URL = "http://127.0.0.1:9200"
DEFAULT_USER_ACTIVE_STATE = True

# annotation event dispatch
DISPATCHER_ENDPOINT = "http://ADDURL/store"
DISPATCHER_SECRET_TOKEN = "T0KEN"

# set environment
DEBUG = True

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "name": "givenName",
    "surname": "sn",
    "email": "mail"
}

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'accounts.backends.EmailAuthBackend'
)
AUTH_LDAP_SERVER_URI = "ldap://mpiwg-ldap.mpiwg-berlin.mpg.de:7389"

AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch("cn=users,dc=mpiwg-berlin,dc=mpg,dc=de",
    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

AUTH_LDAP_PROFILE_ATTR_MAP = {"home_directory": "homeDirectory"}

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("cn=groups,dc=mpiwg-berlin,dc=mpg,dc=de",
    ldap.SCOPE_SUBTREE, "(objectClass=posixGroup)"
)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

AUTH_LDAP_MIRROR_GROUPS = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": "cn=dept_gmpg,cn=groups,dc=mpiwg-berlin,dc=mpg,dc=de",
    #"is_active": "cn=dept_gmpg,cn=groups,dc=mpiwg-berlin,dc=mpg,dc=de",
}