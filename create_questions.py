import guidance
from guidance import gen, select, system, user, assistant

from guidance.chat import ChatMLTemplate
import guidance.chat
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer 
from tqdm import tqdm

from tokenizers import Tokenizer
import torch
from time import sleep
import glob
import json
import os

MODEL_PATH = 'cognitivecomputations/dolphin-2.9.3-mistral-7B-32k'
quantization_config = BitsAndBytesConfig(load_in_4bit=True)

model = guidance.models.Transformers(MODEL_PATH, echo=False, chat_template=ChatMLTemplate,  quantization_config=quantization_config, device_map="auto")


def add_question(course:str, topic:str,  goal:str) -> list[str]:
    
    questions = []
    for i in range(5):
        with system():
            lm = model + f"You are a teacher teaching {course}. I will give you a learning objective and a topic. You will give a question that can be answered in a multiple choice question."
        with user():
            lm += f'Topic: {topic}\nGoal: {goal}'
        with assistant():
            lm += "Question:" + gen(name="question", temperature=0.3, stop=['?', '\n', '.'])
        
        questions.append(lm["question"])

    return questions

def remove_duplicates(unduplicatedList:list[str]) -> list[str]:
    """
    removes duplicate elements in a string
    :param unduplicatedList: the list to remove duplicates from
    :return: a list without duplicates
    """
    seen_strings = []
    for string in unduplicatedList:
        if string not in seen_strings:
            seen_strings.append(string)

    return seen_strings

def generate_correct_answer(question:str, topic:str) -> str:
    """
    Creates the correct answer for a question.
    :param question: The question to generate a correct answer
    :return: The correct answer
    """

    with system():
        lm = model + "You will be given a question you will answer it in the context of a topic. Always answer the question."
    with user():
        lm += f"Topic: {topic}\nQuestion: {question}"
    with assistant():
        lm += "Answer: " + gen(name="answer", stop=['.'])
    return lm['answer']

def generate_incorect_answers(question:str, correct_ans:str) -> list[str]:
    
    with system():
        lm = model + "You will be given a question and a correct answer. Create wrong answers."
    with user():
        lm += f"Question:{question}\nCorrect Answer:{correct_ans}"
    with assistant():
        for i in range(4):
            lm += f"Incorrect answer{i + 1}" + gen(name="incorrect answers", list_append=True, stop=['.', '\n']) + '\n'

    return lm["incorrect answers"]


#THIS IS MAIN
courses = glob.glob("refiened_goals/*.json")

print(courses)

for course in tqdm(courses, "Courses"):
    data = { }
    with open(course, 'r') as f:
        data = json.load(f)
    
    
    course_title = data['title']
    course_chapters = data['chapters']

    if (os.path.isfile("assesment_pages/"+course_title+".json") is False):

        for chapter in tqdm(course_chapters, course_title):
            chapter_title = chapter['title']
            goals = chapter['goals']
            goal_objs =[]
            for goal in goals: 
                questions = add_question(course_title, chapter_title, goal)
                questions = remove_duplicates(questions)
                question_objs = []
                for question in questions:
                    correct_ans = generate_correct_answer(question, course_title)
                    incorrect_ans = generate_incorect_answers(question, correct_ans)
                    question_objs.append({
                        "question": question,
                        "correct_ans": correct_ans,
                        "incorrect_ans": incorrect_ans
                    })
                
                goal_objs.append({
                    "goal":goal,
                    "questions": questions
                })
            
            chapter["goal_objs"] = goal_objs

        assesed_course = {"title": course_title, "chapters": course_chapters}

        with open("assesment_pages/"+ course_title + ".json", "w+") as f:
                f.write(json.dumps(assesed_course))