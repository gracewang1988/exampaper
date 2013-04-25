# -*- coding:utf-8 -*-

from django.conf import settings

def check_answer(answer_str, check_list=(0, 1)):
	"""
	检查答案里面是否只有0和1
	check_list是元组不是列表，所以不会存在check_list中途被改变而导致的bug
	"""

	return set(check_list) == set(answer_str)

def cal_score(answer_list, correct_answer_list, score_list):
	"""
	计算分数
	>>>cal_score([0, 1, 1], [1, 0, 0], [5, 5, 5])
	>>>0
	>>>cal_score([1,1,1], [1,1,0], [5,5,5])
	>>>10
	"""
	cal_length = len(correct_answer_list)
	if len(answer_list) != cal_length or cal_length != len(score_list):
		return None
	zip_list = zip(answer_list, correct_answer_list, score_list)
	# True作1来计算 True * 5 = 5
	return sum([(i[0] == i[1]) * i[2] for i in zip_list])


def convert_to_list(coma_list, tp=int, split=","): 
	"""
	#tp for type
	>>>convert_to_list("1,2,3")
	>>>[1,2,3]
	"""
	try:
		return [tp(i) for i in coma_list.split(split)]
	except (ValueError, TypeError), e:
		return []

def get_paper_cache_key(paper_id):
	return "%s::%s" % (settings.CACHE_PAGE_KEY_PREFIX, paper_id)
