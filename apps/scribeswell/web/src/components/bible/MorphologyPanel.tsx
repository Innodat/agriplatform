/** Readable morphology, with surface pieces only when source boundaries align. */
import type { WordWithMorphologyResponse } from '@/schemas/bible.schema';

function readable(value:string|null|undefined) {return value?.replace(/_/g,' ')??'';}
function title(value:string) {return value.charAt(0).toUpperCase()+value.slice(1);}

export function MorphologyPanel({word}: {word:WordWithMorphologyResponse}) {
  const parts=word.surface_he.split('/');
  const codes=word.morph_code?.replace(/^[HA]/,'').split('/')??[];
  const aligned=parts.length===word.morphemes.length&&codes.length===parts.length&&parts.every(Boolean)&&word.morphemes.every((m,i)=>m.segment_index===i&&m.pos_code===codes[i]);
  return <aside aria-label="Word morphology" className="text-sm border-y border-stone-200 py-2 my-3">
    {word.morphemes.length===0?<p className="text-stone-500">No morphology data.</p>:<ol className="space-y-2">
      {word.morphemes.map(m=>{
        const aspect=m.verb_aspect==='participle_active'?'active participle':m.verb_aspect==='participle_passive'?'passive participle':readable(m.verb_aspect);
        const heading=title([readable(m.verb_stem),aspect].filter(Boolean).join(' ')||readable(m.part_of_speech));
        const features=[m.person?`${m.person} person`:null,m.gender,m.number,m.state].filter(Boolean).map(readable).join(' · ');
        return <li key={m.segment_index} className="flex flex-wrap items-baseline gap-x-2 min-w-0">
          {aligned&&<bdi lang={m.language.toLowerCase()==='aramaic'?'arc':'he'} dir="rtl" className="font-hebrew text-xl">{parts[m.segment_index]}</bdi>}
          <span className="font-medium">{heading}</span>{features&&<span className="text-stone-600">{features}</span>}
        </li>;
      })}
    </ol>}
  </aside>;
}
