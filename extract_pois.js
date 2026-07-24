const fs = require('fs');
const f = process.argv[2];
const h = fs.readFileSync(f, 'utf8');
const m = h.match(/var POIS = (\[[\s\S]*?\]);/);
if (!m) { console.log(f, 'NO POIS ARRAY'); process.exit(1); }
const arr = JSON.parse(m[1]);
console.log('=== ' + f + ' (' + arr.length + ' POIs) ===');
arr.forEach(p => console.log(
  String(p.id).padEnd(16),
  'lat=' + p.lat, 'lng=' + p.lng, 'src=' + p.src
));
