# -*- coding: utf-8 -*-
import os.path, xmltodict, requests, json, csv, sys, urllib, hashlib, unicodecsv
import sqlalchemy, sqlalchemy.orm
import collections
import ast
from flask import render_template, request, flash, url_for, redirect, send_from_directory
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, load_only, relationship
from sqlalchemy import func, distinct, update
from privacy import app, db
from privacy.models.models import DataSource, DataPolicy, Attribute, PrivacyRisk, Storage
from wtforms import Form, validators, SubmitField
from werkzeug.utils import secure_filename
from faker import Factory

###### anonymization functions ######
def decisionFunction(ds,fn,at,dt,dataset_value):
    faker_ctx = {}
    value = dataset_value[fn]
    detail = dt
    if at == 'GENERALIZATION':
        code = generalizationFunction(detail, value)
        dataset_value[fn] = code
        return (dataset_value)

    if at == 'ENCRYPTION':
        code = encryptionFunction(detail, value)
        dataset_value[fn] = code
        return (dataset_value)

    if at == 'MASK':
        details_dict = ast.literal_eval(detail)
        faker_obj  = Factory.create(details_dict['lang'])
        faker_ctx[details_dict['label_type']] = collections.\
            defaultdict(getattr(faker_obj, details_dict['label_type']))
        code = maskingFunction(faker_ctx, detail, value)
        dataset_value[fn] = code
        return (dataset_value)

    if at == 'SUPPRESSION':
        code = suppressionFunction(detail, value)
        dataset_value[fn] = code
        return (dataset_value)

def generalizationFunction(detail, value):
    try:
        if type(detail)==str:
            details = ast.literal_eval(detail)
        if type(detail==dict):
            detals = detail
        generailization_type = details['generalization_type']

        # truncateNumber or truncateString
        if generailization_type.lower() == 'truncate'.lower():
            hierarchy_detail = int(details['length'])
            if hierarchy_detail >=0:
                len_value = len(value)
                complete_value = len_value - hierarchy_detail
                truncateValueToStr = str (value)
                return truncateValueToStr[:hierarchy_detail]+'*'*complete_value
            else:
                len_value = len(value)
                complete_value =  len_value + hierarchy_detail
                truncateValueToStr = str (value)
                return '*'*complete_value+truncateValueToStr[hierarchy_detail:]

        # rangeStringToString
        if generailization_type.lower() == 'rangeStringToString'.lower():
            hierarchy_detail = details['hierarchy']
            for detail_value in hierarchy_detail:
                parts = detail_value.split(',');
                list_of_parts = list (parts)
                for ranges in list_of_parts:
                    range_value = ranges.split('=')
                    group = range_value[0]
                    b = range_value[1]
                    values_of_range = b.split('-')
                    for elements in values_of_range:
                        if value == elements:
                            return (group)

        # rangeNumberToString
        if generailization_type.lower() == 'rangeNumberToString'.lower():
            hierarchy_detail = details['hierarchy']
            for detail_value in hierarchy_detail:
                parts = detail_value.split(',');
                list_of_parts = list (parts)
                for ranges in list_of_parts:
                    range_value = ranges.split('=')
                    group = range_value[0]
                    b = range_value[1]
                    values_of_range = b.split('-')
                    range_start = float(values_of_range[0])
                    range_end = values_of_range[1]

                    if range_end == '':
                        if range_start < float (value):
                            return (group)
                    else:
                        range_end = float (range_end)
                        if range_start < float (value) < range_end:
                            return (group)

    except Exception as e:
        raise

# generalization string to string truncation function
def suppressionFunction (detail, value):
# def truncateString (len_truncation, value):
    value_detail = detail
    return value_detail

# encryptionFunction
def encryptionFunction (detail, value):
    detail = detail.lower().encode('utf-8')
    value = value.encode('utf-8')

    if detail == b'md5':
        h = hashlib.md5(value).hexdigest()
    elif detail == b'sha1':
        h = hashlib.sha1(value).hexdigest()
    elif detail == b'sha224':
        h = hashlib.sha224(value).hexdigest()
    elif detail == b'sha256':
        h = hashlib.sha256(value).hexdigest()
    elif detail == b'sha384':
        h = hashlib.sha384(value).hexdigest()
    elif detail == b'sha512':
        h = hashlib.sha512(value).hexdigest()
    else:
        h = 'invalid hierarchy'
    return h

# masking function
def maskingFunction(faker_ctx, detail, value):
    details = ast.literal_eval(detail)
    label_type = details['label_type']
    faker  = faker_ctx[label_type] #Factory.create(idiom)
    return faker[value]

def jsonToCsv (json_file, csvname):
    try:
        with open(csvname, 'w') as csvfile:
            dict_writer = csv.DictWriter(csvfile, json_file[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(json_file)
    except:
        flash('error')

def deleteFileDS(item_id, item_name, item_url):
    try:
        os.remove(os.path.join(item_url, item_name))
        if item_name.endswith('csv'):
            os.remove(os.path.join(item_url, item_name+'.json'))
    except OSError:
        pass
    try:
        db.session.query(DataSource.id).\
            filter(DataSource.id==item_id).delete()
        db.session.commit()
    except OSError:
        pass

def deleteFile(item_id, item_name, item_url):
    try:
        os.remove(os.path.join(item_url, item_name))
    except OSError:
        pass
    try:
        db.session.query(DataPolicy.id).\
            filter(DataPolicy.id==item_id).delete()
        db.session.commit()
    except OSError:
        pass
def deleteItems(item_id):
    db.session.query(PrivacyRisk.id).\
        filter(PrivacyRisk.id==item_id).delete()
    db.session.commit()

def deleteItemsAtt(item_id):
    db.session.query(Attribute.id).\
        filter(Attribute.id==item_id).delete()
    db.session.commit()

def orderTech(tech_hierarchy_list):
    tech_strategy = 'NO_TECHNIQUE'
    hierarchy_num_list = []
    hierarchy_strategy = ''

    for tech,hierarchy in tech_hierarchy_list:
        if tech == 'SUPPRESSION':
            tech_strategy = tech
            hierarchy_strategy = hierarchy
        if tech == 'ENCRYPTION':
            if tech_strategy == 'SUPPRESSION':
                pass
            else:
                tech_strategy = tech
                hierarchy_strategy = hierarchy
        if tech == 'MASK':
            if tech_strategy == 'SUPPRESSION' or tech_strategy == 'ENCRYPTION':
                pass
            else:
                tech_strategy = tech
                hierarchy_strategy = hierarchy
        if tech == 'GENERALIZATION':
            tech_strategy = tech
            if tech_strategy == 'SUPPRESSION' or tech_strategy == 'ENCRYPTION' or tech_strategy == 'MASK':
                pass
            else:
                details = ast.literal_eval(hierarchy)
                generailization_type = details['generalization_type']
                if details['generalization_type'] == 'truncate':
                    hierarchy_detail = int(details['length'])
                    hierarchy_num_list.append(hierarchy_detail)
                    min_value_for_truncate = min(hierarchy_num_list)
                    hierarchy_strategy = str({'generalization_type':'truncate','length': min_value_for_truncate})

                else:
                    hierarchy_strategy = hierarchy

    print (':p')
    return tech_strategy,hierarchy_strategy
