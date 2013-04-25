# -*- coding: utf-8 -*-

import os
import re
import datetime
import simplejson
import uuid

from django.core.cache import cache
from django.template import RequestContext, loader
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from exampaper.question.forms import Question, Paper, Answer
from exampaper.question.forms import QuestionForm, PaperForm
import settings
import utils

EACH_PAGE_NUM = 15  #每页记录数
ANSWER_MAX_HOUR = 3  #答题最大时间数


def home(request):
    """试卷列表"""
    papers = Paper.objects.filter(status=True)
    return render_to_response("foreground/home.html", 
        {"papers": papers}, context_instance=RequestContext(request))

   
def show_paper(request, paper_id):
    """显示指定的试卷"""
    key = utils.get_paper_cache_key(paper_id)
    page_cached = cache.get(key, None)
    # 获取缓存
    if page_cached:
        return HttpResponse(page_cached)
    paper = get_object_or_404(Paper, id=paper_id, status=True)
    page_cached = loader.render_to_string('foreground/show_paper.html', {"paper": paper},  
        context_instance=RequestContext(request))
    cache.set(key, page_cached, settings.CACHE_PAGE_TIME)
    return HttpResponse(page_cached)



def prepare_start(request, paper_id):
    """答题之前准备cache和cookie"""
    
    reference_url = request.META.get("HTTP_REFERER", "").lower()
    if reference_url == "/".join((settings.SITEURL, "show_paper", str(paper_id))):
        uni_mark = str(uuid.uuid4())
        now = datetime.datetime.now()
        cache.set(uni_mark, now, ANSWER_MAX_HOUR * 60 * 60)
        response = HttpResponse("")
        response.set_cookie(key=settings.COOKIE_KEY, value=uni_mark, 
            expires=now+datetime.timedelta(hours=ANSWER_MAX_HOUR))
        return response
    else:
        return HttpResponse("")
    

def handle_answer(request):
    """
    分析答案
    """

    result = {"status": 0, "data": {}}
    paper_id = request.POST.get('paper_id', '0')
    answer_str = request.POST.get('answer', '')
    answer = utils.convert_to_list(answer_str)
    try:
        paper = Paper.objects.get(id=paper_id)
    except (Paper.DoesNotExist, ValueError), e:
        return HttpResponse(simplejson.dumps(result))
    
    if not utils.check_answer(answer):    
        return HttpResponse(simplejson.dumps(result))
    #验证防刷机制
    uni_mark = request.COOKIES.get(settings.COOKIE_KEY, "")
    if not uni_mark:
        return HttpResponse(simplejson.dumps(result))
    start_datetime = cache.get(uni_mark, None)
    if not start_datetime:
        return HttpResponse(simplejson.dumps(result))
    interval_seconds = (datetime.datetime.now() - start_datetime).seconds
    if interval_seconds < (paper.get_questions_count() * 1) or interval_seconds > ANSWER_MAX_HOUR * 60 * 60:
        return HttpResponse(simplejson.dumps(result))
        
    # 获取数据库的数据
    correct_answer = paper.answer_orders
    score_list = paper.score
    score = utils.cal_score(answer, 
                            utils.convert_to_list(correct_answer),
                            utils.convert_to_list(score_list))
    if score is None:
        return HttpResponse(simplejson.dumps(result))
    beat_count = Answer.objects.filter(paper__id=paper_id, scores__lt=score).count()
    result["status"] = 1
    result["data"].update(score=score, 
                          beat_count=beat_count, 
                          correct_answer=paper.answer_orders)
                          
    #把用户的答案信息保存起来
    new_answer = Answer(paper=paper, answer_orders=answer_str, scores=score, 
        ip=request.META.get("REMOTE_ADDR", ""), 
        user_agent=request.META.get("HTTP_USER_AGENT", ""))
    new_answer.save()
    
    return HttpResponse(simplejson.dumps(result))


###########################################
               #后台管理#
###########################################
    
    
@login_required
def bg_index(request):
    """后台首页"""
    
    return render_to_response('base_bg.html', {}, context_instance=RequestContext(request))
    
    
@login_required
def question_index(request):
    """显示所有试题"""
    
    all_questions = Question.objects.filter(status=True).order_by('-instime')
    paginator = Paginator(all_questions , EACH_PAGE_NUM)
    page = request.GET.get('page', 1)
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)
        
    return render_to_response('background/question_index.html', {
    'questions': questions,
    'page': page,
    }, context_instance=RequestContext(request))
    
    
@login_required
def create_question(request):
    """创建试题"""
    
    result = ''
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            result = '创建试题成功！'
            form = QuestionForm()
    else:
        form = QuestionForm()
        
    return render_to_response('background/create_question.html', {
        'form': form,
        'result': result,
    }, context_instance=RequestContext(request))
    

