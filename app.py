from dataclasses import dataclass
from datetime import datetime
import logging
from flask import Flask,redirect,url_for,request,render_template
from flask_migrate import Migrate, current, migrate
#from ftplib import FTP
import ftplib
from threading import Timer
from flask import *
from sqlalchemy.orm import query
from models import Company, db,External_export_query_list as EQUL,External_export_query_timer as EPQT,External_export_query_params as EQP,External_export_query_timer as EEQT, Sendingmail as SM,Ftpserverdetails,HistoryDetails
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import csv,pandas as pd,os,logging
import schedule,time,threading,itertools
from logging import FileHandler,WARNING,ERROR
from forms import ScheduleForm, EmailForm, ServerForm

# app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/timer'
# app.config['SQLALCHEMY_TRACK_MODIFICATION']= False

# db.init_app(app)
def create_app():
    appnew = Flask(__name__)
    appnew.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost/timer'
    appnew.config['SQLALCHEMY_TRACK_MODIFICATION']= False
    appnew.config['SECRET_KEY'] = "SECRETKEY"
    db.init_app(appnew)
    db.app = appnew
    return appnew

app = create_app()

migrate  = Migrate(app, db)

app.app_context().push()
# instance is created
#scheduler = sched.scheduler(time.time,time.sleep)


app.debug = False
#app.logger.setLevel(logging.DEBUG)
if not app.debug:
    logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


 
@app.route('/insertdata', methods=['GET','POST'])
def insertData():
    print("Reached")
    global timer,query_list,query_params
    form=ScheduleForm()
    
    print("Method",request.method)
    if request.method == 'POST':
        user="aashik"
        created_time=datetime.now()
        company_id=request.form['company_id']
        print(request.form)
        division_id=request.form['division_id']
        query_type=request.form['query_type']
        query=request.form['sp_name']
        num_of_parameters=request.form['parameters']
        schedule_time=request.form['scheduler_time']
        schedule_type=request.form['scheduler_type']
        query_status='Active'
        timer_status=request.form['status']
        
        query_list=EQUL(query_company_id=company_id,query_division_id=division_id,query_type=query_type,
                        sp_name=query,query_status=query_status,
                        query_createdby=user,query_createdat=created_time)
        db.session.add(query_list)
        db.session.commit()
        
        
        if query_type == 'SP':
            query_list_id=query_list.query_list_id
            paramname=request.form.getlist('paramname[]')
            paramtype=request.form.getlist('paramtype[]')
            parampos=request.form.getlist('paramposition[]')
            status=[]
            for i in range(int(num_of_parameters)):
                status.append('Active')
            
            for i in range(len(paramname)):
                
                query_params=EQP(query_list_id_fk=query_list_id,param_type=paramtype[i],param_name=paramname[i],
                                 param_position=parampos[i],param_status=status[i],
                                 param_createdby=user,param_createdat=created_time)
                db.session.add(query_params)
                db.session.commit() 
        url='google.com'
        timer= EPQT(query_list_id_fk=query_list.query_list_id,timer_company_id=company_id,timer_division_id=division_id,
                    timer_company_url=url,timer_type=schedule_type,timer_time=schedule_time,timer_status=timer_status,timer_createdby=user,timer_createdat=created_time)
        db.session.add(timer)
        db.session.commit()
        
                                  
        print("THE PARAM NAMES ARE:",paramname)


        flash("Inserted Successfully")  
        return redirect('/viewschedule')  
        
    else:
        return render_template('schedule.html',form=form) 

@app.route('/')
@app.route('/viewschedule')
def viewschedule():
    query='''select company_name,cmpy_divsionname,query_list_id, query_company_id, count(param_name),query_division_id,query_type, sp_name,string_agg(param_type::text,',')as param_type,string_agg(param_position::text,',') as param_position,
    string_agg(param_name::text,',')as param_name,timer_time,timer_type,timer_status from external_export_query_list t1 inner join external_export_query_params t2 on t1.query_list_id =t2.query_list_id_fk
    inner join external_export_query_timer t3 on t3.query_list_id_fk= t1.query_list_id inner join company t4 on t4.company_id=t1.query_company_id inner join company_division t5 on t5.cmpy_divsionid= t1.query_division_id group by query_list_id,company_id,cmpy_divsionid,query_timer_id '''
    
    join_results=db.engine.execute(query).all()  
    print(join_results)
  
    return render_template('viewschedule.html',join_results=join_results)   


