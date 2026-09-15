// Audit BOLD availability for all subjects (metadata only, no downloads).
// Flags: URL path mismatch, or size inconsistent with the git-clone annex key.
// Output: data/manifests/cm5_bold_url_audit.tsv
const { configuredClient } = require('@openneuro/cli/dist/configuredClient.js');
const { downloadDataset } = require('@openneuro/cli/dist/datasets.js');
const fs = require('fs');
const path = require('path');

const client = configuredClient();
const datasetId = 'ds006067';
const tag = '2.0.0';
const ROOT = '/home/jovyan/work/causal-mind-v2';
const MNI = 'space-MNI152NLin2009cAsym';
const outTsv = path.join(ROOT, 'data', 'manifests', 'cm5_bold_url_audit.tsv');

function urlPath(u) {
  try {
    const url = new URL(u);
    const idx = url.pathname.indexOf('ds006067/');
    return idx >= 0 ? url.pathname.slice(idx + 'ds006067/'.length) : url.pathname;
  } catch (e) { return '<unparseable>'; }
}

// expected sizes from the metadata audit
const expected = {};
{
  const lines = fs.readFileSync(path.join(ROOT, 'reports', 'cm5_subject_eligibility.tsv'), 'utf8').trim().split('\n');
  const header = lines[0].split('\t');
  const iSub = header.indexOf('subject_id');
  const iSize = header.indexOf('bold_size');
  for (const line of lines.slice(1)) {
    const p = line.split('\t');
    expected[p[iSub]] = parseInt(p[iSize], 10);
  }
}

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const rp = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (rp === 'derivatives' || /^derivatives\/sub-\d{3}$/.test(rp) ||
          /^derivatives\/sub-\d{3}\/func$/.test(rp)) {
        await collect(f.id, rp, out);
      }
    } else if (new RegExp(`^sub-\\d{3}_task-thinkaloud_${MNI}_desc-preproc_bold\\.nii\\.gz$`).test(f.filename)) {
      out.push({ path: rp, size: f.size, url: f.urls[f.urls.length - 1] });
    }
  }
}

async function main() {
  const out = [];
  await collect(null, '', out);
  const rows = [['subject', 'api_size', 'expected_size', 'url_match', 'status']];
  let bad = 0;
  for (const f of out) {
    const sub = f.path.split('/')[1];
    const up = urlPath(f.url);
    const match = up === f.path ? '1' : '0';
    const exp = expected[sub] || 0;
    let status = 'OK';
    if (match === '0') status = 'URL_MISMATCH';
    else if (exp > 0 && Math.abs(f.size - exp) > 1024) status = 'SIZE_MISMATCH';
    if (status !== 'OK') bad++;
    rows.push([sub, String(f.size), String(exp), match, status]);
  }
  fs.writeFileSync(outTsv, rows.map((r) => r.join('\t')).join('\n') + '\n');
  console.log(`subjects in audit: ${rows.length - 1}, flagged: ${bad}`);
  for (const r of rows.slice(1)) if (r[4] !== 'OK') console.log(`  ${r[0]}: ${r[4]} (api=${r[1]} expected=${r[2]})`);
}
main().catch((e) => { console.error(e.message || e); process.exit(1); });
