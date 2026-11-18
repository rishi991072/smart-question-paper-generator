"""Offline template-based question generation. No LLM/API key/internet."""
import re, random
from collections import Counter
STOP=set('a an the and or but if then than of in on at to for from by with as is are was were be been being this that these those it its into about over under after before during between through can could should would may might will shall do does did have has had not no we you they them their our your which what when where who why how also such using used use based called known many most more less very each other another some any all both one two three first second new'.split())
def sentences_from(text):
    text=re.sub(r'\s+',' ',text)
    return [s.strip(' -•\t') for s in re.split(r'(?<=[.!?])\s+|\n+',text) if len(s.split())>=7 and len(s)<550]
def keywords(sentence):
    words=re.findall(r'[A-Za-z][A-Za-z0-9_-]{3,}',sentence)
    return [w for w,_ in Counter(w for w in words if w.lower() not in STOP).most_common(8)]
def difficulty_for(sentence):
    n=len(sentence.split())
    return 'easy' if n<15 else 'medium' if n<24 else 'hard' if n<34 else 'extreme'
def generate_from_text(source,subject,count,difficulty,language):
    sentences=sentences_from(source); vocab=list(dict.fromkeys(t for s in sentences for t in keywords(s)))
    questions=[];seen=set()
    for i,s in enumerate(sentences):
        terms=keywords(s)
        if not terms:continue
        term=terms[0]; level=difficulty_for(s)
        m=re.search(r'\[PAGE (\d+)\]',s); page=int(m.group(1)) if m else 1
        clean=re.sub(r'\[PAGE \d+\]','',s).strip()
        for prompt in [f'Explain the concept of {term} based on the study material.',f'Describe the role or importance of {term}.',f'Write a short note on {term}.']:
            if prompt.lower() not in seen:
                seen.add(prompt.lower());questions.append({'question':prompt,'type':'descriptive','options':[],'correct_answer':clean,'explanation':'Answer derived from uploaded study material.','difficulty':level,'topic':term,'unit':term,'source_pages':[page]})
        if len(clean)>35 and re.search(re.escape(term),clean,re.I):
            blank=re.sub(re.escape(term),'________',clean,count=1,flags=re.I)
            distractors=[x for x in vocab if x.lower()!=term.lower() and x.lower() not in clean.lower()]
            opts=[term]+distractors[:3]
            while len(opts)<4:opts.append(f'Option {len(opts)+1}')
            random.Random(i+17).shuffle(opts)
            q='Choose the term that correctly completes the statement: '+blank
            if q.lower() not in seen:
                seen.add(q.lower());questions.append({'question':q,'type':'mcq','options':opts,'correct_answer':next((chr(65+j)+'. '+o for j,o in enumerate(opts) if o.lower()==term.lower()),term),'explanation':clean,'difficulty':level,'topic':term,'unit':term,'source_pages':[page]})
        if len(questions)>=max(count*4,40):break
    for term in vocab:
        q=f'Define {term} and give one relevant example.'
        if q.lower() not in seen:
            seen.add(q.lower());questions.append({'question':q,'type':'descriptive','options':[],'correct_answer':'Refer to the explanation of this term in the uploaded study material.','explanation':'Verify the expected answer against the source PDF.','difficulty':'easy','topic':term,'unit':term,'source_pages':[]})
        if len(questions)>=max(count*5,60):break
    return questions
