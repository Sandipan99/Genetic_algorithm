import pickle
from copy import deepcopy
from G_A import classify_reviewers,cross_over,fitness_function
import random
import sys

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

def swap(A):
	B = [A[1],A[0]]
	return B

def Genetic_algorithm(population_class, group_size, prop_class,reviewer):
	population = []
	#print "Inside genetic algorithm routine"
	reviewer_c = swap(reviewer)
	#print reviewer,reviewer_c
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
	it = 0

	fitness_value_best = fitness_function(population,population_class,group,prop_class)
	#print fitness_value_best
	
	while(True):
		group_cross = cross_over(group)
		fitness_value_cross = fitness_function(population,population_class,group_cross,prop_class)
		#print group_cross
		#print sum(fitness_value_cross)
		
		if sum(fitness_value_cross)>sum(fitness_value_best):
			fitness_value_best = deepcopy(fitness_value_cross)
			group = deepcopy(group_cross)
		
	
	return group,fitness_value_best,it




def read_pickle(fname):
	fs = open(fname)
	A = pickle.load(fs)
	fs.close()
	return A

def calculate_acpt_ratio(A):
	cnt = 0
	cnt_r = 0
	for obj in A:
		if obj=='A':
			cnt+=1
		elif obj=='R':
			cnt_r+=1
		else:
			continue
	val = 0.0
	try:
		val = float(cnt)/(cnt+cnt_r)
	except:
		val = 0.0
	return val
		

def find_reviewer(paper,keyword_reviewer,keyword,rev_assgn,rev_acpt_rjct,alpha,reviewer,rev_last_assgn,date):
	population = []
	prop_class = {}
	reviewer_class = {}
	temp = keyword.split("\t")
	for key in temp:
		population = list(set().union(population,keyword_reviewer[key]))
	if(reviewer[0] in population)and(reviewer[1] in population):
		print "both reviewers present in population"
	else:
		print "assigned reviewers not present"
	#print "Initial population obtained"
	for rev in population:
		a_c = calculate_acpt_ratio(rev_acpt_rjct[rev])
		del_l_a = 0.0
		delay = deepcopy(rev_assgn[rev])
		d = date_difference(rev_last_assgn[rev],date)
		delay.append(d)
		if len(delay)>1:
			try:
				nor = max(delay)
				delay = map(lambda x: x/nor,delay)
				del_l_a = delay[-1]
	
				f_v = alpha*a_c + (1-alpha)*del_l_a
				if f_v<0.33:
					reviewer_class[rev] = 1
				elif (f_v>=0.33)and(f_v<0.66):
					reviewer_class[rev] = 2
				else:
					reviewer_class[rev] = 3
			except:
				continue	
				
	prop_class[1] = 0
	prop_class[2] = 0
	prop_class[3] = 0
	for rev in reviewer_class:
		prop_class[reviewer_class[rev]]+=1
	#print prop_class[1],prop_class[2],prop_class[3]
	return reviewer_class,prop_class	

def update(keyword,keyword_reviewer,reviewer,rev_last_assgn,rev_assgn,rev_acpt_rjct):
	temp = keyword.split("\t")
	for key_w in temp:
		if key_w not in keyword_reviewer:
			keyword_reviewer[key_w] = []
		for rev in doc_reviewer[str(p)]:
			keyword_reviewer[key_w].append(rev)
	for rev in reviewer:
		if rev not in rev_last_assgn:
			rev_last_assgn[rev] = date
			rev_assgn[rev] = [0]
			if p in acpt:
				rev_acpt_rjct[rev] = ['A']
			elif p in rjct:
				rev_acpt_rjct[rev] = ['R']
			else:
				rev_acpt_rjct[rev] = ['W']
		else:
			delay = date_difference(rev_last_assgn[rev],date)
			rev_last_assgn[rev] = date
			rev_assgn[rev].append(delay)
			if p in acpt:
				rev_acpt_rjct[rev].append('A')
			elif p in rjct:
				rev_acpt_rjct[rev].append('R')
			else:
				continue

	#print "reviewer",reviewer
	#print keyword_reviewer
	#print rev_last_assgn
	#print rev_assgn
	#print rev_acpt_rjct
	#print "--------------------"
	
	return keyword_reviewer,rev_last_assgn,rev_assgn,rev_acpt_rjct	

