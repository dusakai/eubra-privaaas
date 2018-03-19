# -*- coding: utf-8 -*-
import json
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime, Numeric, Text, Unicode, UnicodeText
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_i18n import make_translatable, translation_base, Translatable
import sqlite3


make_translatable(options={'locales': ['pt', 'en', 'es'],
                           'auto_create_locales': True,
                           'fallback_locale': 'en'})

db = SQLAlchemy ()
#db.create_all()

# noinspection PyClassHasNoInit
class DataSourceFormat:
    XML_FILE = 'XML_FILE'
    NETCDF4 = 'NETCDF4'
    HDF5 = 'HDF5'
    SHAPEFILE = 'SHAPEFILE'
    TEXT = 'TEXT'
    CUSTOM = 'CUSTOM'
    JSON = 'JSON'
    CSV = 'CSV'
    PICKLE = 'PICKLE'


# noinspection PyClassHasNoInit
class StorageType:
    HDFS = 'HDFS'
    OPHIDIA = 'OPHIDIA'
    ELASTIC_SEARCH = 'ELASTIC_SEARCH'
    MONGODB = 'MONGODB'
    POSTGIS = 'POSTGIS'
    HBASE = 'HBASE'
    CASSANDRA = 'CASSANDRA'
    JSON = 'JSON'


# noinspection PyClassHasNoInit
class DataType:
    FLOAT = 'FLOAT'
    LAT_LONG = 'LAT_LONG'
    TIME = 'TIME'
    DOUBLE = 'DOUBLE'
    DECIMAL = 'DECIMAL'
    ENUM = 'ENUM'
    CHARACTER = 'CHARACTER'
    LONG = 'LONG'
    DATETIME = 'DATETIME'
    VECTOR = 'VECTOR'
    TEXT = 'TEXT'
    DATE = 'DATE'
    INTEGER = 'INTEGER'
    TIMESTAMP = 'TIMESTAMP'

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code

# noinspection PyClassHasNoInit
class PrivacyType:
    IDENTIFIER = 'IDENTIFIER'
    QUASI_IDENTIFIER = 'QUASI_IDENTIFIER'
    SENSITIVE = 'SENSITIVE'
    NON_SENSITIVE = 'NON_SENSITIVE'

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code

class AnonymTechnique:
    GENERALIZATION = 'GENERALIZATION'
    SUPPRESSION = 'SUPPRESSION'
    MASK = 'MASK'
    ENCRYPTION = "ENCRYPTION"
    NO_TECHNIQUE = 'NO_TECHNIQUE'

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code



class DataSource(db.Model):
    """ Data source in Lemonade system (anything that stores data. """
    __tablename__ = 'data_source'

    # Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    enabled = Column(Boolean, default=True)
    read_only = Column(Boolean, default=True)
    url = Column(String(200))
    created = Column(DateTime, default=func.now())
    format = Column(Enum(*DataSourceFormat.__dict__.keys(),
                         name='DataSourceFormatEnumType'))
    provenience = Column(Text)
    estimated_rows = Column(Integer)
    estimated_size_in_mega_bytes = Column(Numeric(10, 2))
    expiration = Column(String(200))
    user_id = Column(Integer)
    user_login = Column(String(50))
    user_name = Column(String(200))
    tags = Column(String(100))
    temporary = Column(Boolean, default=False)
    workflow_id = Column(Integer)
    task_id = Column(Integer)
    __mapper_args__ = {
        'order_by': 'name'
    }

    #construcutor
    def __init__ (self, name, url, storage_id):
        self.name = name
        self.url = url
        self.storage_id = storage_id


    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)

