from llama_cpp import Llama

import json
import glob


MODEL = "dolphin-2.8-mistral-7b-v02.Q2_K.gguf"

model = Llama(MODEL, n_ctx=13000, n_gpu_layers=100, verbose=False)


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
        response = model.create_chat_completion(
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_prompt
                }
            ],
            response_format={
                "type": "json_object",
                "schema": schema
            },
            temperature=0.7
        )["choices"][0]["message"]["content"]
        print(response)
        try:
            obj = json.loads(response)
        except Exception as e:
            obj = {}
        print(obj)
        if "topics" in obj:
            topics = obj["topics"]

    return topics

def is_section_Important(course_name: str, section:str, topic_list: list[str]):
    """ 
    This will check if the course is important based on the given course name and the given topic list
    :param course_name: Name of the course to generate the topics for
    :param summary: Summary from wikipedia about the overall topic
    :returns: List[str] List of the topics
    """ 

    schema ={
        "description": "The schema to get a topic out",
        "type": "object",
        "properties": {
            "topic": {
            "type": "string"
            }
        },
        "required": [
            "topic"
        ]
    }

    topic_list.append("None")
    topic_str = '\n* '.join(topic_list)
    topic_str = '\n* ' + topic_str

    topic_examples = ""
    for topic in topic_list:
        topic_obj = {
            "topic": topic
            }
        
        topic_one = "{topic_obj}\n"

        topic_examples += topic_one

    system_prompt = f"You are a professor creating a course for {course_name}. I will give you a wikipedia section and a list of topics. Tell me if the section would be part of any of the topics. If the section does not fall into any of the topics just type 'None'. The topics are:\n{topic_str}\n The output is in JSON in the following schema of {schema}. Possible topics are {topic_list}"

    user_prompt = f"Wikipedia Section:\n{section}\n\n Topics:{topic_str}\nWhat topic is would the selection be part of? Just classify it."

    topic = None

    i = 5
    while topic is None and i > 0:
        response = model.create_chat_completion(
            messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role':  'user',
                'content': user_prompt
            }
        ],
        response_format={
            "type": "json_object",
            "schema": schema
        }
        )["choices"][0]["message"]["content"]

        try:
            obj = json.loads(response)
        except Exception as e:
            obj = {}
        if "topic" in obj:
            if type(obj["topic"]) is str and obj["topic"] in topic_list:
                topic = obj["topic"]
        i -= 1
        if i == 0 and obj == {}:
            topic = "None"
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

    system = f"You are a teacher creating the course objectives for {title}. I will give you a wikipedia section and you will generate course objectives.The output is JSON in the schema of {schema}"
    
    goals = []
    while len(goals ) == 0:
        print("Generating goals")
        response = model.create_chat_completion(
            messages=[
            {
                'role':'system',
                'content': system
            },
            {
                'role':  'user',
                'content': section
            }
        ],
        response_format={
            "type": "json_object",
            "schema":schema
        }
        )["choices"][0]["message"]["content"]
        print(response)
        print("goals generated")
        try:
            obj = json.loads(response)
        except Exception as e:
            obj = {}
        if "goals" in obj:
            goals = obj["goals"]
        else:
            print("Have to try again")
        

    return goals

   

pages_file_names = glob.glob("./page_content/*.json")
pages_file_names = [pages_file_names[0]]
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