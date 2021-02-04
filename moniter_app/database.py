from moniter_app import db

def init(db):
    ##
    # at root of package, that is, same level as moniter_app
    # 1. from moniter_app import db
    # 2. from moniter_app import database
    # 3. db.create_all(), ## that is for create table
    # 4. database.init(db), ## that is for insert user accounts

    education = Account(username="education", password="education", _type="education")
    engineer = Account(username="engineer", password="engineer", _type="engineer")
    employee = Account(username="employee", password="employee", _type="employee")
    PM = Account(username="PM", password="PM", _type="PM")
    db.session.add_all([education, engineer, employee, PM])
    db.session.commit()

class Account(db.Model):
    """記錄使用者資料的資料表"""
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    _type = db.Column("type", db.String(15), nullable=False)

    def __repr__(self):
        return 'id:%s, username:%s, type:%s' % (self.id, self.username, self._type)

class Schools(db.Model):
    """記錄學校聯絡資料的資料表"""
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    district = db.Column(db.String(5), nullable=False)
    address = db.Column(db.String(50))
    infoGroupName = db.Column(db.String(5))
    infoGroupPhone = db.Column(db.String(15))
    generalAffairsName = db.Column(db.String(5))
    generalAffairsPhone = db.Column(db.String(15))
    agentName = db.Column(db.String(5))
    agentPhone = db.Column(db.String(15))
    workerLeaderName = db.Column(db.String(5))
    workerLeaderPhone = db.Column(db.String(15))
    workerOneName = db.Column(db.String(5))
    workerOnePhone = db.Column(db.String(15))
    workerTwoName = db.Column(db.String(5))
    workerTwoPhone = db.Column(db.String(15))

    # foreign key
    progress = db.relationship('Progress', backref='schools', lazy=True)
    inventory = db.relationship('DeviceInventory', backref='schools', lazy=True)

    def __repr__(self):
        return 'id:%s, school name:%s, district:%s' % (self.id, self.name, self.district)


class Progress(db.Model):
    """記錄施工進度的資料表"""
    __tablename__ = 'progress'
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), primary_key=True, nullable=False)
    _type = db.Column("type", db.String(10), primary_key=True, nullable=False)
    expectedDate = db.Column(db.String(10))
    actualDate = db.Column(db.String(10))
    confirmDate = db.Column(db.String(10))
    lastFile = db.Column(db.Text)
    remarks = db.Column(db.Text)
    finished = db.Column(db.Boolean, default=False)

    # def __init__(self, id, _type, exDate, acDate, coDate, lastF, remark, finished):
    #     self.school_id = id
    #     self._type = _type
    #     self.expectedDate = exDate
    #     self.actualDate = acDate
    #     self.confirmDate = coDate
    #     self.lastFile = lastF
    #     self.remarks = remark
    #     self.finished = finished

    def __repr__(self):
        return 'school id:%s, type:%s' % (self.school_id, self._type)

class Devices(db.Model):
    """記錄裝置列表的資料表"""
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(20), unique=True, nullable=False)

    # foreign key
    inventory = db.relationship('DeviceInventory', backref='devices', lazy=True)

    def __repr__(self):
        return 'id:%s, type:%s' % (self.id, self.name)

class DeviceInventory(db.Model):
    """記錄裝置列表的資料表"""
    __tablename__ = 'deviceInventory'
    school_id = db.Column(db.Integer, db.ForeignKey("schools.id"), primary_key=True, nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), primary_key=True, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer)#, server_default=0, default=0)  # it fucking don't work

    def __repr__(self):
        return 'school id:%s, device id:%s' % (self.school_id, self.device_id)