"""Offline reference identity and strict English/Hebrew parser. No text availability inference."""
import json
import re
import unicodedata
from pathlib import Path
CATALOGUE=json.loads((Path(__file__).resolve().parents[1]/'data/reference-catalogue/catalogue.json').read_text())
CATALOGUE_ID=CATALOGUE['catalogue_id']
CATALOGUE_VERSION=CATALOGUE['catalogue_version']
BOOKS={book['book_id']:book for book in CATALOGUE['books']}
VALUES=((400,'ת'),(300,'ש'),(200,'ר'),(100,'ק'),(90,'צ'),(80,'פ'),(70,'ע'),(60,'ס'),(50,'נ'),(40,'מ'),(30,'ל'),(20,'כ'),(10,'י'),(9,'ט'),(8,'ח'),(7,'ז'),(6,'ו'),(5,'ה'),(4,'ד'),(3,'ג'),(2,'ב'),(1,'א'))
class ReferenceError(ValueError):
 def __init__(self,code='reference_invalid',choices=()):self.code=code;self.choices=choices;super().__init__(code)

def normalize(value):
 value=unicodedata.normalize('NFC',value)
 value=re.sub('[\u0591-\u05BD\u05BF\u05C1-\u05C2\u05C4-\u05C5\u05C7]','',value)
 return re.sub(r'\s+',' ',value.casefold().strip())
ALIASES={}
for book in BOOKS.values():
 for alias in book['aliases']:ALIASES.setdefault(normalize(alias).replace('.',''),set()).add(book['book_id'])

def hebrew_number(number):
 result=''
 for value,letter in VALUES:
  while number>=value:
   if number in (15,16):return result+('טו' if number==15 else 'טז')
   result+=letter;number-=value
 return result

def number(value):
 if re.fullmatch('[1-9][0-9]*',value):return int(value)
 plain=re.sub('[\u05F3\u05F4\'"]','',value)
 if not plain or any(c not in dict((letter,n) for n,letter in VALUES) for c in plain):raise ReferenceError()
 result=sum(dict((letter,n) for n,letter in VALUES)[c] for c in plain)
 if result>999 or hebrew_number(result)!=plain:raise ReferenceError()
 # Optional punctuation occurs after the sole letter or before the final letter.
 if value not in (plain,plain+'׳' if len(plain)==1 else plain[:-1]+'״'+plain[-1],plain+"'" if len(plain)==1 else plain[:-1]+'"'+plain[-1]):raise ReferenceError()
 return result

def validate_reference(value):
 if type(value) is not dict or set(value)!= {'catalogue_id','catalogue_version','versification_id','book_id','target'}:raise ReferenceError()
 book=BOOKS.get(value['book_id']) if type(value['book_id']) is str else None
 if not book or value['catalogue_id']!=CATALOGUE_ID or value['catalogue_version']!=CATALOGUE_VERSION or value['versification_id']!=book['versification_id']:raise ReferenceError('reference_version_invalid')
 target=value['target']
 if type(target) is not dict:raise ReferenceError()
 def chapter(c):return type(c) is int and 1<=c<=len(book['chapter_verse_counts'])
 def point(p):return type(p) is dict and set(p)=={'chapter','verse'} and chapter(p['chapter']) and type(p['verse']) is int and 1<=p['verse']<=book['chapter_verse_counts'][p['chapter']-1]
 if target.get('kind')=='chapter':valid=set(target)=={'kind','chapter'} and chapter(target['chapter'])
 else:valid=set(target)=={'kind','start','end'} and target.get('kind')=='verse_range' and point(target['start']) and point(target['end']) and (target['start']['chapter'],target['start']['verse'])<=(target['end']['chapter'],target['end']['verse'])
 if not valid:raise ReferenceError()
 return value

def make_reference(book_id,target):
 book=BOOKS.get(book_id)
 if not book:raise ReferenceError()
 return validate_reference({'catalogue_id':CATALOGUE_ID,'catalogue_version':CATALOGUE_VERSION,'versification_id':book['versification_id'],'book_id':book_id,'target':target})

def parse_reference(text):
 if type(text) is not str or len(text)>300:raise ReferenceError()
 text=normalize(text);matches=[]
 for alias,ids in ALIASES.items():
  pattern=''.join(r'\s+' if char==' ' else re.escape(char)+r'\.*' for char in alias)
  match=re.match(pattern,text)
  if match and text[match.end():].strip():matches.append((len(alias),ids,text[match.end():].strip()))
 if not matches:raise ReferenceError('reference_unknown_book')
 _,ids,tail=max(matches,key=lambda match:match[0])
 if len(ids)!=1:raise ReferenceError('reference_ambiguous',tuple(sorted(ids)))
 book_id=next(iter(ids));parts=re.split(r'\s*[-–—]\s*',tail)
 if len(parts)>2:raise ReferenceError()
 start=[number(n.strip()) for n in parts[0].split(':')]
 if len(start)==1 and len(parts)==1:return make_reference(book_id,{'kind':'chapter','chapter':start[0]})
 if len(start)!=2:raise ReferenceError()
 end=[number(n.strip()) for n in parts[1].split(':')] if len(parts)==2 else start
 if len(end)==1:end=[start[0],end[0]]
 if len(end)!=2:raise ReferenceError()
 return make_reference(book_id,{'kind':'verse_range','start':dict(zip(('chapter','verse'),start)),'end':dict(zip(('chapter','verse'),end))})

from typing import Annotated, Literal, Union
from pydantic import BaseModel, ConfigDict, Field, model_validator
class ReferenceModel(BaseModel):
 model_config=ConfigDict(extra='forbid',strict=True,frozen=True,hide_input_in_errors=True)
class ReferencePoint(ReferenceModel):
 chapter:Annotated[int,Field(ge=1,le=150)]
 verse:Annotated[int,Field(ge=1,le=176)]
class ChapterTarget(ReferenceModel):
 kind:Literal['chapter']
 chapter:Annotated[int,Field(ge=1,le=150)]
class RangeTarget(ReferenceModel):
 kind:Literal['verse_range']
 start:ReferencePoint
 end:ReferencePoint
class PassageReference(ReferenceModel):
 catalogue_id:Literal['scribeswell.references.v1']
 catalogue_version:Literal[CATALOGUE_VERSION]
 versification_id:Literal['oshb-hebrew-json-c2d8e9e5','crosswire-kjv-3765']
 book_id:Annotated[str,Field(min_length=1,max_length=8)]
 target:Annotated[Union[ChapterTarget,RangeTarget],Field(discriminator='kind')]
 @model_validator(mode='after')
 def valid_reference(self):
  validate_reference(self.model_dump(mode='json'));return self
