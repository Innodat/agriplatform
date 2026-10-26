[
  {
    "location": "apps/scribeswell/web/src/hooks/useReaderWorkspace.ts:443-444",
    "trigger_condition": "Multiple staged victims share a dirty note, and final installation removes every context.",
    "guard_snippet": "guardDeparturesAgainstFinalSurvivors(candidate.union, victims, () => finishDevice(union, candidate.active));",
    "potential_consequence": "Each departure sees another live context; installation removes all without confirming unsaved input."
  },
  {
    "location": "apps/scribeswell/web/src/hooks/useReaderWorkspace.ts:443-444",
    "trigger_condition": "A dirty victim is confirmed before capacity fits, then restoration is canceled.",
    "guard_snippet": "stageVictim(key); /* Defer destructive departure handling until final installation. */",
    "potential_consequence": "Cancel retains the tab after departure handling has discarded its unsaved input."
  },
  {
    "location": "apps/scribeswell/web/src/context/StudiesContext.tsx:87-104",
    "trigger_condition": "A requested study or note returns HTTP 200 with a null payload.",
    "guard_snippet": "if ((candidate.study && !selected) || (candidate.note && !note)) throw new NotesFailure('response_invalid');",
    "potential_consequence": "Missing resources pass validation, exposing remembered labels or erasing remembered note selections."
  },
  {
    "location": "apps/scribeswell/web/src/context/StudiesContext.tsx:131-138",
    "trigger_condition": "Delayed results cannot replace current work.",
    "guard_snippet": "if (affected || pending) fields.set('current', null); /* pending matches remembered metadata despite newer selections. */",
    "potential_consequence": "A delayed old-resource denial clears a newer unrelated selection and its label.",
    "kind": "claim",
    "confidence": "high"
  }
]