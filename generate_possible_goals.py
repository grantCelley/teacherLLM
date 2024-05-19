import guidance
from guidance import gen, select
from tqdm import tqdm
import os

import json
import glob


MODEL = "dolphin-2.8-mistral-7b-v02.Q2_K.gguf"
model_kwargs = {"verbose": False, "n_gpu_layers": 256, "n_ctx": 30000}

model = guidance.models.LlamaCppChat(MODEL, echo=False, **model_kwargs)

def generate_chapters(title: str, level: str = "undergraduate") -> list[str]:
    """
    Generates chapter topics for the course
     :param title: Title of the course
     :param level: A string for the the level education of the course. eg. "elementry" , "highschool", "undergraduate", "graduate" 
     :return: The list of generated chapter titles
    """

    with guidance.user():
        lm = model + f"You are a teacher teaching about titled {title} at the level of {level}. Generate a 14 chapter course on the topic."
    with guidance.assistant():
        for i in range(14):
            lm += "Chapter" + str(i) +" : " +  gen(name='chapters', list_append=True, max_tokens= 50, stop=['\n', 'Chapter', '.'] ) + "\n"

    return lm['chapters']

def gen_goals(course_title:str, chapter_title: str, level: str ="undergraduate") -> list[str]:
    """
    Generate the course objectives
     :param course_title: Title of the course
     :param chapter_title: Chapter title
     :param level: A string for the the level education of the course. eg. "elementry" , "highschool", "undergraduate", "graduate". Default is "undergraduate"
    :return: The list of generated course objectives
    """

    action_verbs_list = ["implement", 'design' , 'construct', 'develop', 'produce', 'revise', 'propose', 'build', 'devise', 'invent', 'judge', 'justify', 'select', 'critique', 'defend', 'rate', 'evaluate', 'assess', 'rank', 'argue', 'review', 'distinguish', 'differentiate', 'orginize', 'examine', 'compare', 'contrast', 'classify', 'apply', 'use', 'solve', 'compute', 'implement', 'instruct', 'demonstrate', 'interpret', 'complete', 'explain', 'demonstrate', 'summarize', 'review', 'generalize', 'describe', 'identify', 'represent', 'paraphrase', 'interpret', 'define', 'identify', 'recall', 'recite', 'reproduce', 'list', 'name', 'memorize', 'repeat', 'state', 'duplicate', 'match']

    with guidance.system():
        lm = model + f"You are a teacher teaching about the course {course_title} at the level of {level}. Generate the course objectives. I will give you he topic"
    with guidance.user():
        lm += "The course objectives"
    with guidance.assistant():
        lm += chapter_title
    with guidance.assistant():
        lm += "The course objectives are: \n"
        cont = True
        for i in range(10):
            if cont:
                lm += "The student will be able to" + select(action_verbs_list, name='verbs', list_append=True) + gen(name='goal_end', list_append=True, max_tokens= 50, stop=['\n'] )
                action_verbs_list.remove(lm['verbs'][i])
        
        goals = []
        for key, goal_end in enumerate(lm['goal_end']):
            goal = "The student will be able to " + lm['verbs'][key] + goal_end
            goals.append(goal)
        
        return goals
    
courses = glob.glob("page_content/*.json")

for course in tqdm(courses):
    content = { }
    with open(course, "r", encoding="utf-8") as f:
        content = json.load(f)
    
    title = content['title']
    key = content['key']
    sections = content["sections"]

    chapters_titles = generate_chapters(title)

    chapters =  []
    for chapter_title in chapters_titles:
        chapter = {
            "title": chapter_title,
            "goals": gen_goals(title, chapter_title) 
        }
        chapters.append(chapter)
    
    new_page = {
        "title": title,
        "chapters": chapters
    }

    path = "goal_pages/v1.1/"+ title + ".json"
    if os.path.exists(path):
        os.mknod(path)
    with open(path, 'w+') as f:
        json.dump(new_page,f)

