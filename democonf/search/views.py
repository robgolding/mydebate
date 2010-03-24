## 
## Author: Rob Golding
## Project: myDebate
## Group: gp09-sdb
## 

from haystack.views import SearchView

class DemoconfSearchView(SearchView):
	def __name__(self):
		return "DemoconfSearchView"

	def extra_context(self):
		extra = super(DemoconfSearchView, self).extra_context()
		extra['q'] = self.request.GET.get('q', None)
		return extra
