import pickle
import random
import sys
from copy import deepcopy

def date_difference(str1,str2):
	temp=str1.split(" ")
	temp1=map(int,temp[0].split("-"))
	temp=str2.split(" ")
	temp2=map(int,temp[0].split("-"))
	x=temp2[0]-temp1[0]
	temp2[1]+=x*12
	y=temp2[1]-temp1[1]
	temp2[2]+=y*30
	return (temp2[2]-temp1[2])


def Genetic_algorithm(population_class, group_size, prop_class):
	population = []
	#print "Inside genetic algorithm routine"
	for key in population_class:
		population.append(key)

	#print len(population)
	group = []
	while len(population)>1:	
		j = 0
		member = []	
		while j<group_size:
			a = 0
			b = len(population)-1 
			r = random.randint(a,b)
			#print a,b,r,population[r]
			member.append(population[r])
			del population[r]
			j+=1
			#if len(population)<=1:
			#	break
		if len(member)==group_size:
			group.append(member)
	#print group	
	print len(group)			
	it = 100

	fitness_value_best = fitness_function(population,population_class,group,prop_class)
	#print fitness_value_best
	
	while(it>0):
		group_cross = cross_over(group)
		fitness_value_cross = fitness_function(population,population_class,group_cross,prop_class)
		print group_cross
		print "============================================"
		#print sum(fitness_value_cross)
		if sum(fitness_value_cross)>sum(fitness_value_best):
			fitness_value_best = deepcopy(fitness_value_cross)
			group = deepcopy(group_cross)
		it-=1

	
	return group,fitness_value_best


#def fitness_function_final(population,population_class,group,prop_class):	
def fitness_function(population,population_class,group,prop_class):   
	score = []
	#no_groups = len(population)/float(len(group))
	min_class_val = {1:0.0,2:0.0,3:0.0}
	for i in xrange(1,4):
		min_class_val[i] = prop_class[i]/float(len(group))
	#print min_class_val	
	for grp in group:
		g_score = 0
		cls = {1:0.0,2:0.0,3:0.0}
		for j in xrange(len(grp)):
			cls[population_class[grp[j]]]+=1
		#print cls
		for k in xrange(1,4):
			if cls[k]>=min_class_val[k]:
				g_score+=1000
		score.append(g_score)
	return score

def cross_over(group):
	group_intm = deepcopy(group)
	a = 0
	b = len(group_intm)-1
	done = []
	cross_rate = int(1.0*len(group_intm))
	while cross_rate>1:
		x = random.randint(a,b)
		y = random.randint(a,b)
		while x==y:
			y = random.randint(a,b)
		w = random.random()
		if w>0.5:
			tmp = group_intm[x][0]
			group_intm[x][0] = group_intm[y][0]
			group_intm[y][0] = tmp
		else:
			tmp = group_intm[x][1]
			group_intm[x][1] = group_intm[y][1]
			group_intm[y][1] = tmp

		cross_rate -= 1
	return group_intm

   
def classify_reviewers(p_reviewer, rev_acpt, rev_delay, s_date, alpha):
	
	reviewer_class = {}
	prop_class = {}
	for rev in rev_delay:
		if rev in p_reviewer:
			flag = 0
			ac = 0.0
			del_l_a = 0.0
			delay = [0.0]
			for i in xrange(1,len(rev_delay[rev])):	
				if date_difference(rev_delay[rev][i],s_date)>0:
					d = float(date_difference(rev_delay[rev][i-1],rev_delay[rev][i]))
					ac = rev_acpt[rev][i]
					delay.append(d)
				else:
					flag = 1
					break
			if flag==1:
				delay.append(float(date_difference(s_date,rev_delay[rev][i])))
			else:
				if len(rev_delay[rev])>1:
					delay.append(float(date_difference(rev_delay[rev][-1],s_date)))
			if len(delay)>1:
				nor = max(delay)
				
				delay = map(lambda x: x/nor,delay)
				del_l_a = delay[-1]
				f_v = alpha*ac + (1-alpha)*del_l_a
				if f_v<0.33:
					reviewer_class[rev] = 1
				elif (f_v>=0.33)and(f_v<0.66):
					reviewer_class[rev] = 2
				else:
					reviewer_class[rev] = 3
				
				
	prop_class[1] = 0
	prop_class[2] = 0
	prop_class[3] = 0
	for rev in reviewer_class:
		prop_class[reviewer_class[rev]]+=1
	#print prop_class[1],prop_class[2],prop_class[3]
	return reviewer_class,prop_class

