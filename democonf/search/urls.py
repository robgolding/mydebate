from django.conf.urls.defaults import *
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from views import DemoconfSearchView
from django.db.models import get_model

sqs = SearchQuerySet()

urlpatterns = patterns('haystack.views',
	
	url(r'^$', DemoconfSearchView(template='search/search.html', searchqueryset=sqs, form_class=SearchForm), name='haystack_search'),

)