class DataPolicy(db.Model):
    """ Data source in Lemonade system (anything that stores data. """
    __tablename__ = 'data_policy'

    # Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    datasetname = Column(String(500))
    enabled = Column(Boolean, default=True)
    read_only = Column(Boolean, default=True)
    url = Column(String(200))
    created = Column(DateTime, default=func.now())
    format = Column(Enum(*DataSourceFormat.__dict__.keys(),
                         name='DataSourceFormatEnumType'))
    provenience = Column(Text)
    estimated_rows = Column(Integer)
    estimated_size_in_mega_bytes = Column(Numeric(10, 2))
    expiration = Column(String(200))
    user_id = Column(Integer)
    user_login = Column(String(50))
    user_name = Column(String(200))
    tags = Column(String(100))
    temporary = Column(Boolean, default=False)
    workflow_id = Column(Integer)
    task_id = Column(Integer)
    __mapper_args__ = {
        'order_by': 'name'
    }

    # Associations
    data_source_id = Column(Integer,
                            ForeignKey("data_source.id"), nullable=False)
    data_source = relationship("DataSource", foreign_keys=[data_source_id])

    #construcutor
    def __init__ (self, name, url, datasetname, data_source_id):
        self.name = name
        self.url = url
        self.datasetname = datasetname
        self.data_source_id = data_source_id


    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class Attribute(db.Model):
    """ Data source attribute. """
    __tablename__ = 'attribute'

    # Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    type = Column(Enum(*DataType.__dict__.keys(),
                       name='DataTypeEnumType'))
    size = Column(Integer)
    precision = Column(Integer)
    nullable = Column(Boolean)
    enumeration = Column(Boolean)
    missing_representation = Column(String(200))
    feature = Column(Boolean, default=True)
    label = Column(Boolean, default=True)
    distinct_values = Column(Integer)
    mean_value = Column(Float)
    median_value = Column(String(200))
    max_value = Column(String(200))
    min_value = Column(String(200))
    std_deviation = Column(Float)
    missing_total = Column(String(200))
    deciles = Column(Text)

    # Associations
    data_source_id = Column(Integer,
                            ForeignKey("data_source.id"), nullable=False)
    data_source = relationship("DataSource", foreign_keys=[data_source_id],
                               backref=backref(
                                   "attributes",
                                   cascade="all, delete-orphan"))
#construcutor
    def __init__ (self, name, data_source_id):
        self.name = name
        self.data_source_id = data_source_id


    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name
        #return '<Instance {}: {}>'.format(self.name, self.id)
        #return '{}:{}'.format(self.name, self.id)
        #return '<Instance {}: {}>'.format(self.__class__, self.id)


### adicionando a tabela de privacidade


class PrivacyRisk(db.Model):
    """ Data source attribute. """
    __tablename__ = 'privacy_risk'

    # Fields
    id = Column(Integer, primary_key=True)
    fieldName = Column(String(200))
    privacyAttType = Column(Enum(*PrivacyType.__dict__.keys(),
                                name='PrivacyTypeEnumType'), nullable=False)
    anonymizationTechnique = Column(Enum(*AnonymTechnique.__dict__.keys(),
                                name='AnonymTechniqueEnumType'), nullable=False)
    hierarchy = Column(String(200))
    privacyModel = Column(String(200))
    privacyModelParameters = Column(String(200))
    hierarchyStructureType = Column(String(200))

    # Associations
    attribute_id = Column(Integer,
                            ForeignKey("attribute.id"), nullable=False)
    attribute = relationship("Attribute", foreign_keys=[attribute_id],
                               backref=backref(
                                   "attributes",
                                   cascade="all, delete-orphan"))
    # Associations
    ds_id = Column(Integer,
                            ForeignKey("data_source.id"), nullable=False)
    ds = relationship("DataSource", foreign_keys=[ds_id],
                               backref=backref(
                                   "dss",
                                   cascade="all, delete-orphan"))
    # Associations
    policy_id = Column(Integer,
                            ForeignKey("data_policy.id"), nullable=False)
    policy = relationship("DataPolicy", foreign_keys=[policy_id],
                               backref=backref(
                                   "datapolicys",
                                   cascade="all, delete-orphan"))
    #construcutor
    def __init__ (self, fieldName, privacyAttType, anonymizationTechnique, hierarchy, attribute_id, ds_id, policy_id):
        self.fieldName = fieldName
        self.privacyAttType = privacyAttType
        self.anonymizationTechnique = anonymizationTechnique
        self.hierarchy = hierarchy
        self.attribute_id = attribute_id
        self.ds_id = ds_id
        self.policy_id = policy_id


    def __unicode__(self):
        return self.privacyAttType

    def __repr__(self):
        return '{},{}'.format(self.anonymizationTechnique, self.hierarchy)
        #return '{}:{}'.format(self.anonymizationTechnique, self.attribute_id)
        #return '<Instance {}: {}>'.format(self.anonymizationTechnique, self.attribute_id)
        #return '<Instance {}: {}>'.format(self.__class__, self.id)


### fim da tabela de privacidade

class Storage(db.Model):
    """ Type of storage used by data sources """
    __tablename__ = 'storage'
    __table_args__ = {'sqlite_autoincrement': True}
    # Fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    type = Column(Enum(*StorageType.__dict__.keys(),
                       name='StorageTypeEnumType'))
    url = Column(String(1000))

#construcutor
    def __init__ (self, name, url):
        self.name = name
        self.url = url

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)
