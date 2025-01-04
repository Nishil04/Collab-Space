from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from models import db,app_bcrypt,Influencer,Sponsor,Campaign,CampaignRequest



app=Flask(__name__,static_url_path='/static')
app.secret_key='secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'

db.init_app(app)
app_bcrypt.init_app(app)
app_migrate = Migrate(app,db)

@app.route('/')
def Welcome():
    print(session)
    try:
        if session["logged_in"]:
            return redirect(f'/influencer/{session["username"]}')
        else: 
            return render_template('home.html')
    except KeyError:
        return render_template('home.html')
    

@app.route('/influencer/register', methods=['GET','POST'])
def influencer_register():
    if request.method == 'POST':
        name = request.form["tname"]
        age = request.form["tage"]
        followers = request.form["tfollow"]
        category = request.form["tcat"]
        job = request.form["tjob"]
        reach = request.form["treac"]
        username = request.form["tuse"]
        password = request.form["tpas"]

        # print(f"Received form data: {name}, {age}, {followers}, {category}, {job}, {reach}, {username}, {password}")

        # Hash the password before storing it
        hashed_password = app_bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Influencer(name=name, age=age, followers=followers, category=category, job=job, reach=reach, username=username, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/influencer/login')
        except :
            db.session.rollback()
            return render_template('influencer_register.html')    
            
    return render_template('influencer_register.html')    

@app.route('/influencer/login', methods = ['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        username = request.form['tuse']
        password = request.form['tpas']

        user = Influencer.query.filter_by(username=username).first()
        
        if (user != None) and (user.check_password(password)):
            session['username'] = user.username
            session['logged_in'] = True
            session["role"] = "influencer"
            #session['password'] = user.password
            return redirect(f'/influencer/{user.username}')

        else:
            return redirect('/influencer/login')

    return render_template('influencer_login.html')

@app.route('/sponsor/register', methods=['GET', 'POST'])
def sponsor_register():
    if request.method == 'POST':
        company_name = request.form["tcompanyname"]
        industry = request.form["tindustry"]
        budget = request.form["tbudget"]
        reach = request.form["treach"]
        username = request.form["tuse"]
        password = request.form["tpas"]

        # # Hash the password before storing it
        hashed_password = app_bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = Sponsor(company_name=company_name, industry=industry, budget=budget, reach=reach, username=username, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Sponsor account created successfully!",'success')
            return redirect('/sponsor/login')
        except :
            db.session.rollback()
            flash("There was an error creating you sponsor account, Try again!",'error')
            return render_template('sponsor_register.html')    
            
    return render_template('sponsor_register.html')    
    
@app.route('/sponsor/login', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'POST':
        username = request.form['tuse']
        password = request.form['tpas']

        user = Sponsor.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['logged_in'] = True
            session['username'] = user.username
            session['role'] = 'sponsor'
            return redirect(f'/sponsor/{user.username}')

        else:
            return render_template('sponsor_login.html', error = 'Invalid Details, Try Again!!!')

    return render_template('sponsor_login.html')

#Influencer Home Page
@app.route('/influencer/<string:username>')
def influencer(username):
    
    if session.get("logged_in")==None :
        flash('Please log in to access this page.', 'danger')
        return redirect('/')
    user = Influencer.query.filter_by(username=username).first()
    print(user)
    return render_template('influencer_home.html', user=user)

#Influencer Edit Page
@app.route('/influencer/<string:username>/edit', methods=['GET', 'POST'])
def influencer_edit(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
 
        if request.method == 'POST':
            name = request.form["tname"]
            age = int(request.form["tage"])
            followers = int(request.form["tfollow"])
            category = request.form["tcat"]
            job = request.form["tjob"]
            reach = request.form["treac"]
            user_name = request.form["tuse"]
            password = request.form["tpas"]
            # print(f"Received form data: {name}, {age}, {followers}, {category}, {job}, {reach}, {user_name}, {password}")
      
            modified_entries = user.get_modified_entries({"name":name,"age":age,"followers":followers,"category":category,"job":job,"reach":reach,
                                      "username":user_name,"password":password})
            flag = user.update(modified_entries)

            if(flag):
                flash("Changes were saved successfully",'success')
            elif(flag==0):
                flash("No Changes were detected",'info')
            else:
                flash("Error occured while saving changes",'error')

            

        return render_template("influencer_edit.html",user = user)

@app.route('/influencer/<string:username>/delete')
def influencer_delete(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
        db.session.delete(user)
        db.session.commit()
        logout()
        return redirect('/')
        

#Sponsor Home Page
@app.route('/sponsor/<string:username>')
def sponsor(username):
    
    if session.get("logged_in")==None :
        flash('Please log in to access this page.', 'danger')
        return redirect('/sponsor/login')
    user = Sponsor.query.filter_by(username=username).first()
    print(user)
    return render_template('sponsor_home.html', user=user)

#Sposnor Edit Page
@app.route('/sponsor/<string:username>/edit', methods=['GET', 'POST'])
def sponsor_edit(username):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username = username).first()
        print(user)
        if request.method == 'POST':
            company_name = request.form["tcompanyname"]
            industry = request.form["tindustry"]
            budget = request.form["tbudget"]
            reach = request.form["treach"]
            user_name = request.form["tuse"]
            password = request.form["tpas"]
            # print(f"Received form data: {name}, {age}, {followers}, {category}, {job}, {reach}, {user_name}, {password}")

            campaigns = Campaign.query.filter_by(sponsor_id = user.id)

            modified_entries = user.get_modified_entries({"company_name":company_name,"industry":industry,"budget":budget,"reach":reach,"username":user_name,
                                                          "password":password,"campaigns":campaigns})
            flag = user.update(modified_entries)

            if(flag):
                flash("Changes were saved successfully",'success')
            elif(flag==0):
                flash("No Changes were detected",'info')
            else:
                flash("Error occured while saving changes",'error')

        return render_template("sponsor_edit.html",user = user)


#Logout user page
@app.route('/logout')
def logout():
    if session["logged_in"]:

        session.pop("username")
        session["logged_in"] = None

    else:
        flash('Please log in to access this page.', 'danger')
        return redirect('/')

    return redirect('/')



#Requests Sponsor/Influencer _________________________________________________________________
#     
#Sponsor Invite Requests Page
@app.route('/sponsor/<string:username>/sent_requests')
def sponsor_invites(username):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username = username).first()
        print(user.request_send)
        print(user.request_recieve)
        requests = CampaignRequest.query.filter_by(sender_id = user.id)
        return render_template('sponsor_sent_requests.html',user=user,requests=requests)
    
#Sponsor Requests Page
@app.route('/sponsor/<string:username>/recieved_requests')
def sponsor_recieved_requests(username):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username = username).first()
        requests = CampaignRequest.query.filter_by(reciever_id = user.id)
        return render_template('sponsor_recieved_requests.html',user=user,requests=requests)
    
#Influencer Requests Page
@app.route('/influencer/<string:username>/recieved_requests')
def influencer_recieved_requests(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
        print(user.request_send)
        print(user.request_recieve)
        requests = CampaignRequest.query.filter_by(reciever_id = user.id)


        return render_template('influencer_recieved_requests.html',user=user,requests=requests)
    
#Influencer Sent Requests Page
@app.route('/influencer/<string:username>/sent_requests')
def influencer_sent_requests(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
        requests = CampaignRequest.query.filter_by(sender_id = user.id)

        return render_template('influencer_sent_requests.html',user=user,requests=requests)
    



#Sponsor Campaigns Page
@app.route('/sponsor/<string:username>/campaigns')
def sponsor_campaigns(username):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username = username).first()

        return render_template('sponsor_campaigns.html',user=user)
#Sponsor Campaigns Create new campaign
@app.route('/sponsor/<string:username>/campaigns/new',methods=['GET','POST'])
def create_campaign(username):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username = username).first()

        if request.method == 'POST':
            campaign_name = request.form["campaignName"]
            details = request.form["details"]
            budget = request.form["budget"]
            category = request.form["category"]

            new_campaign = Campaign(campaign_name=campaign_name,details=details,budget=budget,category=category,sponsor_id=user.id)

            try:
                db.session.add(new_campaign)
                db.session.commit()
                flash("Campaign created successfully!","success")
            except:
                db.session.rollback()
                flash("There were an errors while creating a new campaign, Try again!","error")

        return render_template('create_campaign.html',user=user)

#Sponsor Campaign details
@app.route('/sponsor/<string:username>/campaigns/<string:campaign_id>',methods=['GET','POST'])
def campaign(username,campaign_id):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username=username).first()
        campaign = Campaign.query.filter_by(id=campaign_id).first()
        return render_template('campaign_page.html',user=user,campaign=campaign)
  
#Campaign delete
@app.route('/sponsor/<string:username>/campaigns/<string:campaign_id>/delete',methods=['GET','POST'])
def campaign_delete(username,campaign_id):
    if session["logged_in"]:
        user = Sponsor.query.filter_by(username=username).first()
        campaign = Campaign.query.filter_by(id=campaign_id).first()

        flag = campaign.delete()

        if(flag):
            flash("Campaign deleted successfully!","success")
            return redirect(f'/sponsor/{user.username}/campaigns')
        else:
            flash("There were an errors while deleting the campaign","error")

        return render_template('campaign_page.html',user=user,campaign=campaign)
        
@app.route('/sponsor/<string:username>/campaigns/<string:campaign_id>/influencers/find',methods=['GET','POST'])
def find_influencers(username,campaign_id):
    user = Sponsor.query.filter_by(username=username).first()
    influencers = Influencer.query.all()
    campaign= Campaign.query.filter_by(id = campaign_id).first()

    return render_template("all_influencers.html",influencers=influencers,user=user,campaign=campaign)

@app.route('/sponsor/<string:username>/campaigns/<string:campaign_id>/influencers/<string:user_id>',methods=['GET','POST'])
def view_influencer(username,campaign_id,user_id):
    user = Sponsor.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(id=user_id).first()
    campaign= Campaign.query.filter_by(id = campaign_id).first()
    exisiting_request = CampaignRequest.query.filter_by(sender_id=user.id,reciever_id=influencer.id,campaign_id=campaign.id).first()

    if not exisiting_request:
        btn = {"state":"enabled","content":"Invite"}
    else:
        btn = {"state":"disabled","content":f"Invite Request {exisiting_request.status}"}

    return render_template("influencer_page.html",btn=btn,user=user,influencer=influencer,campaign=campaign)

@app.route('/sponsor/<string:sponser_username>/campaigns/<string:campaign_id>/influencers/<string:influencer_id>/invite',methods=['GET','POST'])
def invite_influencer(sponser_username,campaign_id,influencer_id):
    if session['logged_in'] and session['role'] == 'sponsor':
        sponsor = Sponsor.query.filter_by(username=sponser_username).first()
        campaign_request = CampaignRequest.query.filter_by(campaign_id=campaign_id).first()
        existing_influencer_request = CampaignRequest.query.filter_by(sender_id=influencer_id,reciever_id=sponsor.id,campaign_id=campaign_id).first()
        existing_sponsor_request = CampaignRequest.query.filter_by(sender_id = sponsor.id,reciever_id=influencer_id,campaign_id=campaign_id).first()

        if campaign_request:
            campaign_status = campaign_request.status
        else:
            campaign_status = False
            
        if not (existing_influencer_request and existing_sponsor_request) and not campaign_status == CampaignRequest.COMPLETED:
            new_request = CampaignRequest(sender_id=sponsor.id,reciever_id=influencer_id,campaign_id=campaign_id)
            try:
                db.session.add(new_request)
                db.session.commit()
                btn = {"state":"enabled","content":"Invite"}

                flash("Invite request sent successfully! See request's status on request page","success")
            except:
                db.session.rollback()

                flash("Error occured while sending the invite request, Try again!","error")
        else:
            btn = {"state":"disabled","content":f"Influencer Already Sent a Request for this campaign!"}
            flash("Influencer has already sent a request for the same campaign for which you're trying to invite or the campaign is completed! See requests page","error")
        return redirect(f'/sponsor/{sponser_username}/campaigns/{campaign_id}/influencers/{influencer_id}')
 
#My Campaigns Page
@app.route('/influencer/<string:username>/campaigns')
def my_campaigns(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
        accepted_campaigns = CampaignRequest.query.filter_by(reciever_id=user.id,status=CampaignRequest.ACCEPTED)
        for ac in accepted_campaigns :
            print(ac.status)
        return render_template('influencer_campaigns.html',user=user,campaigns=accepted_campaigns)
    
#Find Campaigns Page
@app.route('/influencer/<string:username>/campaigns/find')
def find_campaigns(username):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username = username).first()
        campaigns = Campaign.query.all()

        return render_template('all_campaigns.html',user=user,campaigns=campaigns)

 
#Global Campaign details 
@app.route('/influencer/<string:username>/campaigns/<string:campaign_id>',methods=['GET','POST'])
def influencer_campaign_page(username,campaign_id):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username=username).first()
        campaign = Campaign.query.filter_by(id=campaign_id).first()

        exisiting_request = CampaignRequest.query.filter_by(sender_id=user.id,reciever_id=campaign.sponsor_id,campaign_id=campaign.id).first()

        if not exisiting_request:
            btn = {"state":"enabled","content":"Send Request"}
        else:
            btn = {"state":"disabled","content":f"Request Already Sent | Status : {exisiting_request.status}"}


        return render_template('influencer_campaign_page.html',showbtn=1,btn=btn,user=user,campaign=campaign)
    
@app.route('/influencer/<string:username>/campaigns/<string:campaign_id>/view',methods=['GET','POST'])
def influencer_campaign_page_view(username,campaign_id):
    if session["logged_in"]:
        user = Influencer.query.filter_by(username=username).first()
        campaign = Campaign.query.filter_by(id=campaign_id).first()
        return render_template('influencer_campaign_page.html',showbtn=0,user=user,campaign=campaign)


@app.route('/influencer/<string:username>/campaigns/<string:campaign_id>/request',methods=['GET','POST'])    
def send_campaign_request(username,campaign_id):
    if session['logged_in'] and session['role'] == 'influencer':
        influencer = Influencer.query.filter_by(username=username).first()
        sponsor_id = Campaign.query.filter_by(id=campaign_id).first().sponsor_id
        exisiting_invite_request = CampaignRequest.query.filter_by(sender_id=sponsor_id,reciever_id=influencer.id,campaign_id=campaign_id).first()

        if not exisiting_invite_request :
            new_request = CampaignRequest(sender_id=influencer.id,reciever_id=sponsor_id,campaign_id=campaign_id)
            try:
                db.session.add(new_request)
                db.session.commit()
                flash("Invite request sent successfully! See request's status on request page","success")
            except:
                db.session.rollback()
                flash("Error occured while sending the invite request, Try again!","error")
        else:
            flash("Sponsor has already sent a request for the same campaign for which you're trying to send request!","error")


        return redirect(f'/influencer/{username}/campaigns/{campaign_id}')


@app.route('/influencer/<string:username>/requests/<string:request_id>/accept',methods=['GET','POST'])    
def influencer_accept_request(username,request_id):
    if session['logged_in'] and session['role'] == 'influencer':
        req = CampaignRequest.query.filter_by(id=request_id).first()
        if req.status == req.PENDING:
            req.status = req.ACCEPTED
            try:
                db.session.commit()
                flash("Request has been accepted by you successfully! See request's status on request page","success")
            except:
                db.session.rollback()
                flash("Error occured while accepting the request, Try again!","error")
        else:
            flash("The request was either accepted or rejected already!","error")
        return redirect(f'/influencer/{username}/recieved_requests')


@app.route('/influencer/<string:username>/requests/<string:request_id>/reject',methods=['GET','POST'])    
def influencer_reject_request(username,request_id):
    if session['logged_in'] and session['role'] == 'influencer':
        req = CampaignRequest.query.filter_by(id=request_id).first()
        if req.status == req.PENDING:
            req.status = req.REJECTED
            try:
                db.session.commit()
                flash("Request has bee accepted by you successfully! See request's status on request page","success")
            except:
                db.session.rollback()
                flash("Error occured while accepting the request, Try again!","error")
        else:
            flash("The request was either accepted or rejected already!","error")
        return redirect(f'/influencer/{username}/recieved_requests')
        
@app.route('/sponsor/<string:username>/requests/<string:request_id>/accept',methods=['GET','POST'])    
def sponsor_accept_request(username,request_id):
    if session['logged_in'] and session['role'] == 'sponsor':
        req = CampaignRequest.query.filter_by(id=request_id).first()
        if req.status == req.PENDING:
            req.status = req.ACCEPTED
            try:
                db.session.commit()
                flash("Request has been accepted by you successfully! See request's status on request page","success")
            except:
                db.session.rollback()
                flash("Error occured while accepting the request, Try again!","error")
        else:
            flash("The request was either accepted or rejected already!","error")
        return redirect(f'/sponsor/{username}/recieved_requests')
    
@app.route('/sponsor/<string:username>/requests/<string:request_id>/accept',methods=['GET','POST'])    
def sponsor_rejct_request(username,request_id):
    if session['logged_in'] and session['role'] == 'sponsor':
        req = CampaignRequest.query.filter_by(id=request_id).first()
        if req.status == req.PENDING:
            req.status = req.REJECTED
            try:
                db.session.commit()
                flash("Request has been accepted by you successfully! See request's status on request page","success")
            except:
                db.session.rollback()
                flash("Error occured while accepting the request, Try again!","error")
        else:
            flash("The request was either accepted or rejected already!","error")
        return redirect(f'/sponsor/{username}/recieved_requests')


@app.route('/sponsor/<string:username>/campaigns/<string:campaign_id>/payment',methods=['GET','POST'])
def make_payment(username,campaign_id):
    user = Sponsor.query.filter_by(username = username).first()
    campaign = Campaign.query.filter_by(id = campaign_id).first()
    if request.method == "POST":
        campaign_request =  CampaignRequest.query.filter_by(campaign_id = campaign_id).first()
        print(campaign_request)
        try:
            if campaign_request.status == campaign_request.ACCEPTED:
                campaign_request.status = campaign_request.COMPLETED
                db.session.commit()
                flash("Payment was done successfully!","success")
                return redirect(f'/sponsor/{username}/campaigns/{campaign_id}')
        except:
            db.seesion.rollback()
            flash("Payment failed!","success")
            return redirect(f'/sponsor/{username}/campaigns/{campaign_id}')

        
    return render_template('payment.html',user=user,campaign=campaign)

if __name__ == '__main__':
    app.run(debug=True)
    
