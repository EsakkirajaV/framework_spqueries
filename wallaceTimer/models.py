from logging import NullHandler
from flask_migrate import history
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import backref,relationship

db = SQLAlchemy()

class Status(Enum):
    Active = 'A'
    Inactive = 'I'

class Timer(Enum):
    Daily = 'D'
    Weekly = 'W'    

class QueryType(Enum):
    SP = 'SP',
    Query = 'Query'    

@dataclass
class Company(db.Model):
    __tablename__ = 'company'

    company_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(50))
    company_description = db.Column(db.Text)
    company_status = db.Column(db.Enum(Status, default=Status.Active))

    def __repr__(self):
        return "{} {} {} {}".format(self.company_id,self.company_name,self.company_description,self.company_status)

@dataclass
class CMPYDevision(db.Model):
    __tablename__ = 'company_division'

    cmpy_divsionid = db.Column(db.Integer,primary_key=True, autoincrement=True)
    cmpy_divsionname = db.Column(db.String)
    cmpy_divisionemail = db.Column(db.String)
    cmpy_companyid = db.Column(db.Integer,db.ForeignKey('company.company_id'))
    cmpy_divsionstatus = db.Column(db.Enum(Status, default=Status.Active))

    def __repr__(self):
        return "{} {} {} {} {}".format(self.cmpy_divsionid,self.cmpy_divsionname,self.cmpy_divisionemail,self.cmpy_companyid,self.cmpy_divsionstatus)

@dataclass
class External_export_query_list(db.Model):
    __tablename__ = 'external_export_query_list'

    query_list_id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    query_company_id = db.Column(db.Integer)
    query_division_id = db.Column(db.Integer,db.ForeignKey('company_division.cmpy_divsionid'))
    query_type = db.Column(db.String)
    sp_name = db.Column(db.Text)
    query_status = db.Column(db.Enum(Status, default=Status.Active))
    query_createdby = db.Column(db.String)
    query_createdat = db.Column(db.DateTime)
    query_updatedby = db.Column(db.String)
    query_updatedat = db.Column(db.DateTime)   

    company_division_querylist  = relationship('CMPYDevision', backref = backref('external_export_query_timer'))

    def __repr__(self):
        return "{} {} {} {} {} {}".format(self.query_list_id,self.query_company_id,self.query_division_id,self.query_type,self.sp_name,self.query_status)


@dataclass
class External_export_query_params(db.Model):

    query_param_list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    query_list_id_fk = db.Column(db.Integer, db.ForeignKey('external_export_query_list.query_list_id'))
    param_type = db.Column(db.String)
    param_name = db.Column(db.String)
    param_position = db.Column(db.String)   
    param_status = db.Column(db.Enum(Status, default=Status.Active))
    param_createdby = db.Column(db.String)
    param_createdat = db.Column(db.DateTime)
    param_updatedby = db.Column(db.String)
    param_updatedat = db.Column(db.DateTime)       

    external_export_query_list  = relationship('External_export_query_list',uselist=False, backref = backref('external_export_query_params'))

    def __repr__(self):
        return "{} {} {} {}".format(self.query_param_list_id,self.query_list_id_fk,self.param_type,self.param_name,self.param_position,self.param_status)

@dataclass
class External_export_query_timer(db.Model):
    __tablename__ = 'external_export_query_timer'

    query_timer_id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    timer_company_id = db.Column(db.Integer,nullable=False)
    timer_division_id = db.Column(db.Integer,nullable=False)
    query_list_id_fk = db.Column(db.Integer, db.ForeignKey('external_export_query_list.query_list_id'))
    timer_company_url = db.Column(db.Text,nullable=False)
    timer_type = db.Column(db.Enum(Timer,default=Timer.Daily))
    timer_time = db.Column(db.String, nullable=False)
    timer_status = db.Column(db.Enum(Status,default=Status.Active))
    timer_createdby = db.Column(db.String)
    timer_createdat = db.Column(db.DateTime)
    timer_updatedby = db.Column(db.String)
    timer_updatedat = db.Column(db.DateTime)

    #external_export_query_list  = relationship('External_export_query_list',uselist=False,backref = backref('external_export_query_timer'))

    def __repr__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.query_timer_id,self.timer_company_id,self.timer_division_id,self.timer_company_url,self.timer_type,self.timer_status,self.timer_time,self.query_list_id_fk)

@dataclass
class Sendingmail(db.Model):
    __tablename__ = "sendingmail"

    send_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    send_cmpy_divid = db.Column(db.Integer, db.ForeignKey('company_division.cmpy_divsionid'))  
    send_email_tocc = db.Column(db.String, nullable=False)
    send_emailid = db.Column(db.String, nullable=False)
    send_emailstatus = db.Column(db.Enum(Status,default=Status.Active))

    company_division = relationship('CMPYDevision', backref=backref('sendingmail'))
          

    def __repr__(self):
       return '{} {} {} {} {}'.format(self.send_id,self.send_cmpy_divid,self.send_email_tocc,self.send_emailid,self.send_emailstatus)  


@dataclass
class Ftpserverdetails(db.Model):
    __tablename__ = 'ftpserverdetails'

    sever_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    server_divisionid = db.Column(db.Integer, db.ForeignKey('company_division.cmpy_divsionid'))
    server_host = db.Column(db.String,nullable=False)
    server_name = db.Column(db.String,nullable=False)
    server_password = db.Column(db.String,nullable=False)
    server_folderpath = db.Column(db.String,nullable=False)
    server_status = db.Column(db.Enum(Status, default=Status.Active))

    company_division = relationship('CMPYDevision', backref=backref('ftpserverdetails'))

    def __repr__(self):
        return "{} {} {} {} {} {} {}".format(self.sever_id,self.server_divisionid,self.server_host,self.server_name,self.server_password,self.server_folderpath,self.server_status)


@dataclass
class HistoryDetails(db.Model):
    __tablename__ = 'historydetails'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    history_cmpyid = db.Column(db.Integer, nullable=False)
    history_divid = db.Column(db.Integer, nullable=False)
    history_scheduler_time = db.Column(db.String, nullable=False)
    history_filename = db.Column(db.String, nullable=False)
    history_filesenttime = db.Column(db.String, nullable=False)
    history_ftpdetails = db.Column(db.Text, nullable=False)
    history_to_emailid = db.Column(db.Text, nullable=False)
    history_cc_emailid = db.Column(db.Text, nullable=False)
    history_querytype  = db.Column(db.String, nullable=False)

    def __repr__(self):
        return "{} {} {} {} {} {} {} {} {}".format(self.history_id,self.history_cmpyid,self.history_divid,self.history_scheduler_time,self.history_filename,self.history_filesenttime,self.history_ftpdetails,self.history_to_emailid,self.history_cc_emailid)
