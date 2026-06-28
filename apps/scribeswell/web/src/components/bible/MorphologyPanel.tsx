/**
 * MorphologyPanel — shows decoded morpheme breakdown for a selected word.
 */
import { X } from "lucide-react";
import type { WordWithMorphologyResponse, Morpheme } from "@/schemas/bible.schema";

interface MorphologyPanelProps {
  word: WordWithMorphologyResponse;
  onClose: () => void;
}

function capitalize(s: string | null | undefined): string {
  if (!s) return "—";
  return s.charAt(0).toUpperCase() + s.slice(1).replace(/_/g, " ");
}

export function MorphologyPanel({ word, onClose }: MorphologyPanelProps) {
  return (
    <aside
      className="bg-white border border-stone-200 rounded-xl shadow-md p-4"
      aria-label="Word morphology"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <p
            className="text-3xl font-hebrew leading-none mb-1"
            dir="rtl"
            lang="he"
            aria-label={`Hebrew word: ${word.display_he}`}
          >
            {word.display_he}
          </p>
          {word.lemma_strong && (
            <p className="text-xs text-stone-400 font-mono">
              {word.lemma_strong}
            </p>
          )}
          {word.morph_code && (
            <p className="text-xs text-stone-400 font-mono mt-0.5">
              {word.morph_code}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          className="text-stone-400 hover:text-stone-600 transition-colors ml-2 shrink-0"
          aria-label="Close morphology panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Morphemes */}
      {word.morphemes.length === 0 ? (
        <p className="text-sm text-stone-400 italic">No morphology data.</p>
      ) : (
        <div className="space-y-3">
          {word.morphemes.map((m: Morpheme) => (
            <div
              key={m.segment_index}
              className="border border-stone-100 rounded-lg p-3 bg-stone-50"
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-mono bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded">
                  {m.pos_code}
                </span>
                <span className="text-sm font-semibold text-stone-700">
                  {capitalize(m.part_of_speech)}
                </span>
                <span className="text-xs text-stone-400 capitalize">
                  {m.language}
                </span>
              </div>

              <dl className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                {m.verb_stem && (
                  <>
                    <dt className="text-stone-400">Stem</dt>
                    <dd className="text-stone-700 capitalize">
                      {capitalize(m.verb_stem)}
                    </dd>
                  </>
                )}
                {m.verb_aspect && (
                  <>
                    <dt className="text-stone-400">Aspect</dt>
                    <dd className="text-stone-700">
                      {capitalize(m.verb_aspect)}
                    </dd>
                  </>
                )}
                {m.person && (
                  <>
                    <dt className="text-stone-400">Person</dt>
                    <dd className="text-stone-700 capitalize">{m.person}</dd>
                  </>
                )}
                {m.gender && (
                  <>
                    <dt className="text-stone-400">Gender</dt>
                    <dd className="text-stone-700 capitalize">{m.gender}</dd>
                  </>
                )}
                {m.number && (
                  <>
                    <dt className="text-stone-400">Number</dt>
                    <dd className="text-stone-700 capitalize">{m.number}</dd>
                  </>
                )}
                {m.state && (
                  <>
                    <dt className="text-stone-400">State</dt>
                    <dd className="text-stone-700 capitalize">{m.state}</dd>
                  </>
                )}
              </dl>
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}