if __name__=="__main__":

	### filter reviewer for keyword
		# finding paper reviewer map
	fs = open("doc_ver_ref")
	group_size = 2
	doc_rev = {}

	for line in fs:
		temp = line.strip().split("\t")
		if temp[0] not in doc_rev:
			doc_rev[temp[0]] = []
		for i in xrange(2,len(temp)):
			if temp[i] not in doc_rev[temp[0]]:
				doc_rev[temp[0]].append(temp[i])

	fs.close()

	fs = open("key_word_cluster.pickle")
	key_word_doc = pickle.load(fs)
	fs.close()	

	key_word_rev = {}

	for key in key_word_doc:
		key_word_rev[key] = []
		for doc in key_word_doc[key]:
			if str(doc) in doc_rev:
				key_word_rev[key] += doc_rev[str(doc)]
		#print key_word_rev[key]	

	#print len(key_word_rev)
	
	for key in key_word_rev:
		key_word_rev[key] = list(set(key_word_rev[key]))

	# the reviewers for each keyword is obtained---------------------------
	doc_rev_set = {}	

	fs = open("paper_subm_date.pickle")	
	doc_sub_date = pickle.load(fs)
	fs.close()

	fs = open("doc_key_word.pickle")
	doc_keyword = pickle.load(fs)
	fs.close()

	fs = open("top_percentile_reject.pickle")
	top_p_acpt = pickle.load(fs)
	fs.close()
	t_p = 0
	t_a = 0
	for doc in top_p_acpt:
		#print doc,doc_rev[doc]
		if len(doc_rev[doc])==2:
			t_a+=1
			q_paper = doc
			date_subm_q_paper = doc_sub_date[q_paper]
			keyword_q_paper = doc_keyword[int(q_paper)]
			reviewer_q_paper = []
			for key in keyword_q_paper.split("\t"):
				reviewer_q_paper+=key_word_rev[key]
				
			reviewer_q_paper = list(set(reviewer_q_paper))

			fs = open("reviewer_accpt_ratio_val.pickle")
			reviewer_acpt_ratio = pickle.load(fs)
			fs.close()

			fs = open("reviewer_assign_date_val.pickle")
			reviewer_assgn = pickle.load(fs)
			fs.close()
			rec_group = []
			alpha = 0.5

			try:
				reviewer_class,prop_class = classify_reviewers(reviewer_q_paper, reviewer_acpt_ratio, reviewer_assgn, date_subm_q_paper, alpha)

				rec_group,fitness_value = Genetic_algorithm(reviewer_class,group_size,prop_class)
				
				doc_rev_set[doc] = rec_group

				#print len(rec_group)
				
				rec_group_use = []

				for grp in rec_group:
					c_0 = reviewer_class[grp[0]]
					c_1 = reviewer_class[grp[1]]
					s = c_0 + c_1
					if (c_0!=1)and(c_1!=1)and(s in [3,4,5]):
						rec_group_use.append(grp)
				#print len(rec_group_use)
				#print "-----------------"
				
				for grp in rec_group_use:
					if (grp[0] in doc_rev[doc])or(grp[1] in doc_rev[doc]):
						t_p +=1
						break
			
			except:
				continue
			#print t_a,float(t_p)/t_a
	print t_p,t_a

	fs = open("doc_review_reco_set.pickle","w")
	pickle.dump(doc_rev_set,fs)
	fs.close()
