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

#this is main
no_question_goals = glob.glob("refiened_goals/*.json")

print(no_question_goals)