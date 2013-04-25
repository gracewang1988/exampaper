# -*- coding: utf-8 -*-

from django.db import models


class Question(models.Model):
    """判断试题"""
    
    content = models.CharField("题目内容", max_length=200)
    description = models.TextField("题目描述", blank=True)
    correct_answer = models.BooleanField("正确答案")
    score = models.IntegerField("题目分值", default=0)
    status = models.BooleanField("是否存在试题库", default=True)
    instime = models.DateTimeField("创建时间", auto_now_add=True)
    uptime = models.DateTimeField("更新时间", auto_now=True)
    
    def content_for_short(self):
        """试题内容的简写"""
        
        length = 18
        result = self.content if len(self.content) <= length else (self.content[0:length] + "...")
        return result
        
    def get_correct_answer(self):
        """获取正确答案"""
        result = "对" if self.correct_answer else "错"
        return result
        
        
class Paper(models.Model):
    """试卷"""
    
    name = models.CharField("试卷名称", max_length=200)
    title = models.CharField("试卷标题", max_length=200)
    
    question = models.ManyToManyField(Question, blank=True)
    question_orders = models.CommaSeparatedIntegerField("试题排序", max_length=500)
    answer_orders = models.CommaSeparatedIntegerField("试题答案", max_length=500)
    score = models.CommaSeparatedIntegerField("每题分数", max_length=500)
    status = models.BooleanField("是否存在试卷库", default=True)
    instime = models.DateTimeField("试卷创建时间", auto_now_add=True)
    uptime = models.DateTimeField("更新时间", auto_now=True)
    
    def get_questions_count(self):
        """获取试题个数"""
        
        return self.question.count()
        
    def get_ordered_questions(self):
        """获取试卷中顺序排列的试题集"""
        if not self.question_orders:
            return []
        else:
            qids = [int(qid) for qid in self.question_orders.split(",")]
            return [self.question.get(id=qid) for qid in qids]
        
    def get_answer_num(self):
        return self.answer_set.count()
    
    def get_total_scores(self):
        if not self.score:
            return 0
        else:
            return sum([int(s) for s in self.score.split(",")])
            
    def get_all_answers(self):
        return self.answer_set.all()
    class Meta:
        ordering = ("-instime", )
    
    
class Answer(models.Model):
    """用户回答试卷记录"""
    
    paper = models.ForeignKey(Paper, verbose_name='试卷编号')
    answer_orders = models.CommaSeparatedIntegerField("试卷题目答案，按题目顺序", max_length=500)
    scores = models.IntegerField("用户得分数")
    ip = models.IPAddressField('用户IP地址')
    user_agent = models.TextField('User-Agent', null=True, blank="True")
    instime = models.DateTimeField('答卷时间', auto_now_add = True)
    uptime = models.DateTimeField("更新时间", auto_now=True)
