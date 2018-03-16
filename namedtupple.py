from collections import namedtuple

num_students = int(raw_input())

Student = namedtuple('Student', raw_input().split())

s_marks_total = 0
for i in range(0,num_students):
	student_entry = Student(*raw_input().split())
	s_marks_total += float(student_entry.MARKS)
	
print '{:.2f}'.format(s_marks_total/num_students)
		
