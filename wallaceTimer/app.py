from dataclasses import dataclass
from datetime import datetime
import logging
from flask import Flask
from flask_migrate import Migrate, current, migrate
#from ftplib import FTP
import ftplib

from sqlalchemy.orm import query
from models import Company, db,External_export_query_list as EQUL,External_export_query_timer as EPQT,External_export_query_params as EQP,External_export_query_timer as EEQT, Sendingmail as SM,Ftpserverdetails,HistoryDetails
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv,pandas as pd,os
import schedule,time
from logging import FileHandler,WARNING,ERROR

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/timer'
app.config['SQLALCHEMY_TRACK_MODIFICATION']= False

db.init_app(app)

migrate  = Migrate(app, db)

app.app_context().push()
# instance is created
#scheduler = sched.scheduler(time.time,time.sleep)


app.debug = True
#if not app.debug:
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)
file_handler.setLevel(ERROR)

app.logger.addHandler(file_handler)

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
 

# @app.route('/')
# def readTimerQuery():
#      query_data = EPQT.query.filter(EPQT.timer_status=='Active').all()
#      for data in query_data:
#         print(data.timer_time)
#         e2 = scheduler.enter(2, 1,readQueryList)
  
#         # removing 1st event from 
#         # the event queue
#         scheduler.cancel(e2)
  
#         # executing the events
#         scheduler.run()
     
#      return 'success'   

company_id  = ''
division_id = ''
timer = ''
filename =''
filesenttime = ''
ftpdetails = ''
type_query = ''


@app.route('/')
def readQueryList(data):
    print("Reached")
    print(data)
    global company_id 
    global division_id
    global timer
    global type_query
    # company_id = data['company_id']
    # division_id = data['division_id']
    querylist_id = data['query_list_id']
    timer = data['timer']
    print(company_id, division_id)
    #header = ['Company_id','Company_name','Company_description']
    result_data  = EQUL.query.filter(EQUL.query_status=='Active').filter(EQUL.query_list_id==querylist_id).order_by(EQUL.query_list_id).all()
    print(result_data)
    if result_data:
        print(result_data[0].query_type)
        for res_data in result_data:
            type_query = res_data.query_type
            company_id = res_data.query_company_id
            division_id = res_data.query_division_id
            if res_data.query_type == 'SP':
                print(res_data.query_list_id)
                params_results = EQP.query.filter_by(query_list_id_fk=res_data.query_list_id).filter_by(param_status='Active').order_by(EQP.param_position).all()
                print('params result ',params_results)
                format_data = ''
                for params in params_results:
                    param_type     = params.param_type
                    param_name     = params.param_name
                    param_position = params.param_position

                    param_name = '1'

                    format_data += param_name+','
                try:    
                    sp_query = res_data.sp_name+"({})".format(format_data.strip(','))
                    print('Tested',sp_query)    
                    # return 'success'
                    header_data = db.engine.execute(sp_query).keys()
                    header = [row for row in header_data]
                    print('Header', header)
                    query_data = db.engine.execute(sp_query)
                    csv_data = [row for row in query_data]
                    print('CSV ',csv_data)
                    result = exportCSV(header,csv_data)

                except Exception as e:
                    logging.error('Error'+str(e))    
            else:
                try:
                    header_data = db.engine.execute(res_data.sp_name).keys()
                    header = [row for row in header_data]
                    print('Header', header)
                    query_data = db.engine.execute(res_data.sp_name)
                    csv_data = [row for row in query_data]
                    print('CSV ',csv_data)
                    result = exportCSV(header,csv_data)
                except:
                    logging.error('Error'+str(e))

        return result
    else:
        logging.error('Read Query function: No data found')
        return 'No data found'    


def exportCSV(header, csv_data):
    if header and csv_data:
        current_time = datetime.now()
        extension = ".csv"
        path='csv'
        filename='data'+str(current_time)+extension
        filepath=os.path.join(path,filename)
        file = open(filepath, 'w', newline='')
        write = csv.writer(file)
        write.writerow(header)
        write.writerows(csv_data)
        print('filename ',filename)
        result=ftpConnection(filepath,filename)
        return result
    else:
        logging.error('CSV No data found')
        return 'CSV No data found'    