@app.route('/edit/<int:id>')
def edit(id):
    form = ScheduleForm()
    query='''select company_name,cmpy_divsionname,query_list_id, query_company_id, count(param_name),query_division_id,query_type, sp_name,string_agg(param_type::text,',')as param_type,string_agg(param_position::text,',') as param_position,
    string_agg(param_name::text,',')as param_name,timer_time,timer_type,timer_status from external_export_query_list t1 inner join external_export_query_params t2 on t1.query_list_id =t2.query_list_id_fk
    inner join external_export_query_timer t3 on t3.query_list_id_fk= t1.query_list_id inner join company t4 on t4.company_id=t1.query_company_id inner join company_division t5 on t5.cmpy_companyid= t4.company_id and query_list_id='''+str(id)+''' group by query_list_id,company_id,cmpy_divsionid,query_timer_id '''
    join_results=db.engine.execute(query).all()
    
    print(join_results)
    return render_template('update.html',join_results=join_results,form=form) 

@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
 
    if request.method == 'POST':
        query_update=EQUL.query.get(id)
        user="aashik"
        created_time=datetime.now()
        query_update.company_id=request.form['company_id']
        print(request.form)
        query_update.division_id=request.form['division_id']
        query_update.query_type=request.form['query_type']
        query_update.sp_name=request.form['sp_name']
        query_update.query_updatedby=user
        query_update.query_updatedat=datetime.now()
        query_update.query_status=request.form['status']
        
        print(request.form)

        db.session.commit()

    

    paramname=request.form.getlist('paramname[]')
    print("The paframname from updte is:",paramname)
    paramtype=request.form.getlist('paramtype[]')
    parampos=request.form.getlist('paramposition[]')
    status=request.form['status']
    

    print("Length of the paramname",len(paramname))     
    query_params_id=db.session.query(EQP.query_param_list_id). filter_by(query_list_id_fk=id).all()
    query_params_id = list(itertools.chain(*query_params_id))

    print('THE PARAMETERS ID ARE :',query_params_id)
    for i in range(len(paramname)):
        print("Parameter Name {}: {}".format(i,paramname[i]))
        
                
        params_update=EQP.query.filter_by(query_param_list_id=query_params_id[i]).update(dict(param_name=paramname[i],param_type=paramtype[i],param_position=parampos[i],param_status=status,param_updatedby="user",param_updatedat=datetime.now()))           
        
        print("UPDATED DETAILS :",params_update)
        db.session.commit() 
    #     url='google.com'
    
    timer_update= EPQT.query.filter_by(query_list_id_fk=id).update(dict(timer_type=request.form['scheduler_type'],timer_time=request.form['scheduler_time'],timer_status=status,timer_updatedby='aashik',timer_updatedat=datetime.now()))
    print("TIMER UPDATE",timer_update)    
    db.session.commit()
    flash("Updated Successfully")  
    
    return redirect('/viewschedule')         


'''EMAIL FORM FUNCTIONALITIES'''
#MAIL FORM
  
@app.route('/addemail',methods=['GET','POST'])  
def mail():
    print("INSIDE EMAIl")
    form=EmailForm()
    
    if request.method == 'POST':
        print("Inside Post")
        id=request.form['Company_id']
        to_email=request.form['email_to']
        cc_email=request.form['email_cc']
        email_status=request.form['email_status']
        to_mail_list=to_email.split(',')
        to_num=len(to_mail_list)
    
        to_list=[]
        [to_list.append('to') for i in range(to_num)]
        
        print("CC VALUE WHEN THE FIELD IS EMPTY",cc_email)
        if cc_email:
           print("CC IS NOT NONE")
           cc_email_list= cc_email.split(',')
           cc_list=[]
           [cc_list.append('cc') for i in range(len(cc_email_list))]
           print(cc_list)
           print(to_list)
           total_list=list(itertools.chain(to_list, cc_list))
           print(str(total_list))
           total_mail=list(itertools.chain(to_mail_list,cc_email_list))
           
           for i in range(len(total_list)):
               email_details=SM(send_cmpy_divid=id,send_email_tocc=total_list[i],send_emailid=total_mail[i],send_emailstatus=email_status)
               db.session.add(email_details)
               db.session.commit()
            

               
        else:
            for i in range(len(to_mail_list)):
               email_details=SM(send_cmpy_divid=id,send_email_tocc=to_list[i],send_emailid=to_mail_list[i],send_emailstatus=email_status)
               db.session.add(email_details)
               db.session.commit()
        
        flash("Inserted Successfully") 
        return redirect('/viewemail')
    
    return render_template('email.html',form=form)


#EMAIL EDIT
@app.route('/mailedit/<int:id>')
def mail_edit(id):
    form = EmailForm()
    query='''select send_cmpy_divid ,send_email_tocc, string_agg(send_emailid,', ') as email_id,string_agg(send_emailstatus::text, ',') as email_status  from sendingmail  where send_cmpy_divid='''+str(id)+''' group by send_email_tocc,send_cmpy_divid order by send_cmpy_divid;'''
    join_results=db.engine.execute(query).all()
    print(query)
    
    
    return render_template('email_update.html',join_results=join_results,form=form)   


#EMAIL VIEW


