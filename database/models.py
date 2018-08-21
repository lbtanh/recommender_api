from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns, connection
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
from cassandra.util import uuid_from_time


class UserBusinessDiscovery(Model):
    __table_name__ = "user_business_discovery"

    id = columns.BigInt(primary_key=True)
    name = columns.Text()
    biography = columns.Text()
    media_count = columns.Integer()
    comments_count = columns.Integer()
    likes_count = columns.Integer()
    followers_count = columns.Integer()
    username = columns.Text()
    profile_picture_url = columns.Text()
    ts = columns.UUID(primary_key=True)