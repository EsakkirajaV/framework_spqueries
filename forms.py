from  flask_wtf import FlaskForm
from wtforms import StringField,IntegerField
from wtforms import validators
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import TimeField
from wtforms.fields.simple import SubmitField, TextAreaField,EmailField
from wtforms.validators import DataRequired, NumberRange
from wtforms.widgets.core import PasswordInput
 
class ScheduleForm(FlaskForm):
    
    company_id= StringField(label='Company Id:',validators=[DataRequired(),NumberRange(min=0)])
    division_id= StringField(label='Division Id:',validators=[DataRequired(),NumberRange(min=0)])
    query_type = SelectField(u' Query Type', choices=[('SP', 'SP') ,('Qeury', 'Query')],validators=[DataRequired()])
    sp_name=TextAreaField('SP_Name',validators=[DataRequired(),])
    parameters=IntegerField('Number of Parameter',validators=[DataRequired(),NumberRange(min=0)])

    scheduler_time=TimeField('Scheduler Time')
    scheduler_type=SelectField(u' Scheduler Type', choices=[('Daily', 'Daily')],validators=[DataRequired()])
    status=SelectField(u' Status', choices=[('Active', 'Active') ,('Inactive', 'Inactive')])
    submit = SubmitField(label='Save')


class EmailForm(FlaskForm):
    
    Company_id=IntegerField(label="Company Id:",validators=[DataRequired(),NumberRange(min=0)])
    email_to=EmailField(label='TO',validators=[DataRequired()])
    
    email_cc=EmailField(label="Cc")
    email_status=SelectField(u' Email Status', choices=[('Active', 'Active') ,('Inactive', 'Inactive')])
    submit = SubmitField(label='Save')
    
class ServerForm(FlaskForm):
    
    serverdivision_id=IntegerField(label="Server Division Id:",validators=[DataRequired(),NumberRange(min=0)])
    serverhost=StringField(label="Server Host:",validators=[DataRequired()])
    servername=StringField(label='Server Name:',validators=[DataRequired()])
    serverpass=StringField(label='Password',validators=[DataRequired()],widget=PasswordInput(hide_value=False))
    serverpath=StringField(label='Server Folder Path',validators=[DataRequired()])
    server_status=SelectField(u'Server Status', choices=[('Active', 'Active') ,('Inactive', 'Inactive')])

    submit = SubmitField(label='Save')
    

    
 
 