@app.route('/viewemail')
def viewmail():
    query='''select send_cmpy_divid ,send_email_tocc, string_agg(send_emailid,', ') as email_id,string_agg(send_emailstatus::text, ',') as email_status 
 from sendingmail group by send_email_tocc,send_cmpy_divid order by send_cmpy_divid;
'''
    
    join_results=db.engine.execute(query).all()
  
    
    
  
    return render_template('viewmail.html',join_results=join_results)   

#MAIL UPDATE

@app.route('/mailupdate/<int:id>',methods=['GET','POST'])
def mailupdate(id):
 
    if request.method == 'POST':
        email_update=SM.query.get(id)
        
        Company_id=request.form['Company_id']
        print(request.form)
        to_email=request.form['email_to']
        cc_email=request.form['email_cc']
        email_status=request.form['email_status']
        to_mail_list=to_email.split(',')
        to_num=len(to_mail_list)
    
        to_list=[]
        [to_list.append('to') for i in range(to_num)]
        
        print("CC VALUE WHEN THE FIELD IS EMPTY",cc_email)
        
        SM.query.filter_by(send_cmpy_divid=id).delete()
        
        db.session.commit()
       

        if cc_email:
           print("CC IS NOT NONE")
           cc_email_list= cc_email.split(',')
           cc_list=[]
           [cc_list.append('cc') for i in range(len(cc_email_list))]
           print(cc_list)
           print(to_list)
           total_list=list(itertools.chain(to_list, cc_list))
           print(str(total_list))
           total_mail=list(itertools.chain(to_mail_list,cc_email_list))
           print('The length of mail Id ',len(total_mail))
           
           for i in range(len(total_list)):
               email_details=SM(send_cmpy_divid=id,send_email_tocc=total_list[i],send_emailid=total_mail[i],send_emailstatus=email_status)
               db.session.add(email_details)
               db.session.commit()
            

               
        else:
            for i in range(len(to_mail_list)):
               email_details=SM(send_cmpy_divid=id,send_email_tocc=to_list[i],send_emailid=to_mail_list[i],send_emailstatus=email_status)
               db.session.add(email_details)
               db.session.commit()
        flash("updated Successfully")            
        return redirect('/viewemail')


#SERVER ADD

@app.route('/addserver',methods=['GET','POST'])  
def serverform():
    form=ServerForm()
    if request.method == 'POST':
        print("Inside Post")
        
        sdiv_id=request.form['serverdivision_id']
        shost=request.form['serverhost']
        sname=request.form['servername']
        spass=request.form['serverpass']
        spath=request.form['serverpath']
        sstatus = request.form['server_status']  
        
        server_details=Ftpserverdetails(server_divisionid=sdiv_id,server_host=shost,server_name=sname,server_password=spass,server_folderpath=spath,server_status=sstatus)
        db.session.add(server_details)
        db.session.commit()
        flash("Inserted Successfully") 
        return redirect('/viewserver')
    return render_template('ftpserver.html',form=form)


#SERVER EDIT

@app.route('/serveredit/<int:id>')
def server_edit(id):
    form = ServerForm()
    query='select * from ftpserverdetails where server_divisionid='+ str(id)
    join_results=db.session.execute(query).all()
    print("Edit OUTPUT",join_results)
    
    
    return render_template('server_update.html',join_results=join_results,form=form)  


# UPDATE SERVER
@app.route('/updateserver/<int:id>',methods=['GET','POST'])  
def updateserver(id):
    
    if request.method == 'POST':
        server_update=Ftpserverdetails.query.get(id)

        server_update.server_division_id=request.form['serverdivision_id']
        server_update.server_host=request.form['serverhost']
        server_update.server_name=request.form['servername']
        server_update.server_password=request.form['serverpass']
        server_update.server_folderpath=request.form['serverpath']  
        server_update.server_status=request.form['server_status']  

        db.session.commit()
        flash("Updated Successfully") 
        return redirect('/viewserver')

 #VIEW SERVER
 
@app.route('/viewserver')
def viewserver():
    
    join_results=Ftpserverdetails.query.all()
    print(join_results)
    return render_template('viewserver.html',join_results=join_results)
      





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

def queryTimer():
    print("querytimer")
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


company_id  = ''
division_id = ''
timer = ''
filename =''
filesenttime = ''
ftpdetails = ''
type_query = ''



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
                     
                    format_data += param_name+','
                if len(params_results)==1:
                        format_data = '1'
                elif len(params_results)==2:
                        format_data = "'cmpy002','user002'"      
                elif len(params_results)==3:         
                        format_data = "'cmpy003','user003','Esakki'" 
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


 


if __name__=="__main__":
    first_thread = threading.Thread(target=queryTimer)
    first_thread.start()
    app.run(host='localhost',port='5002',use_reloader=False) 
    
 