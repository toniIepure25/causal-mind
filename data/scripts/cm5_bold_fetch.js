// CM-5 sealed-cohort BOLD acquisition (113 subjects).
//
// HARD GUARD: requested dataset path must equal the resolved S3 URL path AND
// the resolved size must equal the annex-key size. Mismatch => SKIP, never
// download (regression guard for the documented OpenNeuro API anomaly).
//
// - Resumable/idempotent: existing file with matching size+hash is skipped.
// - Crash-safe: writes to .part, renames on completion.
// - Token-expiry safe: on 401/403 stops cleanly (no partial files kept);
//   re-running resumes where it left off.
// - Concurrency pool (default 4).
//
// Usage: node cm5_bold_fetch.js [--pool=N] [--limit=N]
const { configuredClient } = require('@openneuro/cli/dist/configuredClient.js');
const { downloadDataset } = require('@openneuro/cli/dist/datasets.js');
const { getToken } = require('@openneuro/cli/dist/config.js');
const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');
const mkdirp = require('mkdirp');
const crypto = require('crypto');

const client = configuredClient();
const datasetId = 'ds006067';
const tag = '2.0.0';
const ROOT = '/home/jovyan/work/causal-mind-v2';
const dest = path.join(ROOT, 'data', 'neural');
const MNI = 'space-MNI152NLin2009cAsym';

const args = process.argv.slice(2);
const poolArg = args.find((a) => a.startsWith('--pool='));
const limitArg = args.find((a) => a.startsWith('--limit='));
const POOL = poolArg ? parseInt(poolArg.split('=')[1], 10) : 4;
const LIMIT = limitArg ? parseInt(limitArg.split('=')[1], 10) : Infinity;

function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function urlPath(u) {
  try {
    const url = new URL(u);
    const idx = url.pathname.indexOf('ds006067/');
    return idx >= 0 ? url.pathname.slice(idx + 'ds006067/'.length) : url.pathname;
  } catch (e) { return '<unparseable>'; }
}

// Sealed cohort + expected annex keys from the metadata audit.
const seal = JSON.parse(fs.readFileSync(path.join(ROOT, 'reports', 'cm5_cohort_seal.json'), 'utf8'));
const eligible = new Set([
  ...seal.included_subjects.train, ...seal.included_subjects.val, ...seal.included_subjects.test,
]);
const expected = {}; // relPath -> { size, key }
{
  const lines = fs.readFileSync(path.join(ROOT, 'reports', 'cm5_subject_eligibility.tsv'), 'utf8').trim().split('\n');
  const header = lines[0].split('\t');
  const iSub = header.indexOf('subject_id');
  for (const line of lines.slice(1)) {
    const p = line.split('\t');
    const sub = p[iSub];
    if (!eligible.has(sub)) continue;
    const boldKey = p[header.indexOf('bold_annex_key')];
    const maskKey = p[header.indexOf('mask_annex_key')];
    expected[`derivatives/${sub}/func/${sub}_task-thinkaloud_${MNI}_desc-preproc_bold.nii.gz`] =
      { size: parseInt(p[header.indexOf('bold_size')], 10), key: boldKey.split('--')[1] };
    expected[`derivatives/${sub}/func/${sub}_task-thinkaloud_${MNI}_desc-brain_mask.nii.gz`] =
      { size: parseInt(p[header.indexOf('mask_size')], 10), key: maskKey.split('--')[1] };
  }
}
console.log(`eligible subjects: ${eligible.size}, expected files: ${Object.keys(expected).length}`);

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const rp = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (rp === 'derivatives' || /^derivatives\/sub-\d{3}$/.test(rp) ||
          /^derivatives\/sub-\d{3}\/func$/.test(rp)) {
        await collect(f.id, rp, out);
      }
    } else if (expected[rp]) {
      out.push({ path: rp, size: f.size, url: f.urls[f.urls.length - 1] });
    }
  }
}

let authExpired = false;
async function downloadOnce(f, fullPath) {
  const res = await fetch(f.url, { headers: { cookie: `accessToken=${getToken()}` } });
  if (res.status === 401 || res.status === 403) {
    authExpired = true;
    throw new Error(`AUTH_EXPIRED (HTTP ${res.status})`);
  }
  if (res.status !== 200) throw new Error(`HTTP ${res.status}`);
  const buf = await res.buffer();
  const part = fullPath + '.part';
  fs.writeFileSync(part, buf);
  fs.renameSync(part, fullPath);
  return buf;
}

async function processFile(f) {
  const up = urlPath(f.url);
  const exp = expected[f.path];
  const fullPath = path.join(dest, f.path);
  if (up !== f.path) {
    console.log(`SKIP (URL_MISMATCH) ${f.path} (url path: ${up})`);
    return 'mismatch';
  }
  if (exp && f.size !== exp.size) {
    console.log(`SKIP (SIZE_MISMATCH) ${f.path} (api=${f.size} expected=${exp.size})`);
    return 'mismatch';
  }
  if (fs.existsSync(fullPath) && fs.lstatSync(fullPath).size === f.size) {
    const h = sha256(fs.readFileSync(fullPath));
    if (exp && h === exp.key) {
      console.log(`EXISTS ${f.size} -> ${f.path} | HASH_MATCH`);
      return 'skipped';
    }
    console.log(`REHASH_MISMATCH, re-downloading ${f.path}`);
  }
  mkdirp.sync(path.dirname(fullPath));
  let buf = null, lastErr = null;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      buf = await downloadOnce(f, fullPath);
      lastErr = null;
      break;
    } catch (e) {
      lastErr = e;
      if (authExpired || String(e.message).includes('AUTH_EXPIRED')) break;
      await new Promise((r) => setTimeout(r, 3000 * attempt));
    }
  }
  if (lastErr) {
    console.error(`FAILED ${f.path}: ${lastErr.message}`);
    return 'failed';
  }
  const h = sha256(buf);
  const status = exp && h === exp.key ? 'HASH_MATCH' : `HASH_MISMATCH(expected=${exp && exp.key} got=${h})`;
  if (status !== 'HASH_MATCH') {
    fs.unlinkSync(fullPath);
    console.error(`REMOVED (hash bad) ${f.path}`);
    return 'hash_bad';
  }
  console.log(`downloaded ${buf.length} -> ${f.path} | ${status}`);
  return 'ok';
}

async function main() {
  const out = [];
  await collect(null, '', out);
  console.log(`tree walk found ${out.length} target files`);
  const targets = out.slice(0, LIMIT);
  const tally = { ok: 0, skipped: 0, mismatch: 0, failed: 0, hash_bad: 0 };
  let idx = 0;
  const t0 = Date.now();
  async function worker() {
    while (idx < targets.length && !authExpired) {
      const i = idx++;
      const f = targets[i];
      try {
        tally[await processFile(f)]++;
      } catch (e) {
        console.error(`ERROR ${f.path}: ${e.message}`);
        tally.failed++;
      }
    }
  }
  await Promise.all(Array.from({ length: POOL }, worker));
  const mins = (Date.now() - t0) / 60000;
  console.log(`SUMMARY ok=${tally.ok} skipped=${tally.skipped} url_mismatch=${tally.mismatch} hash_bad=${tally.hash_bad} failed=${tally.failed} (${mins.toFixed(1)} min)`);
  if (authExpired) console.log('AUTH_EXPIRED: stop; re-run to resume after re-auth.');
  if (tally.failed > 0 || tally.hash_bad > 0 || tally.mismatch > 0) process.exitCode = 1;
}
main().catch((e) => { console.error(e.message || e); process.exit(1); });
