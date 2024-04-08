from wiki_page import search_wikipedia
from initial_course_list import Courses_list
import json
import os

for course in Courses_list:
    possible_courses = search_wikipedia(course)
    dic = {
        'pages' : possible_courses
    }
    course_filename = 'posible_pages/' + course + '.json'
    if os.path.exists(course_filename):
        os.mknod(course_filename)
    with open(course_filename, 'w+') as f:
        json.dump(dic,f)
