str = 'I on(A,B) on(B,C) on(C,Table) clear(A)'

class Atom:
	def __init__(self,a_name,t_list,n):
		self.name =  a_name		
		self.terms_list = t_list
		# 0 negative 1 not negative
		self.negative = n

"""
line_list = str.split()
atoms_list = []

for atom in line_list[1:]:

	p_list = []

	atom = atom[:-1]
	atomm = atom.split('(')

	name = atomm[0]

	for a in atomm[1:]:
		part = a.split(',')
		for p in part:
			p_list.append(p)
	negative = 1		

	atoms_list.append(Atom(name,p_list,negative))

for atom in atoms_list:
	print ('atom: ' + atom.name)
	for p in atom.terms_list:
		print p


str = 'A move(b,f,t) : on(b,f)  clear(b) clear(t) -> -on(b,f) on(b,t) -clear(t) clear(f)'

line_terms = str.split()
n_point = 0
for term in line_terms:
	if term == '->':
		break
	n_point = n_point + 1		

for a in str[1:n_point+1]:
	print (a)

print n_point	

"""

from itertools import combinations_with_replacement,permutations,product
a = 'olatudobem'

s = combinations_with_replacement(a,3)
"""
for i in s:
	print (i)
	ii = list(i)
	print(ii)
"""
a = ['A','B','C','Table']	
bb = ['A','B']
b = ('B','A','C')

p = product(a,repeat = 2)

for pp in p:
	print(pp)

a = [2,'Table']


for n in a:
	try:
	   val = int(n)
	except ValueError:
	   print(n)