from guidance import gen, select, system, user, assistant
import guidance

import guidance.chat
from transformers import BitsAndBytesConfig

import chromadb

import torch
import json
import glob
import tqdm

MODEL_PATH = 'Qwen/Qwen2.5-0.5B-Instruct'
quantization_cfg = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16)
model = guidance.models.Transformers(MODEL_PATH, echo=False, chat_template=guidance.chat.ChatMLTemplate, device_map="auto")
def create_sections(course:str, chapter_title:str, chapter_goals_objs, chapter_goals) -> list[dict]:
    """
    This will generate the sections
    :return
    """

    goals_str = "\n".join(chapter_goals)

    with system():
        lm = model + f"You are a teacher teaching a course on {course}. You are creating 5 lessons for the chapter on {chapter_title}.\nThe goals for chapter are:\n{goals_str}"
    with user():
        lm += "Seperate the goals into the 5 different lessons. Write all the Lesson titles."
    with assistant():
        lm += "Here are the lessons:\nFirst Lesson:" + gen(name="titles", list_append=True, max_tokens=20, stop="\n") 
        lm += "Second Lesson:" + gen(name="titles", max_tokens=20, list_append=True, stop="\n")
        lm += "Third Lesson:" + gen(name="titles", max_tokens=20, list_append=True,stop="\n") 
        lm += "Forth Lesson:" + gen(name="titles", max_tokens=20, list_append=True, stop="\n")
        lm += "Fifth Lesson:" + gen(name="titles", list_append=True, max_tokens=20, stop="\n")

    lessons = []

    for title in lm['titles']:
        lesson = {
            "title": title,
            "goals": []
        }
        lessons.append(lesson)
    
    client = chromadb.Client()
    collection = client.create_collection(name="lessons")
    ids_Keys = {
        "0":0,
        "1":1,
        "2":2,
        "3":3,
        "4":4
    }
    collection.add(
        documents=lm['titles'],
        ids=["0","1","2","3","4"]
    )

    for goal_obj in chapter_goals_objs:
        result = collection.query(query_texts=[goal_obj["goal"]], n_results=1)
        id = ids_Keys[result["ids"][0][0]]
        lessons[id]["goals"].append(goal_obj)
    
    client.delete_collection("lessons")

    for lesson in lessons:
        if not lesson["goals"]:
            lessons.remove(lesson)

    return lessons

        
def create_content(Lesson_topic, goal_objs):
    """
    This will create the course content
    :return: A list of content
    """

    question_str = ""

    for goal_obj in goal_objs:
        for question in goal_obj["questions"]:
            question_str = question_str + "\nQuestion: " + question["question"] + "\nCorrect answer: " + question["correct_ans"]

    with system():
        lm = model + f"You are a teacher that is teaching a lesson on the topic of {Lesson_topic}. The student should answer all of the questions:{question_str}\nWrite all of your content in Markdown. It should be about 1000 words."
    with user():
        lm += f"Write the Lesson: {Lesson_topic}"
    with assistant():
        lm += gen(name="lesson", max_tokens=2000, temperature=0.3)
    
    return lm["lesson"]



#THIS IS BASICLY MAIN
files = [
    'assesment_pages/Algebra.json',
    'assesment_pages/Deep learning.json',
    'assesment_pages/Microbiology.json',
    'assesment_pages/Social psychology.json'
]

for course in tqdm.tqdm(files):
    data = {}
    with open(course, 'r') as f:
        data = json.load(f)
    
    course_title = data['title']
    course_chapters = data['chapters']
    for chapter in tqdm.tqdm(course_chapters):
        chapter_goal_objs = chapter["goal_objs"]
        chapter_goals = chapter["goals"]
        chapter_title = chapter["title"]
        lessons_topics = create_sections(course_title, chapter_title, chapter_goal_objs, chapter_goals)

        lessons = []
        for topic in lessons_topics:
            content = create_content(topic["title"], topic["goals"])
            lesson = {
                "title" : topic["title"],
                "goal_objs": topic["goals"],
                "content": content
            }
            lessons.append(lesson)

        chapter["lessons"] = lessons

    with open('content_pages/' + course_title + ".json", "w+") as f:
        json.dump({
            'title': course_title,
            'chapters': course_chapters
        }, f)
