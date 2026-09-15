// Targeted retry for a single subject's confounds TSV (URL guard enforced).
// Usage: node cm5_confounds_retry.js <subject>
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
const sub = process.argv[2];
if (!sub) { console.error('usage: node cm5_confounds_retry.js <subject>'); process.exit(2); }

function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function urlPath(u) {
  try {
    const url = new URL(u);
    const idx = url.pathname.indexOf('ds006067/');
    return idx >= 0 ? url.pathname.slice(idx + 'ds006067/'.length) : url.pathname;
  } catch (e) { return '<unparseable>'; }
}

const auditTsv = path.join(ROOT, 'reports', 'cm5_subject_eligibility.tsv');
const lines = fs.readFileSync(auditTsv, 'utf8').trim().split('\n');
const header = lines[0].split('\t');
const row = lines.slice(1).find((l) => l.split('\t')[header.indexOf('subject_id')] === sub);
const p = row.split('\t');
const expKey = p[header.indexOf('confounds_annex_key')].split('--')[1];
const expSize = parseInt(p[header.indexOf('confounds_size')], 10);
const relPath = `derivatives/${sub}/func/${sub}_task-thinkaloud_desc-confounds_timeseries.tsv`;

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const relPathNow = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (relPathNow === 'derivatives' || relPathNow === `derivatives/${sub}` ||
          relPathNow === `derivatives/${sub}/func`) {
        await collect(f.id, relPathNow, out);
      }
    } else if (relPathNow === relPath) {
      out.push({ path: relPathNow, size: f.size, url: f.urls[f.urls.length - 1] });
    }
  }
}

async function main() {
  const out = [];
  await collect(null, '', out);
  if (out.length !== 1) { console.error(`expected 1 target, found ${out.length}`); process.exit(1); }
  const f = out[0];
  const up = urlPath(f.url);
  console.log(`requested: ${f.path}`);
  console.log(`url path : ${up}`);
  console.log(`size     : ${f.size} (expected ${expSize})`);
  if (up !== f.path) {
    console.log('RESULT: URL_MISMATCH (guard holds; not downloaded)');
    process.exit(1);
  }
  const fullPath = path.join(dest, f.path);
  mkdirp.sync(path.dirname(fullPath));
  const res = await fetch(f.url, { headers: { cookie: `accessToken=${getToken()}` } });
  if (res.status !== 200) { console.error(`HTTP ${res.status}`); process.exit(1); }
  const buf = await res.buffer();
  const h = sha256(buf);
  const status = h === expKey ? 'HASH_MATCH' : `HASH_MISMATCH(expected=${expKey} got=${h})`;
  if (status === 'HASH_MATCH') {
    fs.writeFileSync(fullPath, buf);
    console.log(`downloaded ${buf.length} -> ${f.path} | ${status}`);
  } else {
    console.error(`NOT SAVED: ${status}`);
    process.exit(1);
  }
}
main().catch((e) => { console.error(e.message || e); process.exit(1); });
