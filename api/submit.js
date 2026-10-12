// Nimmt Tipps und Kommentare entgegen und legt sie als GitHub-Issue zur redaktionellen Prüfung ab.
// Umgebungsvariablen (Vercel): GITHUB_TOKEN (Fine-grained, nur Issues: write), optional GITHUB_REPO.
const REPO = process.env.GITHUB_REPO || 'danieltabstmglobal/zanzibarinsider';
const hits = new Map();

function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ ok: false });
  const origin = req.headers.origin || '';
  if (origin && !/^https:\/\/(www\.)?zanzibarinsider\.com$|\.vercel\.app$/.test(origin)) return res.status(403).json({ ok: false });
  const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  if (b.website) return res.status(200).json({ ok: true }); // Honeypot
  if (Number(b.elapsed) < 2500) return res.status(400).json({ ok: false });
  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0] || 'x';
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter(t => now - t < 10 * 60 * 1000);
  if (recent.length >= 5) return res.status(429).json({ ok: false });
  hits.set(ip, recent.concat(now));
  const token = process.env.GITHUB_TOKEN;
  if (!token) return res.status(503).json({ ok: false });

  const type = b.type === 'kommentar' ? 'kommentar' : 'tipp';
  const text = clean(b.text, 2000);
  const name = clean(b.name, 120);
  if (!text || !name) return res.status(400).json({ ok: false });
  const lines = type === 'kommentar'
    ? [`**Eintrag:** ${clean(b.entry, 80)}`, `**Name:** ${name}`, '', text]
    : [`**Kategorie:** ${clean(b.cat, 40)}`, `**Name:** ${name}`, `**Kontakt zum Ort:** ${clean(b.contact, 200)}`,
       `**Eingesendet von:** ${clean(b.from, 160)}`, '', text];
  lines.push('', `_Sprache: ${clean(b.lang, 5)} · Status: ungeprüft_`);
  const r = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'zanzibarinsider' },
    body: JSON.stringify({ title: `[${type}] ${name}`.slice(0, 200), body: lines.join('\n'), labels: [type, 'ungeprueft'] })
  });
  return res.status(r.ok ? 200 : 502).json({ ok: r.ok });
};
