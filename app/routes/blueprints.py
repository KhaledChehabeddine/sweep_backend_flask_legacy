"""Summary: Project Blueprints

Organize all root blueprints to easily allow child blueprints to be added to them
"""
from flask import Blueprint
from app.controllers.account.account_category_controller import account_category_api_v1
from app.controllers.components.service_category_controller import service_category_api_v1
from app.controllers.history.reservation_controller import reservation_api_v1
from app.controllers.home.home_main_feature_promotion_controller import home_main_feature_promotion_api_v1
from app.controllers.home.home_main_feature_reward_controller import home_main_feature_reward_api_v1
from app.controllers.home.home_sub_feature_controller import home_sub_feature_api_v1
from app.controllers.search.search_controller import search_api_v1
from app.controllers.user.company_controller import company_api_v1
from app.controllers.user.worker_controller import worker_api_v1

raw_sweep_api_v1 = Blueprint('sweep_api_v1', __name__, url_prefix='/api/v1/sweep')

raw_sweep_api_v1.register_blueprint(account_category_api_v1)
raw_sweep_api_v1.register_blueprint(company_api_v1)
raw_sweep_api_v1.register_blueprint(home_main_feature_promotion_api_v1)
raw_sweep_api_v1.register_blueprint(home_main_feature_reward_api_v1)
raw_sweep_api_v1.register_blueprint(home_sub_feature_api_v1)
raw_sweep_api_v1.register_blueprint(search_api_v1)
raw_sweep_api_v1.register_blueprint(service_category_api_v1)
raw_sweep_api_v1.register_blueprint(worker_api_v1)
raw_sweep_api_v1.register_blueprint(reservation_api_v1)


sweep_api_v1 = raw_sweep_api_v1