@login_required
def edit_question(request, question_id):
    """编辑试题"""
    
    question_obj = get_object_or_404(Question, pk=question_id)
    result = ""
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question_obj = form.update(question_obj)
            result = "修改试题成功！"
            form = QuestionForm(instance=question_obj)
            # 清空对应试卷的缓存页面
            for paper_id in question_obj.paper_set.values_list("id", flat=True):
                key = utils.get_paper_cache_key(paper_id)
                cache.delete(key)
    else:
        form = QuestionForm(instance=question_obj)
    
    return render_to_response('background/edit_question.html', {
        'form': form,
        'result': result,
    }, context_instance=RequestContext(request))
    
    
@login_required
def question_delete(request):
    """从试题库删除，只是把status置为False"""
    
    if request.method == "POST":
        question_id = request.POST.get("question_id", "")
        if not question_id:
            return HttpResponse("error")
            
        try:
            question = Question.objects.get(id=question_id)
        except (Question.DoesNotExist, ValueError), e:
            return HttpResponse("error")
            
        question.status = False
        question.save()
        return HttpResponse("success")
        

@login_required
def paper_index(request):
    """所有的试卷信息"""
    
    all_papers = Paper.objects.filter(status=True).order_by('-instime')
    paginator = Paginator(all_papers , EACH_PAGE_NUM)
    page = request.GET.get('page', 1)
    try:
        papers = paginator.page(page)
    except PageNotAnInteger:
        papers = paginator.page(1)
    except EmptyPage:
        papers = paginator.page(paginator.num_pages)
        
    return render_to_response('background/paper_index.html', {
    'papers': papers,
    'page': page,
    }, context_instance=RequestContext(request))
    
    
@login_required
def create_paper(request):
    """创建试卷"""
    
    result = ''
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if form.is_valid():
            form.save()
            result = '创建试卷成功！'
            form = PaperForm()
    else:
        form = PaperForm()
        
    return render_to_response('background/create_paper.html', {
        'form': form,
        'result': result,
    }, context_instance=RequestContext(request))
    
    
@login_required
def edit_paper(request, paper_id):
    """修改试卷基本信息"""
    
    paper = get_object_or_404(Paper, pk=paper_id)
    result = ''
    if request.method == 'POST':
        form = PaperForm(request.POST)
        if form.is_valid():
            paper = form.update(paper)
            result = '修改试卷成功！'
            form = PaperForm(instance=paper)
            # 清空对应的缓存
            key = utils.get_paper_cache_key(paper_id)
            cache.delete(key)
    else:
        form = PaperForm(instance=paper)
        
    return render_to_response('background/edit_paper.html', {
        'form': form,
        'result': result,
    }, context_instance=RequestContext(request))
    
    
@login_required
def paper_delete(request):
    """从试卷库删除，只是把status置为False"""
    
    if request.method == "POST":
        paper_id = request.POST.get("paper_id", "")
        if not paper_id:
            return HttpResponse("error")
            
        try:
            paper = Paper.objects.get(id=paper_id)
        except (Paper.DoesNotExist, ValueError), e:
            return HttpResponse("error")
            
        paper.status = False
        paper.save()
        # 清空缓存
        key = utils.get_paper_cache_key(paper_id)
        cache.delete(key)

        return HttpResponse("success")
        
        
@login_required
def paper_questions(request, paper_id):
    """试卷配置试题操作，包括添加、移除等"""
    
    paper = get_object_or_404(Paper, pk=paper_id)
    result = ""
    if request.method == "POST":
        sortids = request.POST.get("sortstr", "")
        paper.question_orders = sortids
        new_questions = []
        if sortids:
            sortids = [int(sid) for sid in sortids.split(",")]
            new_questions = [(Question.objects.get(id=sid)) for sid in sortids]
        paper.question = new_questions
        paper.answer_orders = ",".join([str(int(qobj.correct_answer)) for qobj in new_questions])
        paper.score = ",".join([str(qobj.score) for qobj in new_questions])
        paper.save()
        result = "试卷试题配置成功！"
        qids = sortids if sortids else []
        paper_questions = new_questions
        # 清空缓存
        key = utils.get_paper_cache_key(paper_id)
        cache.delete(key)

    else:
        qids = []
        paper_questions = []
        if paper.question_orders:
            qids = [int(qid) for qid in paper.question_orders.split(",")]
            [paper_questions.append(Question.objects.get(id=qid)) for qid in qids]
            
    all_questions = Question.objects.exclude(id__in=qids).filter(status=True).order_by('-instime')
    
    return render_to_response("background/paper_questions.html",{
        "result": result,
        "paper": paper,
        "all_questions": all_questions,
        "paper_questions": paper_questions
    }, context_instance=RequestContext(request))
    
    
@login_required
def paper_detail(request, paper_id):
    """试卷具体详细信息"""
    
    paper = get_object_or_404(Paper, pk=paper_id)
    return render_to_response("background/paper_detail.html", {"paper": paper}, 
        context_instance=RequestContext(request))
        
        
        
