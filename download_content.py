from wiki_page import get_page, create_sections
import json
import glob
import os

all_pages = glob.glob("revised_page_names/*.json")



for page in all_pages:
    key = ""
    with open(page, "r", encoding="utf-8") as f:
        data_raw = f.read()
        data = json.loads(data_raw)
        key = data['pages'][0]
    _page = get_page(key)
    sections = create_sections(_page['source'])
    _page['sections'] = sections

    fileName = "page_content/" + _page['title'] + ".json"

    if not os.path.exists(fileName):
        os.mknod(fileName)
    
    with open(fileName, 'w') as f:
        json.dump(_page, f)