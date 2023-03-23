import bs4
from bs4 import BeautifulSoup
from pathlib import Path
import glob
import json

def parse_contact(soup, verbose=False):
    _dcont = {}
    for _i in soup.select('div[class=person-section-contact] > div > div[class="person-contact-box"]'):
        try:
            _t = " ".join([_j.capitalize() for _j in _i.select('h3')[0].text.split()])
        except:
            # One case skips the h3 tags, no contact subsections
            _t = "Primary"

        _dcont[_t] = []
        for _j in _i.select('p'):
            try:
                _href = _j.select('a')[0]['href']
            except:
                _href = None

            try: 
                _dcont[_t].append({
                    'type': _j['class'][0],
                    'val': _j.text,
                    'href': _href
                })
            except:
                continue
    
    _contact = {}
    for _i in _dcont.keys():
        if verbose: print("\tContact:", _i, '\n')
        _contact[_i] = {}
        for _j in _dcont[_i]:
            _t = _j['type']
            _v = _j['val']
            _l = _j['href']
            if _l is not None and 'website' in _v:
                _v = _l
            if verbose: print(f"\t\t{_t.capitalize()}\t{_v}")
            _contact[_i][_t] = _v 
        if verbose: print()
            
    return _contact

def parse_paragraph_content(soup, verbose=False):
    _tagdict = {}
    try:
        _tagdict['Quote'] = soup.select('div[class=person-section-body]')[0].select('div > p[class=quote]')[0].text.strip()
        if verbose: print(f"\t{briefp}\n")
    except:
        if verbose: print("\tERROR: NO PARAGRAPH QUOTE FOUND\n")
    _stmp = soup.select('div[class=person-section-body]')[0].select('div[class=paragraph-content-textcolumn]')
    _last = ""
    for _s in _stmp[0]:
        if type(_s) is bs4.element.Tag:
            if _s.name == 'h3':
                _last = _s.text
                _tagdict[_s.text] = []
                if verbose: print(f"{_s.text}")
            elif _s.name == 'p':
                _tagdict[_last] = _s.text
                if verbose: print(f"\t{_s.text}")
    return _tagdict

def parse_publication_link(soup, verbose = False):
    _subs = soup.select('div[class=person-section-body]')[0]
    _publink = ""
    for _link in _subs.find_all('a', href=True):
        if 'list of publications' in _link.text:
            if verbose: print(_link['href'])
            _publink = _link['href']
    return _publink
        
def parse_person_page(fn="people/faculty/matthew-vander-heiden.html", verbose=False):
    _entry = {}
    soup = BeautifulSoup(Path(fn).read_text(), 'html.parser')
    try:
        _entry['Name'] = soup.select('title')[0].text.split('|')[0].strip()
        _entry['Affiliation'] = soup.select('title')[0].text.split('|')[1].strip()
        if verbose: print(f"{_name}, {_inst}")
    except:
        if verbose: print("\tERROR: NO TITLE FOUND")
    _entry['Titles'] = []
    for _i in soup.select('div[class=person-titles] > p'):
        if verbose: print(f"\t- {_i.text}")
        _entry['Titles'].append(_i.text)
    if verbose: print()
    _entry['Info'] = parse_paragraph_content(soup, verbose=verbose)
    _entry['Contact'] = parse_contact(soup, verbose=verbose)
    _hp = 'ki.mit.edu'
    _entry['Profile'] = "https://" + _hp + str(fn).split(_hp)[1].split('.')[0]
    _entry['PubMed'] = parse_publication_link(soup, verbose=verbose)
    return soup, _entry
    
def parse_all_people_in(fp='people/faculty', verbose=False):
    soups = {}
    cards = {}
    _p = Path(fp).absolute()
    for _i in _p.glob("*.html"):
        soups[_i.name], cards[_i.name] = parse_person_page(_i)
        if verbose: print()
    return soups, cards

def pull_faculty(fp='/mnt/data/www/ki.mit.edu/people/faculty', verbose=False):
    soups, cards = parse_all_people_in(fp=fp, verbose=verbose)
    if verbose:
        print('Faculty','\n')
        for _k in soups.keys():
            print(f"\t- {_k}")
        print()
    faculty_info = {}
    for _k, _v in cards.items():
        faculty_info[_v['Name']] = _v
    return faculty_info

def pull_clinical_investigators_and_research_fellows(
        fp='/mnt/data/www/ki.mit.edu/people/clinical-investigators-research-fellows', 
        verbose=False):
    soups, cards = parse_all_people_in(fp=fp, verbose=verbose)
    if verbose:
        print('Clinical Investigators and Research Fellows','\n')
        for _k in soups.keys():
            print(f"\t- {_k}")
        print()
    faculty_info = {}
    for _k, _v in cards.items():
        faculty_info[_v['Name']] = _v
    return faculty_info

def pull_leadership(fp='/mnt/data/www/ki.mit.edu/people/leadership', verbose=False):
    soups, cards = parse_all_people_in(fp=fp, verbose=verbose)
    if verbose:
        print('Leadership','\n')
        for _k in soups.keys():
            print(f"\t- {_k}")
        print()
    faculty_info = {}
    for _k, _v in cards.items():
        faculty_info[_v['Name']] = _v
    return faculty_info

def pull_all(verbose=False):
    faculty = pull_faculty()
    clinical_investigators_and_research_fellows = pull_clinical_investigators_and_research_fellows()
    leadership = pull_leadership()
    return leadership | faculty | clinical_investigators_and_research_fellows

def print_dict(d, indent=4):
    print(json.dumps(d, indent=indent))


def write_dict(d, fn, indent=4):
    with open(fn, 'w', encoding ='utf8') as _f:
        json.dump(d, _f, ensure_ascii = False, indent=2)
