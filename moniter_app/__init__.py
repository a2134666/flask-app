from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
#from datetime import timedelta
import os

#  取得啟動文件資料夾路徑
pjdir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
#  新版本的部份預設為none，會有異常，再設置True即可。
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = os.urandom(24)
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(pjdir, 'work_process.sqlite')

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

from moniter_app import view

# if __name__ == "__main__":
#     app.run(debug=True)