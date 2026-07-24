const fs = require('fs');
const vm = require('vm');
const f = process.argv[2];
const h = fs.readFileSync(f, 'utf8');
const scripts = [...h.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const map = scripts.find(s => s.includes('var POIS'));
if (!map) { console.log(f, 'NO POIS SCRIPT'); process.exit(1); }
try {
  new vm.Script(map);
  console.log(f, 'SYNTAX OK');
} catch (e) {
  console.log(f, 'SYNTAX ERROR:', e.message);
  process.exit(1);
}
