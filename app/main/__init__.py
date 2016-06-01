from flask import Blueprint
from dmutils.content_loader import ContentLoader

main = Blueprint('main', __name__)

content_loader = ContentLoader('app/content')
content_loader.load_manifest('cirrus', 'services', 'edit_service')
content_loader.load_manifest('cirrus', 'services', 'edit_submission')
content_loader.load_manifest('cirrus', 'declaration', 'declaration')
content_loader.load_messages('cirrus', ['dates'])


@main.after_request
def add_cache_control(response):
    response.cache_control.no_cache = True
    return response


from .views import services, suppliers, login, frameworks, users, briefs
from . import errors
