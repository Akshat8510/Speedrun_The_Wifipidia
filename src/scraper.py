# src/scraper.py
import wikipediaapi

def get_wiki_agent():
    return wikipediaapi.Wikipedia(
        user_agent='SpeedrunBot/MediumProject (educational)',
        language='en'
    )

def resolve_redirect(wiki_obj, title):
    page = wiki_obj.page(title)
    if page.exists():
        return page.title
    return title

def get_valid_links(page_obj):
    links = []
    try:
        if not page_obj.exists(): return []
        for title in page_obj.links.keys():
            if ":" not in title:
                links.append(title)
    except:
        pass
    return links