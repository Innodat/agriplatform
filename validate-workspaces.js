const fs = require("fs");
const path = require("path");

const root = process.cwd();
const included = ["packages/*"];
const excludedPrefixes = ["packages/tools", "packages/backend"];

const pkgsDir = path.join(root, "packages");
if (!fs.existsSync(pkgsDir)) {
  console.error("No packages/ directory found.");
  process.exit(1);
}

const dirs = fs.readdirSync(pkgsDir, { withFileTypes: true })
  .filter(d => d.isDirectory())
  .map(d => path.join("packages", d.name))
  .filter(p => !excludedPrefixes.some(ex => p.startsWith(ex)));

let ok = 0, bad = 0;
for (const p of dirs) {
  const pkgJsonPath = path.join(root, p, "package.json");
  if (!fs.existsSync(pkgJsonPath)) {
    console.log(`? ${p}: missing package.json`);
    bad++;
    continue;
  }
  try {
    const j = JSON.parse(fs.readFileSync(pkgJsonPath, "utf8"));
    const name = j.name;
    const ver = j.version;
    const nameOk = typeof name === "string" && name.length > 0 && name === name.toLowerCase();
    const verOk = typeof ver === "string" && /^\d+\.\d+\.\d+(?:[-+].*)?$/.test(ver);

    if (!nameOk || !verOk) {
      console.log(`? ${p}: invalid fields -> name='${name}' version='${ver}'`);
      if (!nameOk) console.log("   - name must be lowercase or scoped (e.g., @agriplatform/mobile)");
      if (!verOk) console.log("   - version must be semver like 0.0.1");
      bad++;
    } else {
      console.log(`? ${p}: name='${name}' version='${ver}'`);
      ok++;
    }
  } catch (e) {
    console.log(`? ${p}: JSON parse error -> ${e.message}`);
    bad++;
  }
}
console.log(`\nSummary: ${ok} ok, ${bad} problems`);
