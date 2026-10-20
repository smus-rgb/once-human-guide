// Zdroj průvodce: API (/guide, případně s Google Drive overlayem), jinak
// bundlovaná kopie kanonického guide.json — jedna pravda o datech zůstává v repu.
import bundled from './data/guide.json';

const API = process.env.EXPO_PUBLIC_API_URL || '';

export function localGuide() {
  return bundled;
}

export async function loadGuide() {
  if (API) {
    try {
      const res = await fetch(`${API}/guide`);
      if (res.ok) {
        const doc = await res.json();
        if (doc && doc.paths) {
          return { doc, source: (doc.meta && doc.meta.source) || 'drive' };
        }
      }
    } catch (e) {
      // offline nebo API neběží → bundlovaná kopie
    }
  }
  return { doc: bundled, source: 'local' };
}

export function norm(value) {
  return String(value == null ? '' : value).toLowerCase();
}

function haystack(o) {
  return norm([
    o.title,
    o.name,
    o.goal,
    o.why,
    o.summary,
    o.q,
    o.a,
    o.term,
    o.definition,
    (o.keywords || []).join(' '),
  ].join(' '));
}

// Stejná logika jako v shellu: název, cíl, proč, popis a klíčová slova.
export function hit(o, query) {
  return haystack(o).includes(norm(query).trim());
}

export function allSteps(doc) {
  const out = [];
  ((doc && doc.paths) || []).forEach((p) => {
    (p.steps || []).forEach((s) => out.push({ ...s, _path: p.id, _pathTitle: p.title }));
  });
  return out;
}

export function searchGuide(doc, query) {
  if (!norm(query).trim()) return { steps: [], faq: [], glossary: [] };
  return {
    steps: allSteps(doc).filter((s) => hit(s, query)),
    faq: ((doc && doc.faq) || []).filter((f) => hit(f, query)),
    glossary: ((doc && doc.glossary) || []).filter((g) => hit(g, query)),
  };
}
