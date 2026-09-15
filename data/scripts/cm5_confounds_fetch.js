// CM-5 cheap QC acquisition: confounds TSVs for all 118 subjects.
//
// - Walks the OpenNeuro snapshot 2.0.0 tree (authenticated).
// - HARD GUARD: requested dataset path must match the resolved S3 URL path
//   (urlPath(url) === requestedPath). Mismatch => SKIP, never download.
//   (Regression guard for the documented OpenNeuro API path-mismatch anomaly.)
// - Expected SHA256 per file comes from reports/cm5_subject_eligibility.tsv
//   (derived from the authoritative git metadata clone annex keys).
// - Idempotent: existing file with matching size+hash is skipped.
// - Resumable: safe to re-run; token-expiry safe (fails loudly, no partial
//   files kept: writes to .part then renames).
//
// Usage: node cm5_confounds_fetch.js [--limit=N]
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
const auditTsv = path.join(ROOT, 'reports', 'cm5_subject_eligibility.tsv');
const limitArg = process.argv.slice(2).find((a) => a.startsWith('--limit='));
const limit = limitArg ? parseInt(limitArg.split('=')[1], 10) : Infinity;

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function urlPath(u) {
  try {
    const url = new URL(u);
    const idx = url.pathname.indexOf('ds006067/');
    return idx >= 0 ? url.pathname.slice(idx + 'ds006067/'.length) : url.pathname;
  } catch (e) {
    return '<unparseable>';
  }
}

// Expected confounds keys from the metadata audit (git-clone annex keys).
const expected = {}; // relPath -> { size, key }
{
  const lines = fs.readFileSync(auditTsv, 'utf8').trim().split('\n');
  const header = lines[0].split('\t');
  const iSub = header.indexOf('subject_id');
  const iAvail = header.indexOf('confounds_available');
  const iSize = header.indexOf('confounds_size');
  const iKey = header.indexOf('confounds_annex_key');
  for (const line of lines.slice(1)) {
    const p = line.split('\t');
    if (p[iAvail] === '1' && p[iKey] && p[iKey].startsWith('SHA256E-')) {
      const rel = `derivatives/${p[iSub]}/func/${p[iSub]}_task-thinkaloud_desc-confounds_timeseries.tsv`;
      expected[rel] = { size: parseInt(p[iSize], 10), key: p[iKey].split('--')[1] };
    }
  }
}
console.log(`expected confounds files: ${Object.keys(expected).length}`);

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const relPath = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (relPath === 'derivatives' || /^derivatives\/sub-\d{3}$/.test(relPath) ||
          /^derivatives\/sub-\d{3}\/func$/.test(relPath)) {
        await collect(f.id, relPath, out);
      }
    } else if (/_desc-confounds_timeseries\.tsv$/.test(relPath)) {
      out.push({ path: relPath, size: f.size, url: f.urls[f.urls.length - 1] });
    }
  }
}

async function downloadOnce(f, fullPath) {
  const res = await fetch(f.url, { headers: { cookie: `accessToken=${getToken()}` } });
  if (res.status === 401 || res.status === 403) {
    throw new Error(`AUTH_EXPIRED (HTTP ${res.status})`);
  }
  if (res.status !== 200) {
    throw new Error(`HTTP ${res.status}`);
  }
  const buf = await res.buffer();
  const part = fullPath + '.part';
  fs.writeFileSync(part, buf);
  fs.renameSync(part, fullPath);
  return buf;
}

async function main() {
  const out = [];
  await collect(null, '', out);
  console.log(`tree walk found ${out.length} confounds TSVs`);
  const targets = out.filter((f) => expected[f.path]).slice(0, limit);
  let ok = 0, skipped = 0, mismatch = 0, failed = 0, hashBad = 0;
  for (const f of targets) {
    const up = urlPath(f.url);
    const fullPath = path.join(dest, f.path);
    const exp = expected[f.path];
    if (up !== f.path) {
      console.log(`SKIP (URL_MISMATCH) ${f.path} (url path: ${up})`);
      mismatch++;
      continue;
    }
    if (fs.existsSync(fullPath) && fs.lstatSync(fullPath).size === f.size) {
      const h = sha256(fs.readFileSync(fullPath));
      if (h === exp.key) {
        console.log(`EXISTS ${f.size} -> ${f.path} | HASH_MATCH`);
        skipped++;
        continue;
      }
      console.log(`REHASH_MISMATCH, re-downloading ${f.path}`);
    }
    try {
      mkdirp.sync(path.dirname(fullPath));
      let buf = null, lastErr = null;
      for (let attempt = 1; attempt <= 3; attempt++) {
        try {
          buf = await downloadOnce(f, fullPath);
          lastErr = null;
          break;
        } catch (e) {
          lastErr = e;
          if (String(e.message).includes('AUTH_EXPIRED')) break;
          await new Promise((r) => setTimeout(r, 2000 * attempt));
        }
      }
      if (lastErr) {
        console.error(`FAILED ${f.path}: ${lastErr.message}`);
        failed++;
        continue;
      }
      const h = sha256(buf);
      const status = h === exp.key ? 'HASH_MATCH' : `HASH_MISMATCH(expected=${exp.key} got=${h})`;
      if (status !== 'HASH_MATCH') {
        fs.unlinkSync(fullPath);
        hashBad++;
      } else {
        ok++;
      }
      console.log(`downloaded ${buf.length} -> ${f.path} | ${status}`);
    } catch (e) {
      console.error(`ERROR ${f.path}: ${e.message}`);
      failed++;
    }
  }
  console.log(`SUMMARY ok=${ok} skipped=${skipped} url_mismatch=${mismatch} hash_bad=${hashBad} failed=${failed}`);
  if (failed > 0 || hashBad > 0 || mismatch > 0) process.exitCode = 1;
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
