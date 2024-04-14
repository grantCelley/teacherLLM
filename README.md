# Teacher LLM
---
Teacher LLM is a project to try and use [LLMs](https://en.wikipedia.org/wiki/Large_language_model) to generate courses.

This project follows the Understanding by design patterns from [This text book](https://en.wikipedia.org/wiki/Understanding_by_Design).

 There are several scopes for teacher LLM:

1. Generate the course by being grounded with wikipedia. Mostly for the summary of the matrial to generate the learning objectives.
2. Generate possible assesments
3. Generate the material.
4. Be undergraduate level material.

Out of scope for the project:

1. Fine tuning. If I do this it will be for a more profesional enviroment.
2. Anything other than terminal. I will use the insights from this project to make a professional product.(hopefully still opensource)

## Install
First create a virtual environment

```bash
virtualenv -p python3 venv
```

And activate it

```bash
source venv/bin/activate
```

We need to install a few packages

```bash
pip install wikipedia-api wikitextparser guidance
```

Also [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) needs to be installed

Also the [model](https://huggingface.co/dagbs/dolphin-2.8-mistral-7b-v02-GGUF) needs to be saved in this directory. It uses the Q3_K_M variant.
## TODO: I need to write how the files work