# -*- coding:utf-8 -*-

import settings

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout_then_login, password_change

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('exampaper.question.views',
    # Examples:
    # url(r'^$', 'exampaper.views.home', name='home'),
    # url(r'^exampaper/', include('exampaper.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    #forebakground
    url(r'^$', 'home'),
    url(r'^home$', 'home', name='home'),
    url(r"^show_paper/(?P<paper_id>\d+)$", "show_paper", name="show_paper"),
    url(r"^prepare_start/(?P<paper_id>\d+)$", "prepare_start", name="prepare_start"),
    url(r"^handle_answer$", "handle_answer", name="handle_answer"),
    #background
    url(r"^bg$", "bg_index", name="bg_index"),
    url(r"^bg/question_index$", "question_index", name="question_index"),
    url(r"^bg/question_delete$", "question_delete", name="question_delete"),
    url(r"^bg/create_question$", "create_question", name="create_question"),
    url(r"^bg/edit_question/(?P<question_id>\d+)$", "edit_question", name="edit_question"),
    url(r"^bg/paper_index", "paper_index", name="paper_index"),
    url(r"^bg/paper_delete$", "paper_delete", name="paper_delete"),
    url(r"^bg/create_paper$", "create_paper", name="create_paper"),
    url(r"^bg/edit_paper/(?P<paper_id>\d+)$", "edit_paper", name="edit_paper"),
    url(r"^bg/paper_questions/(?P<paper_id>\d+)$", "paper_questions", name="paper_questions"),
    url(r"^bg/paper_detail/(?P<paper_id>\d+)$", "paper_detail", name="paper_detail"),
    url(r'^login$', login, {'template_name': 'login.html'}, name="login"),
    url(r'^logout$', logout_then_login, name="logout"),
)


urlpatterns += patterns('django.views.static',
    (r'^static/(?P<path>.*)$', 'serve', {'document_root': settings.STATIC_URL}),
)
