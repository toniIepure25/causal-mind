// Inspect ALL urls the API returns for one file (no download).
// Usage: node cm5_url_inspect.js <subject> <filename-suffix>
const { configuredClient } = require('@openneuro/cli/dist/configuredClient.js');
const { downloadDataset } = require('@openneuro/cli/dist/datasets.js');

const client = configuredClient();
const datasetId = 'ds006067';
const tag = '2.0.0';
const sub = process.argv[2];
const suffix = process.argv[3];
if (!sub || !suffix) { console.error('usage: node cm5_url_inspect.js <subject> <suffix>'); process.exit(2); }

async function collect(tree, prefix, out) {
  const files = await downloadDataset(client)({ datasetId, tag, tree });
  for (const f of files) {
    const rp = prefix ? `${prefix}/${f.filename}` : f.filename;
    if (f.directory) {
      if (rp === 'derivatives' || rp === `derivatives/${sub}` || rp === `derivatives/${sub}/func`) {
        await collect(f.id, rp, out);
      }
    } else if (rp.endsWith(suffix)) {
      out.push({ path: rp, size: f.size, urls: f.urls });
    }
  }
}

async function main() {
  const out = [];
  await collect(null, '', out);
  for (const f of out) {
    console.log(`path: ${f.path}`);
    console.log(`size: ${f.size}`);
    f.urls.forEach((u, i) => console.log(`url[${i}]: ${u}`));
  }
  if (!out.length) console.log('no matching file found');
}
main().catch((e) => { console.error(e.message || e); process.exit(1); });