def ftpConnection(fpath,fname):
    global filesenttime
    global filename
    global ftpdetails
    filename = fname
    filepath = fpath
    print(datetime.now())
    #print(filename)
    print('ftp_connection ',company_id,division_id)
    ftp_details    = Ftpserverdetails.query.filter_by(server_divisionid=division_id).filter_by(server_status='Active').all()
    print('ftp_details ',ftp_details)
    if ftp_details:
        for ftp_res in ftp_details:
            ftp_host   = ftp_res.server_host
            ftp_name   = ftp_res.server_name
            ftp_pwd    = ftp_res.server_password
            ftp_folder = ftp_res.server_folderpath 
            ftpdetails = ftp_host+"::"+ftp_name+"::"+ftp_pwd+"::"+ftp_folder

        try:
            # ftp = FTP()
            # ftp.set_debuglevel(2)
            # ftp.connect(ftp_host)
            # ftp.login(ftp_name,ftp_pwd)
            # ftp.encoding = "utf-8"
            ftp_server=ftplib.FTP()
            ftp_server.connect(ftp_host)
            ftp_server.login(ftp_name,ftp_pwd)
            ftp_server.encoding="utf-8"
            ftp_server.set_debuglevel(2)
            with open(filepath, "rb") as file:
                ftp_server.storbinary(f"STOR Wallace_Test/ {filename}",file)
            ftp_server.close()
            filesenttime = datetime.now()
            

        except Exception as e:
            logging.error("failure at FTP Connection "+str(e) )
            return "failure"+str(e) 

        result = sendingMaildata()
        return result       
    else:
        logging.error('FTP Server No data Found')
        return 'FTP Server No data Found'    
    


def sendingMaildata():
    print('sendingMail ',company_id,division_id)
    send_result = SM.query.filter_by(send_cmpy_divid=division_id).filter_by(send_emailstatus='Active').all()
    print(send_result)
    to = ''
    cc = ''
    if send_result:
        for send_res in send_result:
            if send_res.send_email_tocc.lower()=='to':
                to += send_res.send_emailid+','
            else:
                cc += send_res.send_emailid+',' 
        
        try:
            to_email = to.strip(',')
            cc_email = cc.strip(',')
            message = 'Hi, Files successfully moved to your server'
            s = smtplib.SMTP(host='smtp.office365.com',port=587)
            s.starttls()
            s.login('esakkiraja@swaas.net','$waas@1050')
            msg = MIMEMultipart()
            msg['from'] = 'esakkiraja@swaas.net'
            msg['to']   = to_email
            msg['cc']   = cc_email
            msg['subject'] = 'FIle Transfer'
            msg.attach(MIMEText(message,'plain'))
            s.send_message(msg)
            insert_data = HistoryDetails(history_cmpyid=company_id,history_divid=division_id,history_scheduler_time=timer,history_filename=filename,history_filesenttime=filesenttime,history_ftpdetails=ftpdetails,history_to_emailid=to_email,history_cc_emailid=cc_email,history_querytype=type_query)
            db.session.add(insert_data)
            db.session.commit()    
            s.quit()
             
            return 'success'
        except Exception as e:
            logging.error('Failure sending mail '+str(e)  )
            return 'Failure'+str(e)          
    else:
        logging.error('Send email No data Found')
        return 'Send email No data Found'  
    


timer_result = EEQT.query.filter_by(timer_status='Active').all()
if timer_result:
    for t_res in timer_result:
        data = {
            'query_list_id' : t_res.query_list_id_fk,
            'timer'       : t_res.timer_time
        }
        schedule.every().day.at(t_res.timer_time).do(readQueryList,data)
        #schedule.every().day.at('10:27').do(readQueryList,data)
        #schedule.every(t_res.timer_time).minutes.do(readQueryList)
        #schedule.every(1).minutes.do(readQueryList)
        #schedule.every().day.at("10:26").do(readQueryList)
    while True:
  
        # Checks whether a scheduled task 
        # is pending to run or not
        print(schedule.next_run())
        schedule.run_pending()
        time.sleep(1)
    #print('success')    
else:
    logging.error('Timer table No data Found')
    print('No result found')        



if __name__=="__main__":
    
    app.run(host='localhost',port='5002')

