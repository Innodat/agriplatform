import { test } from "node:test";
import fs from "node:fs";
import { syncBuiltinESMExports } from "node:module";
import assert from "node:assert/strict";
import {
  mkdtempSync,
  readFileSync,
  writeFileSync,
  mkdirSync,
  symlinkSync,
  rmSync,
  existsSync,
  readdirSync,
  lstatSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import {
  installScaffold,
  checkScaffold,
  recoverScaffold,
} from "../src/scaffold-install.ts";
const identity = {
  generator: "builder-v1",
  template: "application-v1-candidate",
  recipe: "a".repeat(64),
  source: "b".repeat(64),
};
const files = {
  "a.txt": { classification: "generated", content: "one" },
  "nested/z.txt": { classification: "generated", content: "two" },
  "seed.txt": { classification: "seed", content: "seed" },
};
function fixture(t) {
  const root = mkdtempSync(join(tmpdir(), "preservation-"));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  writeFileSync(join(root, "docs.md"), "docs");
  return root;
}
const read = (root, path) => readFileSync(join(root, path), "utf8");
test("initial install, stable rerun, seed/custom/docs preservation and generated update", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  writeFileSync(join(root, "seed.txt"), "owner edit");
  writeFileSync(join(root, "custom.txt"), "custom");
  installScaffold(root, files, identity);
  assert.equal(read(root, "seed.txt"), "owner edit");
  assert.equal(read(root, "custom.txt"), "custom");
  assert.equal(read(root, "docs.md"), "docs");
  installScaffold(
    root,
    { ...files, "a.txt": { ...files["a.txt"], content: "updated" } },
    identity
  );
  assert.equal(read(root, "a.txt"), "updated");
  checkScaffold(root);
});
test("later generated conflict and missing file refuse entire plan", (t) => {
  for (const missing of [false, true]) {
    const root = fixture(t);
    installScaffold(root, files, identity);
    if (missing) rmSync(join(root, "nested/z.txt"));
    else writeFileSync(join(root, "nested/z.txt"), "edited");
    assert.throws(
      () =>
        installScaffold(
          root,
          { ...files, "a.txt": { ...files["a.txt"], content: "new" } },
          identity
        ),
      /scaffold_conflict/
    );
    assert.equal(read(root, "a.txt"), "one");
  }
});
test("initial collisions and unsafe maps refuse before writes", (t) => {
  for (const map of [
    { ...files, "docs.md": { classification: "seed", content: "overwrite" } },
    { "../escape": files["a.txt"] },
    { a: files["a.txt"], "a/b": files["a.txt"] },
    { ".generated-files.json": files["a.txt"] },
    { bad: { classification: "other", content: "x" } },
  ]) {
    const root = fixture(t);
    assert.throws(() => installScaffold(root, map, identity), /scaffold_/);
    assert.equal(read(root, "docs.md"), "docs");
    assert.equal(existsSync(join(root, "a.txt")), false);
  }
});
test("symlinks and invalid manifest, identity, ownership are refused", (t) => {
  const root = fixture(t);
  mkdirSync(join(root, "nested"));
  symlinkSync(join(root, "docs.md"), join(root, "nested/z.txt"));
  assert.throws(() => installScaffold(root, files, identity), /scaffold_/);
  rmSync(join(root, "nested/z.txt"));
  installScaffold(root, files, identity);
  assert.throws(
    () =>
      installScaffold(
        root,
        {
          ...files,
          "seed.txt": { classification: "generated", content: "seed" },
        },
        identity
      ),
    /scaffold_ownership/
  );
  assert.throws(
    () => installScaffold(root, files, { ...identity, template: "new" }),
    /scaffold_identity/
  );
  writeFileSync(join(root, ".generated-files.json"), "{}");
  assert.throws(
    () => installScaffold(root, files, identity),
    /scaffold_manifest/
  );
});
test("missing manifest and extra/unrecognized metadata refuse", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  rmSync(join(root, ".generated-files.json"));
  assert.throws(
    () => installScaffold(root, files, identity),
    /scaffold_conflict/
  );
  const clean = fixture(t);
  assert.throws(
    () => installScaffold(clean, files, { ...identity, secret: "x" }),
    /scaffold_identity/
  );
});
test("write failure restores previous complete set and preserves owner edits", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  writeFileSync(join(root, "seed.txt"), "owner");
  assert.throws(
    () =>
      installScaffold(
        root,
        { ...files, "a.txt": { ...files["a.txt"], content: "new" } },
        identity,
        {
          afterWrite: () => {
            throw Error("injected");
          },
        }
      ),
    /scaffold_install_failed/
  );
  assert.equal(read(root, "a.txt"), "one");
  assert.equal(read(root, "seed.txt"), "owner");
  checkScaffold(root);
});
test("interrupted process requires explicit recovery; live writer excluded", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  const installer = new URL("../src/scaffold-install.ts", import.meta.url).href;
  const script = `import {installScaffold} from ${JSON.stringify(
    installer
  )};installScaffold(${JSON.stringify(root)},${JSON.stringify({
    ...files,
    "a.txt": { ...files["a.txt"], content: "new" },
  })},${JSON.stringify(
    identity
  )},{afterWrite(){process.kill(process.pid,'SIGKILL')}});`;
  const child = spawnSync(process.execPath, [
    "--input-type=module",
    "-e",
    script,
  ]);
  assert.equal(child.signal, "SIGKILL");
  assert.throws(() => checkScaffold(root), /scaffold_recovery_required/);
  assert.throws(
    () => installScaffold(root, files, identity),
    /scaffold_recovery_required/
  );
  recoverScaffold(root);
  assert.equal(read(root, "a.txt"), "one");
  checkScaffold(root);
  installScaffold(root, files, identity, {
    afterWrite() {
      assert.throws(
        () => installScaffold(root, files, identity),
        /scaffold_busy/
      );
      assert.throws(() => recoverScaffold(root), /scaffold_busy/);
    },
  });
});
test("uncertain recovery refuses without changing owner content", (t) => {
  const root = fixture(t);
  const installer = new URL("../src/scaffold-install.ts", import.meta.url).href;
  spawnSync(process.execPath, [
    "--input-type=module",
    "-e",
    `import {installScaffold} from ${JSON.stringify(
      installer
    )};installScaffold(${JSON.stringify(root)},${JSON.stringify(
      files
    )},${JSON.stringify(
      identity
    )},{afterWrite(){process.kill(process.pid,'SIGKILL')}});`,
  ]);
  writeFileSync(join(root, "a.txt"), "owner after crash");
  assert.throws(() => recoverScaffold(root), /scaffold_recovery_uncertain/);
  assert.equal(read(root, "a.txt"), "owner after crash");
});
test("symlink output and ancestor refuse, even when targets are absent", (t) => {
  const root = fixture(t);
  const target = fixture(t);
  symlinkSync(target, join(root, "linked"));
  assert.throws(
    () => installScaffold(join(root, "linked"), files, identity),
    /scaffold_path_invalid/
  );
  assert.throws(
    () => installScaffold(join(root, "linked", "new"), files, identity),
    /scaffold_path_invalid/
  );
  assert.equal(existsSync(join(target, "a.txt")), false);
});
test("malformed journal is refused before restoring any files", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  const installer = new URL("../src/scaffold-install.ts", import.meta.url).href;
  spawnSync(process.execPath, [
    "--input-type=module",
    "-e",
    `import {installScaffold} from ${JSON.stringify(
      installer
    )};installScaffold(${JSON.stringify(root)},${JSON.stringify({
      ...files,
      "a.txt": { ...files["a.txt"], content: "new" },
    })},${JSON.stringify(
      identity
    )},{afterWrite(){process.kill(process.pid,'SIGKILL')}});`,
  ]);
  writeFileSync(
    join(root, ".scaffold-install-state/journal.json"),
    JSON.stringify({
      schema_version: 1,
      changes: [
        {
          path: "docs.md",
          old: null,
          next: Buffer.from("docs").toString("base64"),
        },
      ],
    })
  );
  assert.throws(() => recoverScaffold(root), /scaffold_recovery_uncertain/);
  assert.equal(read(root, "a.txt"), "new");
  assert.equal(read(root, "docs.md"), "docs");
});

