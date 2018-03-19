# -*- coding: utf-8 -*-
import os.path, xmltodict, requests, shutil
import json, csv, sys, urllib, hashlib, unicodecsv
import sqlalchemy, sqlalchemy.orm
import collections
from collections import defaultdict
import ast
import subprocess
from subprocess import Popen, PIPE
from flask import render_template, request, flash, url_for, redirect, send_from_directory
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker, load_only, relationship
from sqlalchemy import func, distinct, update
from privacy import app, db
from privacy.models.models import DataSource, DataPolicy, Attribute, PrivacyRisk, Storage
from privacy.controllers.priva_functions import *
from privacy.models.forms import LoginForm, DataSet_PolicyForm
from wtforms import Form, validators, SubmitField
from werkzeug.utils import secure_filename
from faker import Factory

#Session = session.add(bind=db)
DBSession = scoped_session(sessionmaker())

#address folder
BASE_DIR_INPUT = 'privacy/static/up_dir/input/'
BASE_DIR_OUTPUT = 'privacy/static/up_dir/output/'
DIR_POLICIES = 'policies/'
DIR_DS_FILES = 'ds_files/'
DIR_HRISK_FILES = 'h_risk/'
ALLOWED_EXTENSIONS = set(['json', 'csv', 'xml'])

