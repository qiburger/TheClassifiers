import json
import requests
import os
import urllib2
import time 
api_key = "55bf221011d6f639454054ae5044e5fb:1:73719482"
api_key2 = "e04f440978b898f0490bf123bfb5db5a:14:73722280"

def get_all_files(directory):
	dir_list = os.listdir(directory)
	filepaths = []
	for file in dir_list:
		filepaths.append(directory + "/" +file)
	return filepaths

def cut_sentence(sentence):
	sentence = sentence.replace(" ", "+")	
	total_words = 0
	for i in xrange(0, len(sentence)):
		if(sentence[i] == '+'):
			total_words += 1
		if(total_words == 20):
			return sentence[0:i]
	return sentence

def times_call(sentence, key):
	mod_sentence = cut_sentence(sentence)
	url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?fq=body%3A+%28%22'
	url = url + mod_sentence + "%22%29&"
	url = url + "api-key=" + key
	url = url.replace("&amp", "%26")
	r = requests.get(url)

	#switch between api_key's if one is no good
	if(not r and key == api_key):
	#	print(url)
		print("Bad request, first time")
		time.sleep(1)
		return times_call(sentence, api_key2)
	elif(not r and key == api_key2):
		#print(url)
		print("Bad request, second time")
		time.sleep(1)
		return times_call(sentence, api_key)
	#grab the json object and check if we have returns
	json_obj = r.json()
	hits = json_obj["response"]["meta"]["hits"]
	if(hits == 0):
		#print(url)
		print("couldn't find any data on the json pull")
		return False
	if(not json_obj):
		print("Couldn't find json_obj")
		return False
	different_results = json_obj["response"]["docs"]
	gina = 0
	with open('poss_results.txt', 'a') as g:
		for result in different_results:
			if(not result["byline"]):
				#print(result)
				#print("No authors for this article")
				continue
			people = result["byline"]["person"]
			for person in people:
				if(not "firstname" in person or not "lastname" in person):
					print(person)
					continue
				first = person["firstname"].lower()
				first = first.encode('utf8')
				last = person["lastname"].lower()
				last = last.encode('utf8')
				if(first == "gina" and last == "kolata"):
					gina = 1	
					#print("Hit a legit article")
		g.write(sentence + '\t' + str(gina) + '\n')
	return True
def parse_train(author_dict, path):
	with open(path, 'rU') as f:
		i = 0
		for line in f:
			i+=1
			line = line.rsplit('\n', 1)[0]
			sent = line.split('\t')[0]
			author = line.split('\t')[1]
			author_dict[sent] = int(author)
			if(i==1000):
				break

def compare_dicts(train_dict, poss_dict):
	total = 0
	correct = 0
	for key in train_dict:
		total += 1
		if(train_dict[key] == poss_dict[key]):
			correct +=1			
	return float(correct) / total

if __name__ == '__main__':
	author_dict = {}
	path = '/home1/c/cis530/project/data/project_articles_train'
	parse_train(author_dict, path)
 	i = 0
	with open(path, 'rU') as f:
		for line in f:
			i+=1
			sentence = line.rsplit('\n', 1)[0]	
			sentence = line.rsplit('\t', 1)[0]
			print("We are on sentence " + str(i))
			if(not times_call(sentence, api_key)):
				with open('poss_results.txt', 'a') as g:
					g.write(sentence + '\t' + '0' + '\n')
			if(i == 1000):
				break	
	poss_path = 'poss_results.txt'	
	poss_author_dict = {}
	parse_train(poss_author_dict, poss_path)
	accuracy = compare_dicts(author_dict, poss_author_dict)
	print("My accuracy was " + str(accuracy))
