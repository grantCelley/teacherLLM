import guidance
from guidance import gen, select, system, user, assistant

from tqdm import tqdm

import glob
import json

MODEL = "dolphin-2.8-mistral-7b-v02.Q2_K.gguf"
model_kwargs = {"verbose": False, "n_gpu_layers": 256, "n_ctx": 30000}

model = guidance.models.LlamaCppChat(MODEL, echo=False, **model_kwargs)

def prune_to_one_sentence(goal:str) -> str:
    """
    Takes a goal string and returns it if it is more than one senance
    :param goal: the goal string
    :return: the goal as on sentace
    """
    sentance_end = goal.find('.')
    if sentance_end != -1 :
        goal = goal[:sentance_end - 1]

    return goal

def remove_duplicates(goals:list[str]) -> list[str]:
    """
    removes duplicate goals from a a chapter
    :param goals: the list to remove duplicates from
    :return: a list of goals without duplicates
    """
    seen_strings = []
    for string in goals:
        if string not in seen_strings:
            seen_strings.append(string)

    return seen_strings

def multiple_action_verbs(goal:str) -> list[str]:
    """
    checks if the goal is a multiple action verbs and makes them into multiple goals
    :param goal: the goal string
    :return: A list of goals where they are not multiple action verbs
    """
    goals_list = [goal]
    with system():
        lm = model + "You will be given a learning objective. You will tell me if it has multiple action verbs. If it is you will seperate them."
    with user():
        lm += "The student will be able to interprete and apply the basic principles of algebra, including the use of variables, equations, and inequalities."
    with assistant():
        lm += 'The objective has multiple action verbs.'
    with user():
        lm += 'Then split the objective up into independent objectives.'
    with assistant():
        lm += 'The first objective is:\nThe student will be able to interpretethe basic principles of algebra, including the use of variables, equations, and inequalities.\n The second objective is:\nThe student will be able to  apply the basic principles of algebra, including the use of variables, equations, and inequalities.'
    with user():
        lm += 'The student will be able to define and explain the two-step model of moral development.'
    with assistant():
        lm += "There is only one action verb."
    with user():
        lm += goal
    with assistant():
        lm += select(["The objective has multiple action verbs.","There is only one action verb."], name="action_verbs")
    
    if lm["action_verbs"] == "The objective has multiple action verbs.":
        with user():
            lm += "Then split the objective up into independent objectives."
        with assistant():
            lm += f"The first objective is:\n" + gen(name="first-goal", max_tokens=20, stop=['.'])  + "\n The second objective is:\n" + gen(name="second-goal", max_tokens=20, stop=["."]) 
        
        goals_list = [ lm["first-goal"], lm["second-goal"] ]

    return goals_list
    
def break_down(goal:str) -> list[str]:
    """
    DEPRECATED
    breaks down the goal into multiple goals if it is testing for more than one thing
    :param goal: the original goal string
    :return: A list of strings each with a single sentence from the original goal
    """

    new_goals_list = [goal]

    with system():
        lm = model + "You will be given a learning objective. You will tell me if it is testing for more than one thing."
    with user():
        lm += goal
    with assistant():
        lm += select(["The objective is testing for more than one thing.","The objective is not testing for more than one thing."], name="multiple_goals")
    if lm["multiple_goals"] == "The objective is not testing for more than one thing.":
        with user():
            lm += "Then split the objective up into independent objectives."
            with assistant():
                lm += "The objectives are:"
                cont = True
                max_times = 2
                while cont and max_times > 0:
                    max_times =- 1
                    lm += gen(name="new_goals", max_tokens=20, stop=[".", '\n'], list_append=True) + '\n'
                    if lm["new_goals"][-1].endswith(".") == True:
                        cont=False

                    print(lm["new_goals"])
                    new_goals_list = lm["new_goals"]
    return new_goals_list

