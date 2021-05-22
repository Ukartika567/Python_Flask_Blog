from flask import Flask, render_template, request, session, redirect, flash, send_file
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from datetime import datetime
import os
from werkzeug.utils import secure_filename #ye werkzeug file ko secure krne liye hota h
import math

with open('config.json', 'r') as c:
    params=json.load(c)['params']

upload_folder="C://Users//Shivansh//Documents//FLASK CLASSESS//20-Message_Flashing_and_other-Python_Flask_Resources//static//uploads"
     
local_server=True
app=Flask(__name__)
app.secret_key='super-secret-key' #ye seesion ke liye bnate h
app.config['UPLOAD_FOLDER']=upload_folder  
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']

)
mail=Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI']=params['local_uri']
else:
     app.config['SQLALCHEMY_DATABASE_URI']=params['prod_uri']    
db=SQLAlchemy(app)

class Contacts(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(80), nullable=False)
    email=db.Column(db.String(20), nullable=False)
    phone_no=db.Column(db.String(12), nullable=False)
    msg=db.Column(db.String(120), nullable=False)
    date=db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    sno=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(80), nullable=False)
    tagline=db.Column(db.String(80), nullable=False)
    slug=db.Column(db.String(21), nullable=False)
    content=db.Column(db.String(120), nullable=False)
    img_file=db.Column(db.String(50), nullable=False)
    date=db.Column(db.String(12), nullable=True)


@app.route('/')
def home():
    # flash(message= 'Hello!', category='success')
    # flash('Subscribe to codeWithharry', 'success')
    # flash('Like Harry video', 'danger')
    posts=Posts.query.filter_by().all()
    # [0:params['no_of_posts']]
    last=math.ceil(len(posts)/ int(params['no_of_posts']))

    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    #Pagination Logic
    # First
    if page==1:
        prev='#'
        Next='/?page=' + str(page+1)
    # Last
    elif page==last:
        prev='/?page='+ str(page-1)
        Next='#'
    # middle
    else:
        prev='/?page=' + str(page-1)
        Next='/?page=' + str(page+1)    
    
    return render_template('index.html', params=params, posts=posts, prev=prev, next=Next)


@app.route('/dashboard', methods=['GET', 'POST'])
def login():
    
    if ('user' in session and  session['user'] == params['admin_user']):
        posts=Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method=="POST":
        #REDIRECT TO ADMIN PANEL
        username=request.form.get('uname')
        userpass=request.form.get('pass')
        if(username==params['admin_user'] and userpass== params['admin_password']):
            # set the session variable
            session ['user'] = username
            posts=Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
    
    return render_template('login.html', params=params)

@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def edit(sno):
    if('user' in session and session['user'] == params['admin_user']):
        if request.method=='POST':
            box_title=request.form.get('title')
            tline=request.form.get('tagline')
            slug=request.form.get('slug')
            content=request.form.get('content')
            image_file=request.form.get('image_file')
            date=datetime.now()

            if sno=='0':
                post=Posts(title=box_title, tagline=tline, slug=slug, content=content, img_file=image_file, date=date)
                db.session.add(post)
                db.session.commit()
                
            else:
                post=Posts.query.filter_by(sno=sno).first() #fetch the post from db
                post.title=box_title
                post.tagline=tline
                post.slug=slug
                post.content=content
                post.img_file=image_file
                post.date=date
                db.session.commit()   #commit to add new edited data in db
                return redirect('/edit/' + sno)  #then after redirect the edit/sno page

        post= Posts.query.filter_by(sno=sno).first()        
        return render_template('edit.html', params=params, post=post, sno=sno)

@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if('user' in session and session['user']==params['admin_user']):
        if request.method=='POST':
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return 'Uploaded successfully'

#  Download API
@app.route("/downloadfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)        

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path =upload_folder + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')



@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route('/delete/<string:sno>', methods=['GET','POST'])
def delete(sno):
    if('user' in session and session['user']== params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')


@app.route('/about')
def about():
    return render_template('about.html', params=params)



@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    
    return render_template('post.html', params=params, post=post)

@app.route('/contact', methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry=Contacts(name=name, email=email, phone_no=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('Nem mesage from ' + name, 
                        sender=email,
                        recipients=[params['gmail-user']],
                        body=message + '\n' + phone
        )
        flash(message='Thanks for submitting your details, We will get back to you soon.', category='success')
    return render_template('contact.html', params=params)

app.run(debug=True)                