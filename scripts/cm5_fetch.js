const { configuredClient} = require('@openneuro/cli/dist/configuredClient.js');
const { downloadDataset} = require('@openneuro/cli/dist/datasets.js');
const { getToken} = require('@openneuro/cli/dist/config.js');
const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');
const mkdirp = require('mkdirp');
const crypto = require('crypto');

const client = configuredClient();
const datasetId = 'ds006067';
const tag = '2.0.0';
const dest = process.argv.slice(2).find((a) => !a.startsWith('--')) || '/home/jovyan/work/causal-mind-v2/data/neural';
const args = process.argv.slice(2);
const dryRun = args.includes('--dry');
const onlySmall = args.includes('--small');
const noOptional = args.includes('--no-optional');
const subjectArg = args.find((a) => a.startsWith('--subject='));
const subject = subjectArg ? subjectArg.split('=')[1] : null;

const wanted = [
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.json',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_desc-confounds_timeseries.tsv',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_desc-confounds_timeseries.json',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_smooth4mm_denoise_bold.nii.gz',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.json',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_desc-confounds_timeseries.tsv',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_desc-confounds_timeseries.json',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_smooth4mm_denoise_bold.nii.gz',
];

const annexKeys = {
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz': '52c72996946001bda6c767f0cbcad923b53649cb458b61bd0455473759f05a24',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz': '3851b28e93c4b4d61d57787e7c206d3b6fd62da67a566d72704c72ae74b5fb89',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_desc-confounds_timeseries.tsv': '04fbbd4e86a4524c2d1f685e2bdcf89cf00f6601ec6a274c76b6620bffbbd5ef',
  'derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_smooth4mm_denoise_bold.nii.gz': 'a8e0b10c027fd4f1beb042321e3cafbe24f44b40d57ea74c81f06583dd283b5c',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz': 'bf4477999a475c3f3508e03856d9117c869bf83f48774eb71c1af2fc8a716a27',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz': '0fab12dc45f6e23d045575b14a09c0b30167b4ab7cd8d25ec12986a4f73a9a9e',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_desc-confounds_timeseries.tsv': 'ba3d7c1ed37156c9cdd38f3fa7930041332bf287135fe7fc051a099a32e381cf',
  'derivatives/sub-005/func/sub-005_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_smooth4mm_denoise_bold.nii.gz': '92129e86411c58563fae5a00ec97abbe1d4c8b80bc6a9cf78decdda855282eb3',
};

const enterDirs = new Set([
  'derivatives',
  'derivatives/sub-001',
  'derivatives/sub-001/func',
  'derivatives/sub-005',
  'derivatives/sub-005/func',
]);

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const relPath = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (enterDirs.has(relPath)) {
        await collect(f.id, relPath, out);
      }
    } else {
      out.push({ path: relPath, size: f.size, url: f.urls[f.urls.length - 1] });
    }
  }
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
function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

async function main() {
  const out = [];
  await collect(null, '', out);
  let toDownload = out.filter((f) => wanted.includes(f.path));
  if (subject) {
    toDownload = toDownload.filter((f) => f.path.includes(`/func/${subject}_`) || f.path.includes(`/func/${subject}`));
  }
  if (noOptional) {
    toDownload = toDownload.filter((f) => !f.path.includes('smooth4mm'));
  }
  console.log(`targets: ${toDownload.length}`);
  for (const f of toDownload) {
    const up = urlPath(f.url);
    const match = up === f.path ? 'URL_MATCH' : 'URL_MISMATCH';
    console.log(`- ${f.path} | size=${f.size} | ${match}`);
  }
  if (dryRun) return;

  let targets = toDownload;
  if (onlySmall) {
    targets = targets.filter((f) => f.size < 100000);
  }
  for (const f of targets) {
    const up = urlPath(f.url);
    if (up !== f.path) {
      console.log(`  SKIP (URL_MISMATCH) ${f.path}`);
      continue;
    }
    const fullPath = path.join(dest, f.path);
    if (fs.existsSync(fullPath) && fs.lstatSync(fullPath).size === f.size) {
      const buf = fs.readFileSync(fullPath);
      const hash = sha256(buf);
      const expected = annexKeys[f.path];
      const status = expected ? (hash === expected ? 'HASH_MATCH' : 'HASH_MISMATCH') : 'OK';
      console.log(`  EXISTS ${buf.length} bytes -> ${fullPath} | ${status}`);
      continue;
    }
    mkdirp.sync(path.dirname(fullPath));
    const res = await fetch(f.url, { headers: { cookie: `accessToken=${getToken()}` } });
    if (res.status === 200) {
      const buf = await res.buffer();
      fs.writeFileSync(fullPath, buf);
      const hash = sha256(buf);
      const expected = annexKeys[f.path];
      let status = 'OK';
      if (expected) {
        status = hash === expected ? 'HASH_MATCH' : `HASH_MISMATCH(expected=${expected} got=${hash})`;
      }
      console.log(`  downloaded ${buf.length} bytes -> ${fullPath} | ${status}`);
    } else {
      console.error(`  FAILED: HTTP ${res.status} for ${f.path}`);
    }
  }
}
main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});