def evaluate(group,fitness_score,reviewer):
	group_score = {}
	k = 0
	for i in xrange(len(group)):
		g = group[i][0]+"\t"+group[i][1]
		group_score[g] = fitness_score[i]

	for rev,score in sorted(group_score.items(),key = lambda x:x[1], reverse = True):
		k+=1
		rev_rec = rev.split("\t")
		if (rev_rec[0] in reviewer)and(rev_rec[1] in reviewer):
			return k,1
	return 0,0	

def select_random(group):
	a = 0
	b = len(group) - 1	
	c = random.randint(a,b)
	return group[c]

if __name__ == "__main__":

	paper = {}
	fs = open("paper_subm_sorted")
	for line in fs:
		temp = line.strip().split("\t")
		paper[int(temp[0])] = temp[1]
	fs.close()
	
	doc_reviewer = {}
	fs = open("doc_ver_ref")
	for line in fs:
		temp = line.strip().split("\t")
		if temp[0] not in doc_reviewer:
			doc_reviewer[temp[0]] = []
			for i in xrange(2,len(temp)):
				doc_reviewer[temp[0]].append(temp[i])
	fs.close()

	doc_keyword = read_pickle("doc_key_word.pickle")
		
	acpt = []
	rjct = []

	fs = open("accepted_papers_all_info_final")
	for line in fs:
		temp = line.strip().split("\t")
		acpt.append(int(temp[0])) 
	fs.close()

	fs = open("rejected_papers_all_info_final")
	for line in fs:
		temp = line.strip().split("\t")
		rjct.append(int(temp[0]))
	fs.close()

	keyword_reviewer = {}
	rev_assgn = {}
	rev_last_assgn = {}
	rev_acpt_rjct = {}
	alpha = 0.5
	group_size = 2
	paper_top = read_pickle("top_percentile_accept.pickle")
	t_p = 0 
	N_D = []
	cnt = 0
	#print "algorithm -----"
	for p,date in sorted(paper.items(),key = lambda x:x[0]):
		if str(p) in doc_reviewer:
			cnt+=1
			if (str(p) not in paper_top)or(len(doc_reviewer[str(p)])<2):
				#print p,date
				#print doc_keyword[p].split("\t")
				keyword_reviewer,rev_last_assgn,rev_assgn,rev_acpt_rjct = update(doc_keyword[p],keyword_reviewer,doc_reviewer[str(p)],rev_last_assgn,rev_assgn,rev_acpt_rjct)	
					
			else:
				reviewer_class,prop_class = find_reviewer(str(p),keyword_reviewer,doc_keyword[p],rev_assgn,rev_acpt_rjct,alpha,doc_reviewer[str(p)],rev_last_assgn,date) 		
				rec_group,fitness_value,it = Genetic_algorithm(reviewer_class,group_size,prop_class,doc_reviewer[str(p)])
				# rec_grp = select_random(rec_group) # random recommendation without editor intervention 
				keyword_reviewer,rev_last_assgn,rev_assgn,rev_acpt_rjct = update(doc_keyword[p],keyword_reviewer,doc_reviewer[str(p)],rev_last_assgn,rev_assgn,rev_acpt_rjct)
				#keyword_reviewer,rev_last_assgn,rev_assgn,rev_acpt_rjct = update(doc_keyword[p],keyword_reviewer,rec_grp,rev_last_assgn,rev_assgn,rev_acpt_rjct) #to be used in conjunction with select_random.....

	
				p_r,k = evaluate(rec_group,fitness_value,doc_reviewer[str(p)])
				t_p+=p_r
				N_D.append(k)
				#print p_r,k
				print p,p_r,k,len(rec_group),it
				print "-------------"

	#print t_p,len(N_D)

