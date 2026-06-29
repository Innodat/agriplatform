/**
 * hebrew-ordinal.ts — convert a positive integer to a Hebrew gematria string.
 *
 * Covers 1–150 (all chapter counts in the Tanakh; max is Psalms 150).
 * Standard gematria rules:
 *   - 15 → טו  (not יה to avoid a divine name)
 *   - 16 → טז  (not יו)
 *
 * No external dependencies.
 */

// Values in descending order for the greedy algorithm.
const GEMATRIA_VALUES: [number, string][] = [
  [400, "ת"],
  [300, "ש"],
  [200, "ר"],
  [100, "ק"],
  [90,  "צ"],
  [80,  "פ"],
  [70,  "ע"],
  [60,  "ס"],
  [50,  "נ"],
  [40,  "מ"],
  [30,  "ל"],
  [20,  "כ"],
  [10,  "י"],
  [9,   "ט"],
  [8,   "ח"],
  [7,   "ז"],
  [6,   "ו"],
  [5,   "ה"],
  [4,   "ד"],
  [3,   "ג"],
  [2,   "ב"],
  [1,   "א"],
];

/**
 * Converts a positive integer (1–999) to its Hebrew gematria representation.
 *
 * @param n - A positive integer. Must be ≥ 1.
 * @returns The Hebrew gematria string (e.g. 1 → "א", 22 → "כב", 150 → "קנ").
 */
export function toHebrewOrdinal(n: number): string {
  if (n <= 0 || !Number.isInteger(n)) {
    throw new RangeError(`toHebrewOrdinal expects a positive integer, got ${n}`);
  }

  // Special cases to avoid spelling divine names
  if (n === 15) return "טו";
  if (n === 16) return "טז";

  let remaining = n;
  let result = "";

  for (const [value, letter] of GEMATRIA_VALUES) {
    while (remaining >= value) {
      result += letter;
      remaining -= value;
    }
  }

  return result;
}
