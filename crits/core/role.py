import logging

from mongoengine import Document, EmbeddedDocument
from mongoengine import EmbeddedDocumentField
from mongoengine import StringField, ListField, BooleanField

from django.conf import settings

from crits.actors.actor import ActorAccess, ActorIdentifierAccess
from crits.core.crits_mongoengine import CritsDocument, CritsSchemaDocument
from crits.core.crits_mongoengine import CritsDocumentFormatter
from crits.core.source_access import SourceAccess

logger = logging.getLogger(__name__)

class EmbeddedSourceACL(EmbeddedDocument, CritsDocumentFormatter):
    """
    Source ACL.
    """

    name = StringField(required=True)
    read = BooleanField(default=False)
    write = BooleanField(default=False)

class Role(CritsDocument, CritsSchemaDocument, Document):
    """
    CRITs Role Class
    """

    meta = {
        "collection": settings.COL_ROLES,
        "crits_type": 'Role',
        "latest_schema_version": 1,
        "schema_doc": {
        },
    }

    name = StringField(required=True)
    active = StringField(default="on")
    sources = ListField(EmbeddedDocumentField(EmbeddedSourceACL))

    # TLOs
    Actor = EmbeddedDocumentField(ActorAccess, required=True,
                                  default=ActorAccess())
    ActorIdentifier = EmbeddedDocumentField(ActorIdentifierAccess,
                                            required=True,
                                            default=ActorIdentifierAccess())

    # Add New
    add_new_actor_identifier_type = BooleanField(default=False)
    add_new_backdoor = BooleanField(default=False)
    add_new_exploit = BooleanField(default=False)
    add_new_indicator_action = BooleanField(default=False)
    add_new_raw_data_type = BooleanField(default=False)
    add_new_source = BooleanField(default=False)
    add_new_user_role = BooleanField(default=False)
    add_new_tlds = BooleanField(default=False)

    # Control Panel
    control_panel_read = BooleanField(default=False)
    control_panel_system_read = BooleanField(default=False)
    control_panel_general_read = BooleanField(default=False)
    control_panel_general_edit = BooleanField(default=False)
    control_panel_crits_read = BooleanField(default=False)
    control_panel_crits_edit = BooleanField(default=False)
    control_panel_ldap_read = BooleanField(default=False)
    control_panel_ldap_edit = BooleanField(default=False)
    control_panel_security_read = BooleanField(default=False)
    control_panel_security_edit = BooleanField(default=False)
    control_panel_downloading_read = BooleanField(default=False)
    control_panel_downloading_edit = BooleanField(default=False)
    control_panel_system_services_read = BooleanField(default=False)
    control_panel_system_services_edit = BooleanField(default=False)
    control_panel_logging_read = BooleanField(default=False)
    control_panel_logging_edit = BooleanField(default=False)
    control_panel_items_read = BooleanField(default=False)
    control_panel_users_read = BooleanField(default=False)
    control_panel_users_add = BooleanField(default=False)
    control_panel_users_edit = BooleanField(default=False)
    control_panel_users_active = BooleanField(default=False)
    control_panel_services_read = BooleanField(default=False)
    control_panel_services_edit = BooleanField(default=False)
    control_panel_audit_log_read = BooleanField(default=False)

    # Recent Activity
    recent_activity_read = BooleanField(default=False)

    # Structured Exchange Formats
    stix_import_add = BooleanField(default=False)

    # Timelines
    dns_timeline_read = BooleanField(default=False)
    emails_timeline_read = BooleanField(default=False)
    indicators_timeline_read = BooleanField(default=False)


    def migrate(self):
        """
        Migrate to the latest schema version.
        """

        pass

    def make_all_true(self):
        """
        Makes all ACL options True
        """

        for p in self._data.iterkeys():
            if p in settings.CRITS_TYPES.iterkeys():
                attr = getattr(self, p)
                # Modify the attributes.
                for x in attr._data.iterkeys():
                    setattr(attr, x, True)
                # Set the attribute on the ACL.
                setattr(self, p, attr)
            elif p == "sources":
                for s in getattr(self, p):
                    for x in s._data.iterkeys():
                        if x != "name":
                            setattr(s, x, True)
            elif p not in ('name', 'schema_version', 'active', 'id',
                           'unsupported_attrs'):
                setattr(self, p, True)

    def add_all_sources(self):
        """
        Add all of the sources to this Role
        """

        sources = SourceAccess.objects()
        for s in sources:
            self.add_source(s.name)

    def add_source(self, source):
        """
        Add a source to this Role.

        :param source: The name of the source.
        :type source: str
        """

        found = False
        for s in self.sources:
            if s.name == source:
                found = True
                break
        if not found:
            src = SourceAccess.objects(name=source).first()
            if src:
                new_src = EmbeddedSourceACL(name=source)
                self.sources.append(new_src)
