// Nimmt Tipps und Kommentare entgegen: Mail an die Redaktion, optional zusätzlich als GitHub-Issue.
// Umgebungsvariablen (Vercel):
//   SMTP_USER, SMTP_PASS   Postfach für den Versand (Hostinger, smtp.hostinger.com:465)
//   FORM_RECIPIENTS        Empfänger, kommagetrennt (Standard: office@fumbatown.agency,daniel.taborek@me.com)
//   GITHUB_TOKEN, GITHUB_REPO   optional: zusätzlich als Issue ablegen
const nodemailer = require('nodemailer');

const RECIPIENTS = process.env.FORM_RECIPIENTS || 'office@fumbatown.agency,daniel.taborek@me.com';
const REPO = process.env.GITHUB_REPO || 'danieltabstmglobal/zanzibarinsider';
const hits = new Map();

function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
}

async function sendMail(subject, text, replyTo) {
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  if (!user || !pass) return null;
  const transporter = nodemailer.createTransport({ host: 'smtp.hostinger.com', port: 465, secure: true, auth: { user, pass } });
  await transporter.sendMail({
    from: { name: 'Zanzibar Insider', address: user },
    to: RECIPIENTS.split(',').map(s => s.trim()).filter(Boolean),
    replyTo: replyTo || undefined,
    subject, text
  });
  return true;
}

async function createIssue(title, body, labels) {
  const token = process.env.GITHUB_TOKEN;
  if (!token) return null;
  const r = await fetch(`https://api.github.com/repos/${REPO}/issues`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'Content-Type': 'application/json', 'User-Agent': 'zanzibarinsider' },
    body: JSON.stringify({ title, body, labels })
  });
  return r.ok;
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

  const type = b.type === 'kommentar' ? 'kommentar' : 'tipp';
  const text = clean(b.text, 2000);
  const name = clean(b.name, 120);
  if (!text || !name) return res.status(400).json({ ok: false });
  const from = clean(b.from, 160);
  const lines = type === 'kommentar'
    ? [`Eintrag: ${clean(b.entry, 80)}`, `Name: ${name}`, '', text]
    : [`Kategorie: ${clean(b.cat, 40)}`, `Name: ${name}`, `Kontakt zum Ort: ${clean(b.contact, 200)}`, `Eingesendet von: ${from}`, '', text];
  lines.push('', `Sprache: ${clean(b.lang, 5)} · Status: ungeprüft`);
  const subject = `[Zanzibar Insider ${type}] ${name}`.slice(0, 200);
  const replyTo = (from.match(/[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+/) || [])[0];

  let mailed = null, issued = null;
  try { mailed = await sendMail(subject, lines.join('\n'), replyTo); } catch (e) { mailed = false; console.error('mail failed', e && e.code, e && e.responseCode, e && e.message); }
  try { issued = await createIssue(subject, lines.join('\n'), [type, 'ungeprueft']); } catch (e) { issued = false; console.error('issue failed', e && e.message); }
  if (mailed === null && issued === null) return res.status(503).json({ ok: false });
  return res.status(mailed || issued ? 200 : 502).json({ ok: Boolean(mailed || issued) });
};
