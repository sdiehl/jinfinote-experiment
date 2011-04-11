from django.conf.urls.defaults import patterns, include, url

from ot.views import (
        index,
        socketio
)

urlpatterns = patterns('',

    # The Editor
    url(
        regex=r'^$',
        view=index,
        name='index'
    ),

    # Socket IO hook
    url(
        regex=r'^socket\.io',
        view=socketio,
        name='socketio'
    ),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