def is_mesurable(goal:str):
    """
    checks if the goal is a mesurable goal or not
     :param goal: the original goal string
     :return: True if the goal is a measure goal, False otherwise
     """
    
    with system():
        lm = model + "You will be given a learning objective. You will tell me if it is mesurable"
    with user():
        lm += "The student will be able to define sexual orientation."
    with assistant():
        lm += "It is mesurable."
    with user():
        lm += 'The student will be able to understand the history of deep learning'
    with assistant():
        lm += "It is not mesurable."
    with user():
        lm += 'The student will be able to define and explain the following terms:'
    with assistant():
        lm += 'It is not mesurable.'
    with user():
        lm += goal
    with assistant():
        lm += select(["It is mesurable.", "It is not mesurable."], name="mesurable")
    isMesurable = True
    if lm["mesurable"] == "It is not mesurable":
        isMesurable=False
    return isMesurable

def make_sense(goal:str, course:str) -> bool:
    '''
    checks if the goal makes sense in the context of the course
    :param goal: the learning objective
    :param course: the course the goal is part of
    :return: True if the goal makes sense
    '''

    with system():
        lm = model + "You will be given a learning objective. You will tell me if it makes sense in the context of the course."
    with user():
        lm += "The student will be able to identify and describe the basic structure and function of prokaryotic and eukaryotic cells."
    with assistant():
        lm += "It makes sense."
    with user():
        lm += "The student will be able to complete the following tasks:"
    with assistant():
        lm += "It does not make sense."
    with user():
        lm += goal
    with assistant():
        lm += select(["It makes sense", "It does not make sense."], name="sense")
    is_sense= True
    if lm["sense"] == "It does not make sense":
        is_sense=False
    return is_sense

def make_specific(goal:str) -> str:
    '''
    checks if the goal is specific
     :param goal: the learning objective
     :return: the goal that is specific
    '''
    objective = goal
    with system():
        lm = model + "You will be given a learning objective. Tell me if the goal is too broad"
    with user():
        lm += "The student will be able to compare and contrast the two-step model of moral development with other"
    with assistant():
        lm += "It is too broad."
    with user():
        lm += "The student will be able to identify the different types of bacteria and their evolutionary relationships"
    with assistant():
        lm += "It is not too broad."
    with user():
        lm += goal
    with assistant():
        lm += select(["It is too broad.", "It is not too broad."], name="specific")
    if lm["specific"] == "It is too broad":
        with user():
            lm +="Rewrite the goal to be secific."
        with assistant():
            lm += gen("rewrite", stop=".")
        
        objective = lm["rewrite"]
    
    return objective
        


#THIS IS BASICALLY MAIN

unedited_goals_pages = glob.glob("goal_pages/v1.1/*.json")
print(unedited_goals_pages)
unedited_goals_pages = [unedited_goals_pages[2]]

for page in tqdm(unedited_goals_pages, "Page"):
    course = {}
    with open(page,"r") as f:
        course = json.load(f)
    
    chapters = course["chapters"]
    title = course["title"]
    refienedChapers = []
    for chapter in tqdm(chapters, title + " chapters"):
        goals = chapter["goals"]
        chapterTitle = chapter["title"]
        #makes the goals to be a single sentance
        print("Make single sentance")
        for goal in goals:
            goal = prune_to_one_sentence(goal)

        
        #removes duplicate goals
        print("Remove duplicates")
        goals = remove_duplicates(goals)
        
        #makes the goal into one action verb
        print("Get one action verb")
        new_goals_list = []
        for goal in goals:
            new_goals_list.extend(multiple_action_verbs(goal))
        goals = new_goals_list

       
       #gets ride of the goals that are not mesurable
        print("Only keeping mesureable goals")
        for goal in goals:
            if not is_mesurable(goal):
                goals.remove(goal)


        #removes the goals that don't make sense
        print("Removing nonsense goals")
        for goal in goals:
            if not make_sense(goal, title):
                goals.remove(goals)


        #make the goals specific
        print("Makes the goals specific")
        new_goals_list = []
        for goal in goals:
            new_goals_list.append(make_specific(goal))
        
        goals = new_goals_list
        
        #trims the goal
        new_goals_list = []
        for goal in goals:
            new_goals_list.append(goal.strip())
        goals = new_goals_list

        #removes duplicates again
        goals = remove_duplicates(goals)

        chapter_obj = {"title": chapterTitle, "goals":goals}
        refienedChapers.append(chapter_obj)

    with open("refiened_goals/"+ title + ".json", "w+") as f:
        page_obj = {"title": title, "chapters": refienedChapers }
        f.write(json.dumps(page_obj))
       




        
