from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_bcrypt import Bcrypt

db = SQLAlchemy()
app_bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(100), unique = True)
    request_send = db.relationship('CampaignRequest',cascade="all,delete",foreign_keys='CampaignRequest.sender_id',backref='sender',lazy=True)
    request_recieve = db.relationship('CampaignRequest',cascade="all,delete",foreign_keys='CampaignRequest.reciever_id',backref='reciever',lazy=True)

    # __mapper_args__ = {
    #     'polymorphic_identity':'user',
    # }

    def check_password(self, password):
        return app_bcrypt.check_password_hash(self.password,password)
    
    def get_modified_entries(self,modifiedUserDict:dict):
        __tmp_attrval_dict = {}
        __modified_entries = {}

        for attr in dir(self):
            if not callable(getattr(self,attr)) and not attr.startswith(("__","_") ) and attr not in ["id","metadata","query","registry","campaigns","request_recieve","request_send"]:
                # print(getattr(self,attr))
                # print(attr)
                __tmp_attrval_dict[attr] = getattr(self,attr)
        

        for key in __tmp_attrval_dict:
            # print(f"{key} : {__tmp_attrval_dict[key]} ({type(__tmp_attrval_dict[key])}) ? {modifiedUserDict[key]} ({type(modifiedUserDict[key])}) ")
            if __tmp_attrval_dict[key] != modifiedUserDict[key]:
                print("changes detected in " + key)
                __modified_entries[key] = modifiedUserDict[key]
            else:
                pass

        return __modified_entries
    
    def update(self,updates:dict):
        if not updates == {}:
            for key in updates:
                print(f"updates{key}:{updates[key]}")
                setattr(self,key,updates[key])
            try:
                db.session.commit()
                return 1
            except:
                db.session.rollback()
                return -1
        else:
            return 0

# influencer table
class Influencer(User):
    id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    name = db.Column(db.String(100), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    followers = db.Column(db.Integer, nullable = False)
    category = db.Column(db.String(100), nullable = False)
    job = db.Column(db.String(100), nullable = False)
    reach = db.Column(db.String(100), unique = True, nullable = False)
     
# sponsor table
class Sponsor(User):
    id = db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    company_name = db.Column(db.String(100), nullable = False)
    industry = db.Column(db.Integer, nullable = False)
    budget = db.Column(db.Integer, nullable = False)
    reach = db.Column(db.String(100), unique = True, nullable = False)
    campaigns = db.relationship('Campaign',cascade="all,delete",backref='sponsor',lazy=True)


#campaign table    
class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(100), nullable = False)
    details = db.Column(db.String(500), nullable = False)
    budget = db.Column(db.Integer, nullable = False)
    category = db.Column(db.String(100), nullable = False)
    sponsor_id = db.Column(db.Integer,db.ForeignKey('sponsor.id'),nullable=False)
    requests = db.relationship('CampaignRequest',cascade="all,delete",foreign_keys = 'CampaignRequest.campaign_id',backref='campaign',lazy=True)

    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return 1
        except:
            db.session.rollback()
            return -1
        
    def getSponsorCompany(self):
        sponsor = Sponsor.query.filter_by(id=self.sponsor_id).first()
        return sponsor.company_name if sponsor else None

    def getAcceptedInfluencers(self):
        accepted_influencers = []
        for request in self.requests:
            if request.status == request.ACCEPTED and (type(request.getRecieverInfo()) == Influencer or type(request.getSenderInfo()) == Influencer):
                if isinstance(request.getRecieverInfo(),Influencer):
                    # print(f"Reciever{request.getRecieverInfo()}")
                    accepted_influencers.append(request.getRecieverInfo())
                elif isinstance(request.getSenderInfo(),Influencer):
                    # print(f"Sender{request.getSenderInfo()}")
                    accepted_influencers.append(request.getSenderInfo())
        
        return accepted_influencers
    


    def getFirstAcceptedInfluencer(self):
        try:
            return self.getAcceptedInfluencers()[0]
        except Exception as e:
            return 0

    def getFirstCompletedInfluencer(self):
        for request in self.requests:
            if request.status == request.COMPLETED:
                if isinstance(request.getRecieverInfo(),Influencer):
                    return [request.getRecieverInfo()]

                elif isinstance(request.getSenderInfo(),Influencer):
                    return [request.getSenderInfo()]
                
                
class CampaignRequest(db.Model):
    ACCEPTED = 'Accepted' 
    REJECTED = 'Rejected'
    PENDING = 'Pending'
    COMPLETED = 'Completed'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    reciever_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    campaign_id = db.Column(db.Integer,db.ForeignKey('campaign.id'),nullable=False)
    status = db.Column(db.Integer,nullable=False,default=PENDING)

    def getSenderInfo(self):
        sponsor = Sponsor.query.filter_by(id=self.sender_id).first()
        influencer = Influencer.query.filter_by(id=self.sender_id).first()
        return  influencer if not sponsor else sponsor
    
    def getRecieverInfo(self):
        sponsor = Sponsor.query.filter_by(id=self.reciever_id).first()
        influencer =Influencer.query.filter_by(id=self.reciever_id).first()
        return  influencer if not sponsor else sponsor
    
    def getCampaignInfo(self):
        return Campaign.query.filter_by(id=self.campaign_id).first()

