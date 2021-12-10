from dataclasses import dataclass
from datetime import datetime
from flask import Flask
from flask_migrate import Migrate, current, migrate
from ftplib import FTP

from sqlalchemy.orm import query
from models import db,External_export_query_list as EQUL,External_export_query_timer as EPQT
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv,pandas as pd,os
import schedule,time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/timer'
app.config['SQLALCHEMY_TRACK_MODIFICATION']= False

db.init_app(app)

migrate  = Migrate(app, db)

app.app_context().push()
# instance is created
#scheduler = sched.scheduler(time.time,time.sleep)


app.debug = True


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
@app.route('/')
def readQueryList():
    print("Reached")
    
    #header = ['Company_id','Company_name','Company_description']
    result_data  = EQUL.query.filter(EQUL.query_status=='Active').all()
    if result_data:
        for res_data in result_data:
            #if res_data.query_type != 'Query':
                header_data = db.engine.execute(res_data.sp_name).keys()
                header = [row for row in header_data]
                query_data = db.engine.execute(res_data.sp_name)
                # #print(query_data)
                # for res in query_data:
                #     print('Tested data',res[0])
                csv_data = [row for row in query_data]
                print('CSV ',csv_data)
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
            # else:
            #     pass
        return result
    else:
        return 'No data found'    

def ftpConnection(fpath,fname):
    filename = fname
    filepath = fpath
    print(datetime.now())
    #print(filename)
    try:
        ftp = FTP()
        ftp.set_debuglevel(2)
        ftp.connect('66.147.244.154')
        ftp.login('sampleftp@swaas.net','Sw@@S@Ftp@123')
        ftp.encoding = "utf-8"
        with open(filepath, "rb") as file:
            ftp.storbinary(f"STOR Wallace_Test/ {filename}",file)
        ftp.quit()
        result =sendingMail()
        return result

    except Exception as e:
        return "failure"+str(e)


def sendingMail():
    try:
        to_email = 'esakkiraja@swaas.net'
        message = 'Hi, Files successfully moved to your server'
        s = smtplib.SMTP(host='smtp.office365.com',port=587)
        s.starttls()
        s.login('esakkiraja@swaas.net','$waas@1132#')
        msg = MIMEMultipart()
        msg['from'] = 'esakkiraja@swaas.net'
        msg['to']   = to_email
        msg['subject'] = 'FIle Transfer'
        msg.attach(MIMEText(message,'plain'))
        s.send_message(msg)
        s.quit()

        return 'success'
    except Exception as e:
        return 'Failure'+str(e)

schedule.every(5).minutes.do(readQueryList)
#schedule.every().day.at("10:26").do(readQueryList)
while True:
  
    # Checks whether a scheduled task 
    # is pending to run or not
        schedule.run_pending()
        time.sleep(1)


if __name__=="__main__":
    app.run(host='localhost',port='5003')