const installerURL = new URL("../src/scaffold-install.ts", import.meta.url)
  .href;
function interrupted(root, plan = files, position = 1) {
  const child = spawnSync(process.execPath, [
    "--input-type=module",
    "-e",
    `
    import {installScaffold} from ${JSON.stringify(installerURL)};
    installScaffold(${JSON.stringify(root)}, ${JSON.stringify(
      plan
    )}, ${JSON.stringify(identity)}, {
      afterWrite(count) { if (count === ${position}) process.kill(process.pid, 'SIGKILL'); }
    });`,
  ]);
  assert.equal(child.signal, "SIGKILL");
}
function snapshot(root) {
  return Object.fromEntries(
    readdirSync(root, { recursive: true })
      .filter((path) => lstatSync(join(root, path)).isFile())
      .sort()
      .map((path) => [path, read(root, path)])
  );
}
test("own __proto__ destination survives manifest ownership roundtrip", (t) => {
  const root = fixture(t);
  const plan = Object.assign(Object.create(null), files);
  plan.__proto__ = {
    classification: "generated",
    content: "prototype destination",
  };
  installScaffold(root, plan, identity);
  const manifest = JSON.parse(read(root, ".generated-files.json"));
  assert.equal(Object.hasOwn(manifest.files, "__proto__"), true);
  installScaffold(root, plan, identity);
  checkScaffold(root);
  assert.equal(read(root, "__proto__"), "prototype destination");
});
test("caught replacement failures roll back at seed and manifest positions", (t) => {
  for (const initial of [true, false])
    for (const position of initial ? [1, 3, 4] : [1, 2, 3]) {
      const root = fixture(t);
      if (!initial) {
        installScaffold(root, files, identity);
        writeFileSync(join(root, "seed.txt"), "owner");
      }
      writeFileSync(join(root, "custom.txt"), "custom");
      const before = snapshot(root);
      assert.throws(
        () =>
          installScaffold(
            root,
            { ...files, "a.txt": { ...files["a.txt"], content: "changed" } },
            identity,
            {
              afterWrite(count) {
                if (count === position) throw Error("injected");
              },
            }
          ),
        /scaffold_install_failed/
      );
      assert.deepEqual(snapshot(root), before);
    }
});
test("initial SIGKILL rolls back all bytes including seed/manifest then permits reinstall", (t) => {
  for (const position of [3, 4]) {
    const root = fixture(t);
    writeFileSync(join(root, "custom.txt"), "custom");
    const before = snapshot(root);
    interrupted(root, files, position);
    recoverScaffold(root);
    assert.deepEqual(snapshot(root), before);
    installScaffold(root, files, identity);
    checkScaffold(root);
  }
});
test("build admission checks drift and manifest validity but permits edited seeds", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  writeFileSync(join(root, "seed.txt"), "owner");
  checkScaffold(root);
  writeFileSync(join(root, "a.txt"), "edited");
  assert.throws(() => checkScaffold(root), /scaffold_conflict/);
  rmSync(join(root, "a.txt"));
  assert.throws(() => checkScaffold(root), /scaffold_conflict/);
  writeFileSync(join(root, ".generated-files.json"), "{}");
  assert.throws(() => checkScaffold(root), /scaffold_manifest_invalid/);
});
test("partial regular scratch bytes do not prevent validated journal recovery", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  const before = snapshot(root);
  interrupted(root, {
    ...files,
    "a.txt": { ...files["a.txt"], content: "changed" },
  });
  writeFileSync(join(root, ".scaffold-install-state/replacement"), "partial");
  recoverScaffold(root);
  assert.deepEqual(snapshot(root), before);
});
test("recovery claim excludes live competing recovery and install", (t) => {
  const root = fixture(t);
  installScaffold(root, files, identity);
  const before = snapshot(root);
  interrupted(root, {
    ...files,
    "a.txt": { ...files["a.txt"], content: "changed" },
  });
  const original = fs.readFileSync;
  let observed = false;
  fs.readFileSync = function (path, ...args) {
    if (
      String(path) === join(root, ".scaffold-install-state/journal.json") &&
      !observed
    ) {
      observed = true;
      const result = spawnSync(process.execPath, [
        "--input-type=module",
        "-e",
        `
        import assert from 'node:assert/strict';
        import {installScaffold,recoverScaffold} from ${JSON.stringify(
          installerURL
        )};
        assert.throws(()=>recoverScaffold(${JSON.stringify(
          root
        )}),/scaffold_busy/);
        assert.throws(()=>installScaffold(${JSON.stringify(
          root
        )},${JSON.stringify(files)},${JSON.stringify(
          identity
        )}),/scaffold_busy/);`,
      ]);
      assert.equal(result.status, 0, result.stderr.toString());
    }
    return original.call(this, path, ...args);
  };
  syncBuiltinESMExports();
  try {
    recoverScaffold(root);
  } finally {
    fs.readFileSync = original;
    syncBuiltinESMExports();
  }
  assert.equal(observed, true);
  assert.deepEqual(snapshot(root), before);
});
test("dead and incomplete recovery claims fail closed", (t) => {
  for (const contents of [
    null,
    JSON.stringify({ recovering_pid: 2147483647 }),
  ]) {
    const root = fixture(t);
    mkdirSync(join(root, ".scaffold-recovery-claim"));
    if (contents)
      writeFileSync(
        join(root, ".scaffold-recovery-claim/owner.json"),
        contents
      );
    assert.throws(() => recoverScaffold(root), /scaffold_recovery_uncertain/);
    assert.throws(
      () => installScaffold(root, files, identity),
      /scaffold_recovery_uncertain/
    );
    assert.equal(read(root, "docs.md"), "docs");
  }
});
test("actual ENOSPC before mutation cleans only newly created initialization artifacts", (t) => {
  for (const suffix of ["/owner.json", "/journal.json"]) {
    const root = fixture(t),
      before = snapshot(root),
      original = fs.writeFileSync;
    let failed = false;
    fs.writeFileSync = function (path, data, ...args) {
      if (!failed && String(path).endsWith(suffix)) {
        failed = true;
        original.call(this, path, "partial", ...args);
        return original.call(this, "/dev/full", data);
      }
      return original.call(this, path, data, ...args);
    };
    syncBuiltinESMExports();
    try {
      assert.throws(
        () => installScaffold(root, files, identity),
        /scaffold_io_failed/
      );
    } finally {
      fs.writeFileSync = original;
      syncBuiltinESMExports();
    }
    assert.equal(failed, true);
    assert.deepEqual(snapshot(root), before);
    installScaffold(root, files, identity);
    checkScaffold(root);
  }
});