#login
@app.route ('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    return render_template('login.html',
    form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#initial page
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form.get("del_list") != None:
            f_del = request.form.get("del_list")
            q_ds_d = db.session.query(DataSource.id,\
                DataSource.name, DataSource.url).\
                filter(DataSource.name == f_del).all()

            for i,j,k in q_ds_d:
                q_pd_d = db.session.query(DataPolicy.id,\
                     DataPolicy.name, DataPolicy.url).\
                     filter(DataPolicy.data_source_id == i).all()

                q_att_del = db.session.query(Attribute.id).\
                    filter(Attribute.data_source_id == i).all()
                for o, in q_att_del:
                    func_del_file_att = deleteItemsAtt(o)
                if len (q_pd_d)>=1:
                    for l,m,n in q_pd_d:
                        q_pr_del = db.session.query(PrivacyRisk.id).\
                            filter(PrivacyRisk.policy_id == l).all()
                        for o, in q_pr_del:
                            func_del_att = deleteItems(o)
                        func_del_pol_file = deleteFile(l,m,n)
                func_del_ds_file = deleteFileDS(i,j,k)

        if request.files.get("file_dataset") != None:
            f_ds = request.files['file_dataset']
            if f_ds.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if f_ds and allowed_file(f_ds.filename):
                filename = secure_filename(f_ds.filename)
                name = filename
                url = BASE_DIR_INPUT+DIR_DS_FILES
                f_ds.save(url+name)
                storagedetails = Storage(name, url)
                db.session.add(storagedetails)
                db.session.commit()
                #list of dataset name
                storage_id = db.session.query(Storage.id).\
                    filter(name == Storage.name).all()
                #associate at last number
                id_list = [ids[0] for ids in storage_id]
                for label in id_list:
                    storage_id_inuse = label
                #DataSource details - save sqldatabase
                datasourcedetails = DataSource(name, url, storage_id_inuse)
                db.session.add(datasourcedetails)
                db.session.commit()
                db.session.close()
                #if json file
                if f_ds.filename.endswith('json'):
                    with open(url+name) as json_data:
                        data = json.load(json_data)
                    json_file_temp = data [0]
                    json_file_int = json_file_temp.keys()
                    for label in json_file_int:
                        data_source_id = db.session.query(DataSource.id).filter(name == DataSource.name).all()
                        id_label_list = [ids[0] for ids in data_source_id]
                        for n in id_label_list:
                            datasource_id_inuse = n
                        attribute_label = Attribute(label, datasource_id_inuse)
                        #Attribute details - save sqldatabase
                        db.session.add(attribute_label)
                        db.session.commit()
                        db.session.close()
                    #parameter for html page
                    json_file = json_file_int

                elif f_ds.filename.endswith('csv'):
                    #open csv file
                    with open(url+name, 'rt') as csvfile:
                        reader = csv.DictReader(csvfile, delimiter=";")
                        rows = list(reader)
                    #csv file to json file
                    with open(url+name+'.json', 'w') as csvtojsonfile:
                        json.dump(rows, csvtojsonfile, indent=4,separators=(',', ': '))
                    #open json file to manipulate
                    with open(url+name+'.json') as json_data:
                        data = json.load(json_data)

                    json_file_temp = data [0]
                    json_file_int = json_file_temp.keys()
                    for label in json_file_int:
                        data_source_id = db.session.query(DataSource.id).filter(name == DataSource.name).all()
                        id_label_list = [ids[0] for ids in data_source_id]
                        for n in id_label_list:
                            datasource_id_inuse = n
                        attribute_label = Attribute(label, datasource_id_inuse)
                        #Attribute details - save sqldatabase
                        db.session.add(attribute_label)
                        db.session.commit()
                        db.session.close()
                    json_file = json_file_int
                    json_file = json_file_int

                else:
                    json_file = 'Arquivo xml'
                q = db.session.query(DataSource.name, DataSource.created).all()
                return render_template('index_sended.html', json_file=json_file, \
                     items=q)
            else:
                flash('Extension not supported')
                return redirect(request.url)

    q = db.session.query(DataSource.name, DataSource.created).all()

    return render_template('index.html', items=q)

@app.route('/policy/<info>')
@app.route('/policy', defaults={'info':None}, methods=['GET', 'POST'])
def policy(info):
    globalPolicy = False
    if request.method == 'POST':

        if request.form.get("del_list") != None:
            f_del = request.form.get("del_list")
            q_p_del = db.session.query(DataPolicy.id,\
                DataPolicy.name, DataPolicy.url, DataPolicy.datasetname).\
                filter(DataPolicy.name == f_del).all()

            for i,j,k,l in q_p_del:
                q_pr_del = db.session.query(PrivacyRisk.id).\
                    filter(PrivacyRisk.policy_id == i).all()
                for m, in q_pr_del:
                    func_del_att = deleteItems(m)
                if l == 'GlobalPolicy':
                    q_att_gp_del = db.session.query(Attribute.id).\
                        filter(Attribute.data_source_id == 0).all()
                    for o, in q_att_gp_del:
                          func_del_file_att = deleteItemsAtt(o)

                func_del_file = deleteFile(i,j,k)

        if request.files.get("file_policy") != None:
            f_p = request.files['file_policy']
            if request.form.getlist('global_policy') == ['True']:
                globalPolicy = True

            if f_p.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if f_p and allowed_file(f_p.filename):
                filename = secure_filename(f_p.filename)
                name = filename
                url_in_policy = BASE_DIR_INPUT+DIR_POLICIES
                f_p.save(url_in_policy+name)

                #DataPolicy details - save sqldatabase
                if globalPolicy == True:
                    data_source_id = 0
                    selected_dataset = 'GlobalPolicy'
                else:
                    selected_dataset = request.form['datasets_list']
                    q_ds_id_temp = db.session.query(DataSource.id).\
                    filter(DataSource.name == selected_dataset).all()
                    q_ds_id = []
                    for i in q_ds_id_temp:
                        q_ds_id = i
                    data_source_id = q_ds_id[0]

                datapolicydetails = DataPolicy(filename, url_in_policy, \
                    selected_dataset, data_source_id)
                db.session.add(datapolicydetails)
                db.session.commit()
                db.session.close()

                #abrir arquivo
                if f_p.filename.endswith('json'):
                    with open(url_in_policy+name) as json_data:
                        data = json.load(json_data)
                elif f_p.filename.endswith('csv'):
                    #open csv file
                    with open(url_in_policy+name, 'rt') as csvfile:
                        reader = csv.DictReader(csvfile, delimiter=";")
                        rows = list(reader)
                    #csv file to json file
                    with open(url_in_policy+name+'.json', 'w') as csvtojsonfile:
                        json.dump(rows, csvtojsonfile, indent=4,separators=(',', ': '))
                    #open json file to manipulate
                    with open(url_in_policy+name+'.json') as json_data:
                        data = json.load(json_data)

                elif f_p.filename.endswith('xml'):
                    with open(url_in_policy+name) as xmlfile:
                        xmltojson = xmltodict.parse(xmlfile.read())
                        # separa os campos
                        arquivo = xmltojson['AnonymizationOntology']\
                            ['AnonymizationStrategy']['Rules']\
                            ['Rule']
                        xmltojson_file = []
                        for i in arquivo:
                            field_name = i['FieldTable']
                            if i['FieldTableClassification'] == 'KeyAttribute':
                                field_classsification = 'IDENTIFIER'
                            elif i['FieldTableClassification'] == 'QuasiIdentifier':
                                field_classsification = 'QUASI_IDENTIFIER'
                            elif i['FieldTableClassification'] == 'SensitiveAttribute':
                                field_classsification = 'SENSITIVE'
                            elif i['FieldTableClassification'] == 'NonSensitive':
                                field_classsification = 'NON_SENSITIVE'
                            else:
                                field_name = i['FieldTableClassification'].upper()

                            if i['Technique'] == 'Suppression':
                                anonymizationTechnique = 'SUPPRESSION'
                            elif i['Technique'] == 'Generalization':
                                anonymizationTechnique = 'GENERALIZATION'
                            elif i['Technique'] == 'Masking':
                                anonymizationTechnique = 'MASK'
                            elif i['Technique'] == 'Encryption':
                                anonymizationTechnique = 'ENCRYPTION'
                            elif i['Technique'] == 'NoTechnique':
                                anonymizationTechnique = 'NO_TECHNIQUE'
                            else:
                                anonymizationTechnique = i['Technique'].upper()
                            hierarchyDetails = i['Hierarchy']
                            # constroi o dicionario e salva em data
                            xmltojson_file.append({'DataSet':name,'FieldName':field_name,\
                                'PrivacyAttribute':field_classsification,\
                                'AnonymizationTechnique': anonymizationTechnique,\
                                'Details':hierarchyDetails})
                            data = xmltojson_file
                else:
                    flash('File not supported!')

                #PrivacyRisk details - save sqldatabase
                json_policy_file = ''
                for policies in data:
                    json_file_policy_dict = policies
                    json_file_policy_data = data [0]
                    json_file_policy_keys = json_file_policy_data.keys()
                    #captura os campos para chamar o contrutor
                    ds_name = json_file_policy_dict['DataSet']
                    field_name = json_file_policy_dict['FieldName']
                    privacyAttType = json_file_policy_dict['PrivacyAttribute']
                    anonymizationTechnique = json_file_policy_dict['AnonymizationTechnique']
                    hierarchy_temp = json_file_policy_dict['Details']

                    if type(hierarchy_temp)==dict:
                        hierarchy = str(hierarchy_temp).replace('\"', '\\\"')
                    else:
                        hierarchy = hierarchy_temp

                    if globalPolicy == True:
                        actual_id = 0
                        ds_name = 'GlobalPolicy'
                        attribute_pop = Attribute(field_name,actual_id)
                        db.session.add(attribute_pop)
                        db.session.commit()
                        db.session.close()

                        q_data_policy = db.session.query(DataPolicy.id).\
                            filter(DataPolicy.datasetname == ds_name).first()
                        data_policy_id, = q_data_policy

                        q_attr_id = db.session.query(Attribute.id).\
                            filter(Attribute.name == field_name).\
                            filter(Attribute.data_source_id == 0).\
                            all()
                        att_id, = q_attr_id[0]

                        # INSERT na tabela PrivayRisk
                        policy_pop = PrivacyRisk(field_name, privacyAttType, \
                        anonymizationTechnique, hierarchy, att_id, actual_id, \
                        data_policy_id)
                        db.session.add(policy_pop)
                        db.session.commit()
                        db.session.close()
                        json_policy_file = data

                    else:
                        #consulta o datasource id
                        q_datasource_id = db.session.query(DataSource.id, DataSource.name).\
                             filter(DataSource.name == ds_name).all()
                        actual_id,actual_name = q_datasource_id[0]

                        q_attr_id = db.session.query(Attribute.id, Attribute.name,\
                            Attribute.data_source_id).\
                            filter(Attribute.name == field_name and \
                            Attribute.data_source_id == actual_id).\
                            all()

                        for x,y,z in q_attr_id:
                            if actual_id == z:
                                att_id = x

                        q_data_policy = db.session.query(DataPolicy.id).\
                            filter(DataPolicy.datasetname == ds_name).first()

                        data_policy_id, = q_data_policy

                        # INSERT na tabela PrivayRisk
                        policy_pop = PrivacyRisk(field_name, privacyAttType, \
                        anonymizationTechnique, hierarchy, att_id, actual_id, data_policy_id)
                        db.session.add(policy_pop)
                        db.session.commit()
                        db.session.close()
                        json_policy_file = data

                # consultas para mostrar no front
                q_p_list = db.session.query(DataPolicy.name, DataPolicy.datasetname).all()
                q_ds_list  = db.session.query(DataSource.name, DataSource.created).all()
                q = db.session.query(DataPolicy.name, DataPolicy.created, DataPolicy.datasetname).all()

                return render_template('policy_sended.html', \
                    json_policy_file=json_policy_file,\
                      items=q, ds_list=q_ds_list, p_list=q_p_list)

    q_ds_list = db.session.query(DataSource.name, DataSource.created).all()
    q_p_list = db.session.query(DataPolicy.name, DataPolicy.datasetname).all()
    q = db.session.query(DataPolicy.name, DataPolicy.created, DataPolicy.datasetname).all()

    return render_template('policy.html', items=q, ds_list=q_ds_list, p_list=q_p_list)

@app.route('/settings/<info>')
@app.route('/settings', defaults={'info':None}, methods=['GET', 'POST'])
def settings(info):
    q_privacy_separeted = db.session.query(PrivacyRisk.fieldName,\
        PrivacyRisk.anonymizationTechnique, PrivacyRisk.hierarchy,\
        PrivacyRisk.attribute_id, PrivacyRisk.ds_id, PrivacyRisk.policy_id).\
        order_by(func.lower(PrivacyRisk.fieldName))

    # change dataset id to dataset name
    mount_table = []
    for a,b,c,d,ds_id_to_name,f in q_privacy_separeted:
        if ds_id_to_name != 0:
            q_ds_id_to_name = db.session.query(DataSource.name).\
                filter(DataSource.id == ds_id_to_name).all()
            ds_name_final, = q_ds_id_to_name
            e, = ds_name_final
            ds_id_to_name = ds_name_final
            q_p_id_to_name = db.session.query(DataPolicy.name).\
                filter(DataPolicy.id == f).all()
            p_id_to_name, = q_p_id_to_name
            f, = p_id_to_name
            mount_table.append((a,b,c,d,e,f))

        else:
            q_att_all = db.session.query(Attribute.id).\
                filter(func.lower(Attribute.name) == func.lower(a)).\
                filter(Attribute.data_source_id != 0).\
                all()

            if len(q_att_all)>0:
                for i, in q_att_all:
                    q_ds_id_to_name = db.session.query(Attribute.data_source_id).\
                        filter(Attribute.id == i).first()
                    l,=q_ds_id_to_name
                    q_ds_name_f = db.session.query(DataSource.name).\
                        filter(DataSource.id == l).first()
                    ds_name, = q_ds_name_f
                    e = ds_name
                    f = 'GlobalPolicy'
                    mount_table.append((a,b,c,d,e,f))

    gp_list = []
    n_gp_list = []
    duplicates_fl = []
    final_table = []
    for a,b,c,d,e,f in mount_table:
        if f == 'GlobalPolicy':
            gp_list.append((a,b,c,d,e,f))
        else:
            n_gp_list.append((a,b,c,d,e,f))

    for a,b,c,d,e,f in gp_list:
        for i,j,k,l,m,n in n_gp_list:
            if a.lower()==i.lower() and e==m:
                duplicates_fl.append((a,b,c,d,e,f))

    final_table = mount_table
    for a in duplicates_fl:
        for i in mount_table:
            if a == i:
                final_table.remove(a)

    settings_table = final_table

    if request.method == 'POST':
        # recebe o atribute id e o valor para editar
        att_id = request.form.get('edit_att')
        value_update = request.form.get(att_id)

        # Busca Privacy_id, ds_id e attribute_id
        q_to_update = db.session.query(PrivacyRisk.id, \
            PrivacyRisk.ds_id,\
            PrivacyRisk.policy_id).\
            filter(PrivacyRisk.attribute_id == att_id).all()

        q_save_att_name = db.session.query(Attribute.name).\
            filter(Attribute.id == att_id).all()

        db.session.query(Attribute).filter_by(id = att_id).\
            update({'name': value_update })
        db.session.commit()
        db.session.close()

        db.session.query(PrivacyRisk).filter(PrivacyRisk.attribute_id == att_id).\
        update({'fieldName': value_update })
        db.session.commit()
        db.session.close()

        for pr_id,ds_id,p_id in q_to_update:
            if ds_id == 0:
                dsname = 'GlobalPolicy'
            else:
                q_to_get_pname = db.session.query(DataPolicy.name).\
                    filter(DataPolicy.id == p_id).all()
                url_in_policy = BASE_DIR_INPUT+DIR_POLICIES

                for pname, in q_to_get_pname:
                    if pname.endswith('csv'):
                        file_ds_p = url_in_policy+pname+'.json'
                    else:
                        file_ds_p = url_in_policy+pname

                    with open(file_ds_p, 'r') as json_data:
                        policy_dict_temp = json.load(json_data)
                        policy_dict = policy_dict_temp[0].keys()

                    q_get_att_name = db.session.query(Attribute.name).\
                        filter(Attribute.id == att_id).all()

                    url_in_ds = BASE_DIR_INPUT+DIR_DS_FILES
                    for att_name_ant, in q_save_att_name:

                        for p_dict in policy_dict_temp:
                            if p_dict['FieldName'] == att_name_ant:
                                ds_name_update = p_dict['DataSet']
                                for att_name_actual, in q_get_att_name:
                                    p_dict['FieldName'] = att_name_actual

                                    if ds_name_update.endswith('csv'):

                                        with open(url_in_ds+ds_name_update+'.json', 'r+') as json_ds:
                                            ds_dict_temp = json.load(json_ds)
                                            ds_dict = ds_dict_temp[0].keys()

                                        for ds_dict_value in ds_dict_temp:
                                            ds_dict_value[att_name_actual]=ds_dict_value.pop(att_name_ant)

                                        with open(url_in_ds+ds_name_update+'.json', 'w+') as json_ds:
                                            json.dump(ds_dict_temp, json_ds, indent=4,separators=(',', ': '))

                                    else:
                                        with open(url_in_ds+ds_name_update, 'r+') as json_ds:
                                            ds_dict_temp = json.load(json_ds)
                                            ds_dict = ds_dict_temp[0].keys()

                                        for ds_dict_value in ds_dict_temp:
                                            ds_dict_value[att_name_actual]=ds_dict_value.pop(att_name_ant)

                                        with open(url_in_ds+ds_name_update, 'w+') as json_ds:
                                            json.dump(ds_dict_temp, json_ds, indent=4,separators=(',', ': '))

                    with open(file_ds_p, 'w+') as json_data:
                        json.dump(policy_dict_temp, json_data, indent=4,separators=(',', ': '))

        return redirect(url_for('settings'))
    return render_template('settings.html', settings_table=settings_table)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/privacy_or/<info>')
@app.route('/privacy_or', defaults={'info':None}, methods=['GET', 'POST'])
def privacy_or(info):

    url_out_policy = BASE_DIR_OUTPUT+DIR_POLICIES
    url_in_policy = BASE_DIR_INPUT+DIR_POLICIES
    url_out_ds = BASE_DIR_OUTPUT+DIR_DS_FILES
    url_in_ds = BASE_DIR_INPUT+DIR_DS_FILES
    policy = []
    data_post_list = []
    coll_name = []
    q_tb_privacy_risk = []
    temp_list = []
    final_list_or = []

    q_tb_privacy_risk = db.session.query(\
        PrivacyRisk.ds_id,\
        PrivacyRisk.fieldName,\
        PrivacyRisk.privacyAttType,\
        PrivacyRisk.anonymizationTechnique,\
        PrivacyRisk.hierarchy).\
        filter(Attribute.id == PrivacyRisk.attribute_id).\
        filter(PrivacyRisk.ds_id != 0).\
        filter(PrivacyRisk.anonymizationTechnique != 'NO_TECHNIQUE').\
        all()

    q_attribute_table_wogp = db.session.query(\
        Attribute.id, Attribute.name, Attribute.data_source_id).\
        filter(Attribute.data_source_id != 0).\
        all()

    q_attribute_gp = db.session.query(\
        Attribute.id, Attribute.name, Attribute.data_source_id).\
        filter(Attribute.data_source_id == 0).\
        all()

    for l,m,n in q_attribute_gp:
        for att_id,att_name,att_ds_id in q_attribute_table_wogp:
            if m.lower()==att_name.lower():
                q_datapolicy = db.session.query(PrivacyRisk.id).\
                    filter(PrivacyRisk.attribute_id == att_id).\
                    all()
                if len(q_datapolicy) == 0:
                    q_privacyrisk = db.session.query(\
                        PrivacyRisk.privacyAttType,\
                        PrivacyRisk.anonymizationTechnique,\
                        PrivacyRisk.hierarchy).\
                        filter(func.lower(PrivacyRisk.fieldName) == func.lower(att_name)).\
                        filter(PrivacyRisk.ds_id == 0).\
                        all()

                    for pr_pa,pr_at,pr_hi in q_privacyrisk:
                        temp_list.append((att_ds_id,att_name,pr_pa,\
                            pr_at,pr_hi))

    final_list_or = q_tb_privacy_risk + temp_list

    for values in final_list_or:
        param_list = ["DataSet", "FieldName","PrivacyAttribute",\
            "AnonymizationTechnique", "Details"]
        value_list = values
        object_anonym = dict (zip(param_list, value_list))
        dataset_id = object_anonym['DataSet']
        q_id_to_name_ds = db.session.query(DataSource.name).\
            filter(DataSource.id == dataset_id).all()
        for i, in q_id_to_name_ds:
            id_to_name_ds = i
        if dataset_id == 0:
            object_anonym['DataSet'] = 'GlobalPolicy'
        else:
            object_anonym['DataSet'] = id_to_name_ds
        policy.append(object_anonym)

    with open(url_out_policy+'policy_or.json', 'w+') as jsonfile:
        json.dump(policy, jsonfile, indent=4,separators=(',', ': '))

    if request.method == 'POST':
        name = 'policy_or.json'
        #or e and
        ds_list = []
        attribute_list = []
        dataset_fildname_anonymtech = []

        with open(url_out_policy+name, 'rt') as json_data:
            policy_data = json.load(json_data)
        faker_ctx = {}
        dsname_list = []
        dsname_list_uniques = []
        ds_fn_at_dt_list = []
        for policy_dict in policy_data:
            dataset_name = policy_dict['DataSet']
            field_name = policy_dict['FieldName']
            anonym_tech = policy_dict['AnonymizationTechnique']
            details = policy_dict['Details']
            dsname_list.append(dataset_name)
            ds_fn_at_dt_list.append((dataset_name,field_name,anonym_tech,details))

        dsname_list_uniques = list(set(dsname_list))

        for dsname in dsname_list_uniques:
            if dsname != 'GlobalPolicy':
                if dsname.endswith('csv'):
                    with open(url_in_ds+dsname+'.json', 'r+') as json_data:
                        dataset_value = json.load(json_data)

                if dsname.endswith('json'):
                    with open (url_in_ds+dsname, 'r+') as json_data:
                        dataset_value = json.load(json_data)

                coll_name = []

                for ds,fn,at,dt in ds_fn_at_dt_list:
                    if ds.lower() == dsname.lower():
                        if dsname.endswith('csv'):
                            dsname_final = dsname+'.json'
                        else:
                            dsname_final = dsname

                        data_post = []

                        for line in dataset_value:
                            data_post.append(decisionFunction(dsname_final,fn,at,dt,line))

                        # if dsname.endswith('json'):
                        keys = data_post[0].keys()
                        if dsname_final.endswith('csv.json'):
                            with open(url_out_ds+dsname[:-4]+'_anonymized.csv', 'w+') as output_file:
                                dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
                                dict_writer.writeheader()
                                dict_writer.writerows(data_post)
                            with open (url_out_ds+dsname[:-4]+'_anonymized.json', 'w+') as json_data:
                                    json.dump(data_post, json_data, indent=4,separators=(',', ': '))
                        else:
                            with open(url_out_ds+dsname[:-5]+'_anonymized.csv', 'w+') as output_file:
                                dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
                                dict_writer.writeheader()
                                dict_writer.writerows(data_post)
                            with open (url_out_ds+dsname[:-5]+'_anonymized.json', 'w+') as json_data:
                                    json.dump(data_post, json_data, indent=4,separators=(',', ': '))
                    coll_name.append(fn)
                data_post_list.append((data_post,dsname))
    # import pdb; pdb.set_trace()

    return render_template('privacy_or.html', \
                final_OR=policy, code=data_post_list, coll_name=coll_name)

@app.route('/privacy_and/<info>')
@app.route('/privacy_and', defaults={'info':None}, methods=['GET', 'POST'])
def privacy_and(info):
    policy = []
    url_out_policy = BASE_DIR_OUTPUT+DIR_POLICIES
    url_in_policy = BASE_DIR_INPUT+DIR_POLICIES
    url_out_ds = BASE_DIR_OUTPUT+DIR_DS_FILES
    url_in_ds = BASE_DIR_INPUT+DIR_DS_FILES

    policy = []
    data_post_list = []
    coll_name = []
    fn_at_hi_final = []
    final_list = []
    temp_list = []

    #atual
    q_and_att_pr = db.session.query(func.lower(Attribute.name), \
        func.count(Attribute.name)).\
        group_by(func.lower(Attribute.name)).\
        having(func.count(Attribute.name)>1).\
        filter(PrivacyRisk.attribute_id == Attribute.id).all()

    num_of_ds = db.session.query(DataSource).count()
    num_of_p = db.session.query(DataPolicy).count()
    global_yes = db.session.query(DataPolicy).\
        filter(DataPolicy.datasetname == 'GlobalPolicy').count()

    and_list = []
    q_name_tech_hierarc = []

    for x,y in q_and_att_pr:
        if global_yes !=0:
            if y >= num_of_ds+global_yes:
                and_list.append(x)
        else:
            if y >= num_of_ds:
                and_list.append(x)

    for label in and_list:
        q_name_tech_hierarc = db.session.query(\
            PrivacyRisk.ds_id,\
            PrivacyRisk.fieldName,\
            PrivacyRisk.privacyAttType,\
            PrivacyRisk.anonymizationTechnique,\
            PrivacyRisk.hierarchy).\
            distinct(PrivacyRisk.fieldName).\
            filter(PrivacyRisk.anonymizationTechnique != 'NO_TECHNIQUE').\
            filter(func.lower(PrivacyRisk.fieldName) == func.lower(label)).\
            filter(PrivacyRisk.ds_id != 0).\
            all()

        for ds,fn,pa,at,hi in q_name_tech_hierarc:
            fn_at_hi_final.append((ds,fn,pa,at,hi))

    q_global_fn_at_h = db.session.query(\
        PrivacyRisk.ds_id,\
        PrivacyRisk.fieldName,\
        PrivacyRisk.privacyAttType,\
        PrivacyRisk.anonymizationTechnique,\
        PrivacyRisk.hierarchy).\
        filter(PrivacyRisk.ds_id == 0).\
        all()

    for ds_id,fn,pa,at,hi in q_global_fn_at_h:
        q_attribute_fn = db.session.query(Attribute.id, \
            Attribute.name, Attribute.data_source_id).\
            filter(func.lower(Attribute.name) == func.lower(fn)).\
            filter(Attribute.data_source_id != 0).\
            all()

        if len (q_attribute_fn) == num_of_ds:
            for att_id,att_name,att_dsid in q_attribute_fn:
                q_dsname = db.session.query(DataSource.id).\
                    filter(DataSource.id == att_dsid).\
                    all()
                dsname, = q_dsname
                dsn, = dsname
                datasetid_t = att_dsid
                fieldname_t = att_name
                anonymtech_t = at
                privacyatt_t = pa
                hierarchy_t = hi
                temp_list.append((datasetid_t,fieldname_t, privacyatt_t,\
                    anonymtech_t,hierarchy_t))

    if global_yes==0 and num_of_ds == num_of_p:
        final_list = fn_at_hi_final+temp_list

    elif global_yes==1 and num_of_p < num_of_ds:
        final_list = fn_at_hi_final+temp_list

    elif global_yes==1 and num_of_ds == 1:
        pass

    else:
        final_list = temp_list

    for values in final_list:
        ds,_,_,_,_ = values

        if ds != 0:
            param_list = ["DataSet", "FieldName","PrivacyAttribute",\
                "AnonymizationTechnique", "Details"]
            value_list = values
            object_anonym = dict (zip(param_list, value_list))
            dataset_id = object_anonym['DataSet']
            q_id_to_name_ds = db.session.query(DataSource.name).\
                filter(DataSource.id == dataset_id).all()
            for i, in q_id_to_name_ds:
                id_to_name_ds = i
                object_anonym['DataSet'] = id_to_name_ds
            policy.append(object_anonym)
    name_tech_hierarchy_list = []
    name_list = []
    dict_name_tech = {}
    for name_tech_hierarchy in policy:
        name_tech_hierarchy_list.append((\
        name_tech_hierarchy['FieldName'],\
        name_tech_hierarchy['AnonymizationTechnique'],\
        name_tech_hierarchy['Details']))

    for name,tech,hierarchy in name_tech_hierarchy_list:
        name_list.append(name)

    for n in name_list:
        tech_hierarchy_list = []
        for name,tech,hierarchy in name_tech_hierarchy_list:
            if name.lower() == n.lower():
                tech_hierarchy_list.append((tech,hierarchy))
                dict_name_tech[name]=tech_hierarchy_list

        for m in dict_name_tech.keys():
            tech_hierarchy_list = dict_name_tech[m]
            final_tech,final_hierarchy = orderTech(tech_hierarchy_list)
            for p in policy:
                if p['FieldName'] == m:
                    p['AnonymizationTechnique'] = final_tech
                    p['Details'] = final_hierarchy
    # privacy technique priority hierarchy
    with open(url_out_policy+'policy_and.json', 'w+') as jsonfile:
            json.dump(policy, jsonfile, indent=4,separators=(',', ': '))
###### gerate anonymization ######
    codegen = []
    code = []
    data_post = []
    data_post_list = []
    coll_name = []
    if request.method == 'POST':
        name = 'policy_and.json'
        #or e and
        ds_list = []
        attribute_list = []
        dataset_fildname_anonymtech = []

        with open(url_out_policy+name, 'rt') as json_data:
            policy_data = json.load(json_data)
        faker_ctx = {}
        dsname_list = []
        dsname_list_uniques = []
        ds_fn_at_dt_list = []
        for policy_dict in policy_data:
            dataset_name = policy_dict['DataSet']
            field_name = policy_dict['FieldName']
            anonym_tech = policy_dict['AnonymizationTechnique']
            details = policy_dict['Details']
            dsname_list.append(dataset_name)
            ds_fn_at_dt_list.append((dataset_name,field_name,anonym_tech,details))

        dsname_list_uniques = list(set(dsname_list))

        for dsname in dsname_list_uniques:
            if dsname != 'GlobalPolicy':
                if dsname.endswith('csv'):
                    with open(url_in_ds+dsname+'.json', 'r+') as json_data:
                        dataset_value = json.load(json_data)

                if dsname.endswith('json'):
                    with open (url_in_ds+dsname, 'r+') as json_data:
                        dataset_value = json.load(json_data)

                coll_name = []

                for ds,fn,at,dt in ds_fn_at_dt_list:
                    if ds.lower() == dsname.lower():
                        if dsname.endswith('csv'):
                            dsname_final = dsname+'.json'
                        else:
                            dsname_final = dsname

                        data_post = []

                        for line in dataset_value:
                            data_post.append(decisionFunction(dsname_final,fn,at,dt,line))

                        # if dsname.endswith('json'):
                        keys = data_post[0].keys()
                        if dsname_final.endswith('csv.json'):
                            with open(url_out_ds+dsname[:-4]+'_anonymized.csv', 'w+') as output_file:
                                dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
                                dict_writer.writeheader()
                                dict_writer.writerows(data_post)
                            with open (url_out_ds+dsname[:-4]+'_anonymized.json', 'w+') as json_data:
                                    json.dump(data_post, json_data, indent=4,separators=(',', ': '))
                        else:
                            with open(url_out_ds+dsname[:-5]+'_anonymized.csv', 'w+') as output_file:
                                dict_writer = csv.DictWriter(output_file, keys, delimiter=';')
                                dict_writer.writeheader()
                                dict_writer.writerows(data_post)
                            with open (url_out_ds+dsname[:-5]+'_anonymized.json', 'w+') as json_data:
                                    json.dump(data_post, json_data, indent=4,separators=(',', ': '))
                    coll_name.append(fn)
                data_post_list.append((data_post,dsname))
    # import pdb; pdb.set_trace()

    return render_template('privacy_and.html', \
                final_AND=policy, code=data_post_list, coll_name=coll_name)

@app.route('/privaaas/<path:req_path>')
@app.route('/privaaas', defaults={'req_path': ''}, methods=['GET', 'POST'])
def privaaas(req_path):
    url_out_ds = BASE_DIR_OUTPUT+DIR_DS_FILES
    # Joining the base and the requested path
    abs_path = os.path.join(url_out_ds, req_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)
    files = os.listdir(abs_path)

    if request.method == 'POST':
        try:
            filename_output = request.form['del_list']
            os.remove(os.path.join(url_out_ds, filename_output))
            return redirect(url_for('privaaas'))
        except:
            flash ('Don\'t file selected')

    return render_template('privaaas.html', files_sended=files)

@app.route('/risk/<path:req_path>')
@app.route('/risk', defaults={'req_path': ''}, methods=['GET', 'POST'])
def risk(req_path):
    url_out_ds = BASE_DIR_OUTPUT+DIR_DS_FILES
    url_out_hrisk = BASE_DIR_OUTPUT+DIR_HRISK_FILES
    url_in_hrisk = BASE_DIR_INPUT+DIR_HRISK_FILES
    # Joining the base and the requested path
    abs_path = os.path.join(url_out_ds, req_path)
    abs_path_hi = os.path.join(url_in_hrisk, req_path)
    abs_path_ge = os.path.join(url_out_hrisk, req_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)
    files = os.listdir(abs_path)
    files_hrisk = os.listdir(abs_path_hi)
    files_genereted = os.listdir(abs_path_ge)
    post_view = None
    if request.method == 'POST':
        if request.form.get('del_list') != None:
            try:
                filename_output = request.form['del_list']
                os.remove(os.path.join(url_out_hrisk, filename_output))
                folder = url_in_hrisk
                for the_file in os.listdir(folder):
                    file_path = os.path.join(folder, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(e)
                return redirect(url_for('risk'))
            except:
                flash ('Don\'t file selected')

        if request.files.get("file_hrisk") != None:
            hold_click = request.files.get("file_hrisk")
            try:
                hi_filename = request.files['file_hrisk']
                ds_filename = request.form['select_anonymized_dataset']
                if hi_filename and allowed_file(hi_filename.filename):
                    filename_hi_filename = secure_filename(hi_filename.filename)
                    hi_filename.save(url_in_hrisk+filename_hi_filename)

                p1 = subprocess.Popen(['java', '-jar', 'arx-poc/run/arx-poc.jar',\
                    url_out_ds+ds_filename, url_in_hrisk+filename_hi_filename,\
                    url_out_hrisk+ds_filename[:-4]+'_risk.csv'], stdout=subprocess.PIPE)
                p2 = p1.stdout.read()
                p3 = p2.decode("utf-8")
                post_view = p3.splitlines()
                files_genereted = os.listdir(abs_path_ge)

                return redirect(url_for('risk'), files_sended=files, files_genereted=files_genereted, files_hrisk=files_hrisk, post_view=post_view)
            except:
                flash ('Don\'t file selected')

    return render_template('risk.html', files_sended=files, files_genereted=files_genereted, files_hrisk=files_hrisk, post_view=post_view)
