DROP KEYSPACE IF EXISTS aify_recommend;
CREATE KEYSPACE aify_recommend WITH replication = {'class': 'NetworkTopologyStrategy', 'DC1': 1};