import guidance
from guidance import gen, select

import os

import json
import glob


MODEL = "dolphin-2.8-mistral-7b-v02.Q2_K.gguf"
model_kwargs = {"verbose": False, "n_gpu_layers": 256, "n_ctx": 30000}

model = guidance.models.LlamaCppChat(MODEL, echo=False, **model_kwargs)



def generate_topics(course_name: str, summary: str):
    """
    This will generate topics for a course
    :param course_name: Name of the course to generate the topics for
    :param summary: Summary from wikipedia about the overall topic
    :returns: List[str] List of the topics
    """

    schema = {
        "type": "object",
        "properties": {
            "topics": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A topic"
            }
            }
        },
        "required": [
            "topics"
        ]
        }

    system_prompt = f"You are a professor creating a course for {course_name}. I will give you a wikipedia summary. Generate the topics for the course. Output JSON in the following schema {schema}"
    user_prompt = summary

    topics = None
    while topics == None:
        with guidance.system():
            lm = model + system_prompt
        with guidance.user():
            lm = lm + user_prompt
        with guidance.assistant():
            lm = lm + f"""{{
            "topics":[ """
            for i in range(10):
                lm += "\"" + gen("topics", list_append=True, max_tokens=10, stop='"') +  "\""
                if i < 9:
                    lm += ",\n"

        topics = lm['topics']

    return topics

def is_section_Important(course_name: str, section:str, topic_list: list[str]):
    """ 
    This will check if the course is important based on the given course name and the given topic list
    :param course_name: Name of the course to generate the topics for
    :param summary: Summary from wikipedia about the overall topic
    :returns: List[str] List of the topics
    """

    topic_list.append("None")
    topic_str = '\n* '.join(topic_list)
    topic_str = '\n* ' + topic_str

    system_prompt = f"You are a professor creating a course for {course_name}. I will give you a wikipedia section and a list of topics. Tell me if the section would be part of any of the topics. If the section does not fall into any of the topics just type 'None'. The topics are:\n{topic_str}"

    user_prompt = f"Wikipedia Section:\n{section}\n\n Topics:{topic_str}\nWhat topic is would the selection be part of? Just classify it."

    topic = None
    with guidance.system():
        lm = model + system_prompt
    with guidance.user():
        lm += user_prompt
    with guidance.assistant():
        lm += select(topic_list, 'topic')
    
    topic = lm['topic']
    print(topic)
    if topic == "None":
        return False, 
    else:
        return True
    
    
def generate_Objectives(title, section):
    """ 
    This will generate learning objectives
    :param: title: The title of the course
    :param: section: A section of wikipedia
    :return: A list of learning objectives for a course
    """ 

    schema = {
        "description": "The goals object",
        "type": "object",
        "properties": {
            "goals": {
            "type": "array",
            "items": {
                "type": "string",
                "description": "A learning objective"
            }
            }
        },
        "required": [
            "goals"
        ]
    }

    action_verbs_list = ["implement", 'design' , 'construct', 'develop', 'produce', 'revise', 'propose', 'build', 'devise', 'invent', 'judge', 'justify', 'select', 'critique', 'defend', 'rate', 'evaluate', 'assess', 'rank', 'argue', 'review', 'distinguish', 'differentiate', 'orginize', 'examine', 'compare', 'contrast', 'classify', 'apply', 'use', 'solve', 'compute', 'implement', 'instruct', 'demonstrate', 'interpret', 'complete', 'explain', 'demonstrate', 'summarize', 'review', 'generalize', 'describe', 'identify', 'represent', 'paraphrase', 'interpret', 'define', 'identify', 'recall', 'recite', 'reproduce', 'list', 'name', 'memorize', 'repeat', 'state', 'duplicate', 'match']

    system = f"You are a teacher creating the course objectives for {title}. I will give you a wikipedia section and you will generate course objectives. The output is in JSON. The schema is {schema}"
    
    numberOfGoals = 5

    with guidance.system():
        lm = model + system
    with guidance.user():
        lm += section
    with guidance.assistant():
        lm + """{
        goals: ["""

        for i in range(numberOfGoals):
            lm += '"The student will be able to' + select(action_verbs_list, "goal_actions", list_append=True) + gen('end_goals', list_append=True, max_tokens=50, stop=['"', '.',]) + '"'
            if i < numberOfGoals - 1:
                lm += ",\n"
            
        goals = []
        for i in range(numberOfGoals):
            goal = "The student will be able to " + lm['goal_actions'][i] + "" + lm['end_goals'][i]
            goals.append(goal)

    return goals

   

pages_file_names = glob.glob("./page_content/*.json")


print(pages_file_names)

for file_name in pages_file_names:
    page_content = {}
    with open(file_name, 'r') as f:
        page_content = json.loads(f.read())
    
    title = page_content["title"]
    key = page_content['key']
    goal_sections = []
    sections = page_content['sections']

    page_topics = generate_topics(course_name=title, summary=sections[0]['content'])
    print(sections[0]['content'])
    print("Topics generated: ")
    print(page_topics)

    relevant_sections = []
    for section in sections[1:]:
        content = section['content']
        print(section['title'])
        name = section['title']
        if name != " References " and name != " See also " and name != " Sources " and name != " Citations " and name != " Notes " and name != " External links ": 
            relevant = is_section_Important(title, content, page_topics)
            print(relevant)
            if relevant == True:
                relevant_sections.append(section)
    final_sections = []
    for section in relevant_sections:
        content = section['content']
        section_title = section['title']
        section['goals'] = generate_Objectives(title, content)
        print(section_title)
        print(section['goals'])
        final_sections.append(section)
    
    new_page_content ={
        "title": title,
        "key": key,
        "summary": sections[0]['content'],
        "sections": final_sections
    }

    file_path = "goal_pages/v1/" + title + ".json"
    if not os.path.exists(file_path):
        os.mknod(file_path)
    with open(file_path,"w") as f:
        json.dump(new_page_content,f)