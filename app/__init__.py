# flask_app/app/__init__.py

from flask import Flask
from .config import DevelopmentConfig
from .routes import *

from apscheduler.schedulers.background import BackgroundScheduler
from app.rnn_model import train_and_save_model,ensure_model_exists

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)


    app.config.from_object(config_class)
    ensure_model_exists()
    # Schedule model retraining every week
    scheduler = BackgroundScheduler()
    # scheduler.add_job(func=train_and_save_model, trigger="interval", weeks=1)
    scheduler.add_job(func=train_and_save_model, trigger="interval", minutes=2)

    scheduler.start()

    # Register routes here and assigning routes to functions
    app.add_url_rule('/', 'home', Home)
    app.add_url_rule('/Graphs','Graphs', Graphs)
    app.add_url_rule('/GetBranchesForReport','GetBranchesForReport',GetBranchesForReport , methods=['POST'])
    app.add_url_rule('/DisplayNewReport','DisplayNewReport',DisplayNewReport, methods=['POST'])
    app.add_url_rule('/Update_Plot_Graph','Update_Plot_Graph',Update_Plot_Graph,methods=['GET','POST'])
    app.add_url_rule('/plot.png','plot_png',plot_png,methods=['GET','POST'])
    app.add_url_rule('/Update_Branch_Specific_Items_Graph','Update_Branch_Specific_Items_Graph',Update_Branch_Specific_Items_Graph,methods=['GET','POST'])
    app.add_url_rule('/Login','Login',Login, methods=['POST','GET'])
    app.add_url_rule('/SignOut','SignOut',SignOut ,methods=['GET','POST'])
    app.add_url_rule('/ValidateLogin','ValidateLogin',ValidateLogin,methods=['POST','GET'])
    # app.add_url_rule('/MachineLearning','MachineLearning',MachineLearning,methods=['GET','POST'])
    # app.add_url_rule('/UseMachineLearning','UseMachineLearning',UseMachineLearning,methods=['GET','POST'])
    app.add_url_rule('/UserManual','UserManual',UserManual, methods=['GET','POST'])
    app.add_url_rule('/download_csv','download_csv',download_csv, methods=['GET','POST'])
    app.add_url_rule('/machine_learning_view','machine_learning_view',machine_learning_view, methods=['GET','POST'])

    return app
