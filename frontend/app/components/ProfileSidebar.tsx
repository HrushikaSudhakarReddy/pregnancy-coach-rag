'use client';
import { useState, useEffect } from 'react';

type StoredProfile = {
  weeks_pregnant?: number | null;
  trimester?: number | null;
  activity_level?: string | null;
  dietary_pref?: string | null;
  allergies?: string[];
  restrictions?: string[];
  conditions?: string[];
};

// helpers to convert between CSV <-> array
const toCSV = (v: unknown) =>
  Array.isArray(v) ? v.join(', ') : typeof v === 'string' ? v : '';

const toArray = (v: unknown) =>
  Array.isArray(v)
    ? v
    : typeof v === 'string'
    ? v.split(',').map(s => s.trim()).filter(Boolean)
    : [];

// shared input styles: white bg, black text, soft pink borders
const inputBase =
  'w-full rounded-xl bg-white text-slate-900 placeholder:text-slate-400 ' +
  'border border-rose-300 px-3 py-2 outline-none ' +
  'focus:border-rose-400 focus:ring-2 focus:ring-rose-400/30';

export default function ProfileSidebar() {
  // UI state uses strings for the text fields
  const [weeks, setWeeks] = useState<string>('22');
  const [trimester, setTrimester] = useState<string>('2');
  const [activity, setActivity] = useState<string>('light');
  const [diet, setDiet] = useState<string>('omnivore');
  const [allergiesText, setAllergiesText] = useState<string>('');
  const [restrictionsText, setRestrictionsText] = useState<string>('');
  const [conditionsText, setConditionsText] = useState<string>('');

  // load once from localStorage (if present), tolerate any shape
  useEffect(() => {
    try {
      const raw = localStorage.getItem('pc_profile');
      if (!raw) return;
      const p: StoredProfile = JSON.parse(raw);

      setWeeks(
        p.weeks_pregnant === null || p.weeks_pregnant === undefined
          ? ''
          : String(p.weeks_pregnant),
      );
      setTrimester(
        p.trimester === null || p.trimester === undefined
          ? ''
          : String(p.trimester),
      );
      setActivity(p.activity_level || '');
      setDiet(p.dietary_pref || '');
      setAllergiesText(toCSV(p.allergies));
      setRestrictionsText(toCSV(p.restrictions));
      setConditionsText(toCSV(p.conditions));
    } catch {
      localStorage.removeItem('pc_profile');
    }
  }, []);

  // persist as arrays in localStorage whenever inputs change
  useEffect(() => {
    const save: StoredProfile = {
      weeks_pregnant: weeks ? Number(weeks) : null,
      trimester: trimester ? Number(trimester) : null,
      activity_level: activity || null,
      dietary_pref: diet || null,
      allergies: toArray(allergiesText),
      restrictions: toArray(restrictionsText),
      conditions: toArray(conditionsText),
    };
    localStorage.setItem('pc_profile', JSON.stringify(save));
  }, [weeks, trimester, activity, diet, allergiesText, restrictionsText, conditionsText]);

  return (
    <div className="space-y-4 text-sm">
      <div>
        <label className="block text-slate-700 font-medium mb-1">Weeks pregnant</label>
        <input
          type="number"
          min={0}
          step={1}
          value={weeks}
          onChange={(e) => setWeeks(e.target.value)}
          className={inputBase}
          placeholder="e.g., 22"
        />
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Trimester</label>
        <select
          value={trimester}
          onChange={(e) => setTrimester(e.target.value)}
          className={inputBase}
        >
          <option value="">Select…</option>
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
        </select>
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Activity level</label>
        <select
          value={activity}
          onChange={(e) => setActivity(e.target.value)}
          className={inputBase}
        >
          <option value="">Select…</option>
          <option value="sedentary">Sedentary</option>
          <option value="light">Light</option>
          <option value="moderate">Moderate</option>
          <option value="vigorous">Vigorous</option>
        </select>
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Dietary preference</label>
        <select
          value={diet}
          onChange={(e) => setDiet(e.target.value)}
          className={inputBase}
        >
          <option value="">Select…</option>
          <option value="omnivore">Omnivore</option>
          <option value="vegetarian">Vegetarian</option>
          <option value="vegan">Vegan</option>
          <option value="pescatarian">Pescatarian</option>
          <option value="halal">Halal</option>
        </select>
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Allergies (comma-separated)</label>
        <input
          value={allergiesText}
          onChange={(e) => setAllergiesText(e.target.value)}
          className={inputBase}
          placeholder="e.g., peanuts, lactose"
        />
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Restrictions (comma-separated)</label>
        <input
          value={restrictionsText}
          onChange={(e) => setRestrictionsText(e.target.value)}
          className={inputBase}
          placeholder="e.g., gluten-free"
        />
      </div>

      <div>
        <label className="block text-slate-700 font-medium mb-1">Conditions (comma-separated)</label>
        <input
          value={conditionsText}
          onChange={(e) => setConditionsText(e.target.value)}
          className={inputBase}
          placeholder="e.g., heartburn, anemia"
        />
      </div>
    </div>
  );
}
