# -*- coding:utf-8 -*-

import os
import re
import settings

from django.core.cache import cache
from django import forms
from exampaper.question.models import Question, Paper, Answer


class QuestionForm(forms.ModelForm):
    """试题form"""
    
    def save(self):
        """试题保存"""
        
        question_obj = Question(content=self.cleaned_data['content'],
            description=self.cleaned_data['description'], 
            correct_answer = self.cleaned_data['correct_answer'], 
            score=self.cleaned_data['score'])
        question_obj.save()
        
    def update(self, obj):
        """更新试题"""
        obj.content = self.cleaned_data['content']
        obj.description=self.cleaned_data['description']
        obj.correct_answer = self.cleaned_data['correct_answer']
        obj.score=self.cleaned_data['score']
        obj.save()
        return obj
        
    class Meta:
        model = Question
        fields = ('content', 'description', 'correct_answer', 'score')
        
        
class PaperForm(forms.ModelForm):
    """试卷form"""
    
    def save(self):
        """试题保存"""
        
        page_obj = Paper(name=self.cleaned_data['name'], title=self.cleaned_data['title'])
        page_obj.save()
        
    def update(self, obj):
        """更新试卷"""
        
        obj.name = self.cleaned_data['name']
        obj.title = self.cleaned_data['title']
        obj.save()
        return obj
        
    class Meta:
        model = Paper
        fields = ('name', 'title')
