// Internal disposable-proof installer. Candidate readiness remains the renderer's gate.
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  linkSync,
  opendirSync,
  unlinkSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  rmSync,
  rmdirSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, join, resolve } from "node:path";
import type { ServiceFile } from "./service-renderer.ts";
type Identity = {
  generator: string;
  template: string;
  recipe: string;
  source: string;
};
type Entry = { classification: "seed" | "generated"; sha256: string };
type ExtensionImport = { source: string; destination: string; files: Record<string, string> };
type Extensions = { schema_version: 1; imports: ExtensionImport[] };
export type ExtensionInput = {
  repositoryRoot: string;
  declarations: { source: string; destination: string }[];
};
type Manifest = {
  schema_version: 1;
  identity: Identity;
  files: Record<string, Entry>;
  extensions?: Extensions;
};
type Change = { path: string; old: string | null; next: string };
const manifestName = ".generated-files.json",
  lockName = ".scaffold-install-lock",
  stateName = ".scaffold-install-state",
  recoveryName = ".scaffold-recovery-claim";
const hash = (value: string | Buffer) =>
  createHash("sha256").update(value).digest("hex");
function fail(code: string): never {
  throw new Error(`scaffold_${code}`);
}
const plain = (v: unknown): v is Record<string, unknown> =>
  !!v && typeof v === "object" && !Array.isArray(v);
function exact(v: Record<string, unknown>, keys: string[]) {
  return Object.keys(v).sort().join(",") === keys.sort().join(",");
}
function identityValid(v: unknown): v is Identity {
  return (
    plain(v) &&
    exact(v, ["generator", "template", "recipe", "source"]) &&
    ["generator", "template"].every(
      (k) =>
        typeof v[k] === "string" &&
        /^[a-zA-Z0-9_.-]{1,100}$/.test(v[k] as string)
    ) &&
    ["recipe", "source"].every(
      (k) => typeof v[k] === "string" && /^[a-f0-9]{64}$/.test(v[k] as string)
    )
  );
}
function pathValid(path: string) {
  return (
    path.length <= 512 &&
    !isAbsolute(path) &&
    path
      .split("/")
      .every(
        (p) =>
          p !== "" &&
          p !== "." &&
          p !== ".." &&
          !p.includes("\\") &&
          !/[\x00-\x1f]/.test(p)
      ) &&
    !path
      .split("/")
      .some((p) =>
        [manifestName, lockName, stateName, recoveryName, ".git"].includes(p)
      )
  );
}
function safe(path: string, kind: "file" | "directory") {
  let current = "/";
  for (const part of resolve(path).split("/").filter(Boolean)) {
    current = join(current, part);
    if (!existsSync(current)) {
      // lstat still detects dangling symlinks
      try {
        lstatSync(current);
        fail("path_invalid");
      } catch (e) {
        if ((e as NodeJS.ErrnoException).code !== "ENOENT") throw e;
      }
      continue;
    }
    const stat = lstatSync(current);
    if (stat.isSymbolicLink()) fail("path_invalid");
    if (current !== resolve(path) && !stat.isDirectory()) fail("path_invalid");
  }
  if (existsSync(path)) {
    const stat = lstatSync(path);
    if (kind === "file" ? !stat.isFile() : !stat.isDirectory())
      fail("path_invalid");
  }
}
function read(path: string): string | null {
  safe(path, "file");
  return existsSync(path) ? readFileSync(path).toString("base64") : null;
}
function load(root: string): Manifest | null {
  const bytes = read(join(root, manifestName));
  if (bytes === null) return null;
  return decodeManifest(bytes);
}
function decodeManifest(bytes: string): Manifest {
  let m: unknown;
  try {
    m = JSON.parse(Buffer.from(bytes, "base64").toString());
  } catch {
    fail("manifest_invalid");
  }
  if (
    !plain(m) ||
    !exact(m, ["schema_version", "identity", "files", ...(Object.hasOwn(m, "extensions") ? ["extensions"] : [])]) ||
    m.schema_version !== 1 ||
    !identityValid(m.identity) ||
    !plain(m.files) ||
    !Object.keys(m.files).length
  )
    fail("manifest_invalid");
  for (const [path, e] of Object.entries(m.files)) {
    if (
      !pathValid(path) ||
      !plain(e) ||
      !exact(e, ["classification", "sha256"]) ||
      !["seed", "generated"].includes(e.classification as string) ||
      typeof e.sha256 !== "string" ||
      !/^[a-f0-9]{64}$/.test(e.sha256)
    )
      fail("manifest_invalid");
  }
  const paths = Object.keys(m.files);
  if (paths.some((p) => paths.some((q) => q.startsWith(p + "/"))))
    fail("manifest_invalid");
  if (Object.hasOwn(m, "extensions")) validateExtensions(m.extensions, paths);
  return m as Manifest;
}
// Imports are bounded text-only snapshots. Their hashes describe provenance, never
// authority to refresh or validate owner-maintained custom content on later runs.
const overlaps = (a: string, b: string) =>
  a === b || a.startsWith(b + "/") || b.startsWith(a + "/");
function importPath(path: unknown): path is string {
  return typeof path === "string" && pathValid(path) &&
    path.split("/").every(part => /^[a-zA-Z0-9_.-]+$/.test(part) &&
      !part.endsWith(".") && !/^(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)/i.test(part));
}
function declarationsValid(value: unknown): value is ExtensionInput["declarations"] {
  return Array.isArray(value) && value.length <= 100 && value.every((d, index) =>
    plain(d) && exact(d, ["source", "destination"]) && importPath(d.source) && importPath(d.destination) &&
    !value.slice(0, index).some(previous => overlaps(previous.source, d.source as string) || overlaps(previous.destination, d.destination as string)));
}
function validateExtensions(value: unknown, basePaths: string[]): asserts value is Extensions {
  if (!plain(value) || !exact(value, ["schema_version", "imports"]) ||
      value.schema_version !== 1 || !Array.isArray(value.imports) ||
      !value.imports.length || value.imports.length > 100) fail("manifest_invalid");
  const roots: string[] = [], sources: string[] = [];
  let count = 0;
  for (const entry of value.imports) {
    if (!plain(entry) || !exact(entry, ["source", "destination", "files"]) ||
        !importPath(entry.source) || !importPath(entry.destination) || !plain(entry.files) ||
        roots.some(root => overlaps(root, entry.destination as string)) ||
        sources.some(source => overlaps(source, entry.source as string)) ||
        basePaths.some(path => overlaps(path, entry.destination as string))) fail("manifest_invalid");
    roots.push(entry.destination);
    sources.push(entry.source);
    const paths = Object.keys(entry.files);
    for (const path of paths) {
      if (!importPath(path) || path.split("/").length > 16 ||
          !importPath(entry.destination + "/" + path) ||
          paths.some(other => other.startsWith(path + "/")) ||
          typeof entry.files[path] !== "string" || !/^[a-f0-9]{64}$/.test(entry.files[path] as string) ||
          ++count > 1000) fail("manifest_invalid");
    }
  }
}
function extensionPlan(root: string, basePaths: string[], input: ExtensionInput | undefined, previous: Manifest | null) {
  if (input !== undefined && (!plain(input) || !exact(input, ["repositoryRoot", "declarations"]) ||
      typeof input.repositoryRoot !== "string" || !isAbsolute(input.repositoryRoot) || !declarationsValid(input.declarations)))
    fail("extension_invalid");
  const declarations = input?.declarations ?? [];
  if (previous) {
    const installed = previous.extensions?.imports.map(({source, destination}) => ({source, destination})) ?? [];
    if (installed.length !== declarations.length || installed.some((entry, index) =>
      entry.source !== declarations[index]!.source || entry.destination !== declarations[index]!.destination))
      fail("ownership_invalid");
    // Deliberately no stat, enumeration or reads of either old source or custom output.
    return { metadata: previous.extensions, changes: [] as Change[] };
  }
  if (!declarations.length) return { metadata: undefined, changes: [] as Change[] };
  const repo = resolve(input!.repositoryRoot);
  safe(repo, "directory");
  if (!existsSync(repo)) fail("extension_invalid");
  const roots: string[] = [], imports: ExtensionImport[] = [], changes: Change[] = [];
  let total = 0, count = 0;
  for (const declaration of declarations) {
    const {source, destination} = declaration;
    if (roots.some(other => overlaps(other, destination)) || basePaths.some(path => overlaps(path, destination)))
      fail("extension_conflict");
    roots.push(destination);
    const sourceRoot = resolve(repo, source), destinationRoot = join(root, destination);
    if (overlaps(sourceRoot, root)) fail("extension_invalid");
    safe(sourceRoot, "directory"); safe(destinationRoot, "directory");
    if (!existsSync(sourceRoot)) fail("extension_invalid");
    if (existsSync(destinationRoot)) fail("extension_conflict");
    const inventory: Record<string, string> = Object.create(null);
    function walk(directory: string, relative: string, depth: number) {
      if (depth > 16) fail("extension_limit");
      const names: string[] = [], handle = opendirSync(directory);
      try {
        let entry;
        while ((entry = handle.readSync()) !== null) {
          if (++count > 1000) fail("extension_limit");
          names.push(entry.name);
        }
      } finally { handle.closeSync(); }
      for (const name of names.sort()) {
        const path = relative ? relative + "/" + name : name;
        if (!importPath(path) || !importPath(destination + "/" + path)) fail("extension_invalid");
        const sourceFile = join(directory, name), stat = lstatSync(sourceFile);
        if (stat.isSymbolicLink()) fail("extension_invalid");
        if (stat.isDirectory()) { walk(sourceFile, path, depth + 1); continue; }
        if (!stat.isFile()) fail("extension_invalid");
        if (stat.size > 1024 * 1024 || (total += stat.size) > 8 * 1024 * 1024) fail("extension_limit");
        const bytes = readFileSync(sourceFile);
        // Recheck after read so concurrently growing input cannot evade byte limits.
        if (bytes.length !== stat.size) fail("extension_invalid");
        let text: string;
        try { text = new TextDecoder("utf-8", {fatal: true, ignoreBOM: true}).decode(bytes); }
        catch { fail("extension_invalid"); }
        if (/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(text)) fail("extension_invalid");
        inventory[path] = hash(bytes);
        changes.push({path: destination + "/" + path, old: null, next: bytes.toString("base64")});
      }
    }
    walk(sourceRoot, "", 1);
    imports.push({source, destination, files: inventory});
  }
  const metadata: Extensions = {schema_version: 1, imports};
  validateExtensions(metadata, basePaths);
  return {metadata, changes};
}
function extensionFiles(manifest: Manifest) {
  return Object.fromEntries((manifest.extensions?.imports ?? []).flatMap(entry =>
    Object.entries(entry.files).map(([path, sha256]) => [entry.destination + "/" + path, sha256])));
}
function owner(root: string) {
  safe(join(root, lockName), "directory");
  safe(join(root, lockName, "owner.json"), "file");
  if (readdirSync(join(root, lockName)).join() !== "owner.json")
    fail("recovery_uncertain");
  let pid: unknown;
  try {
    const doc = JSON.parse(
      readFileSync(join(root, lockName, "owner.json"), "utf8")
    );
    if (!plain(doc) || !exact(doc, ["pid"])) fail("recovery_uncertain");
    pid = doc.pid;
  } catch {
    fail("recovery_uncertain");
  }
  if (!Number.isSafeInteger(pid) || (pid as number) < 1)
    fail("recovery_uncertain");
  try {
    process.kill(pid as number, 0);
    return true;
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === "ESRCH") return false;
    fail("busy");
  }
}
function recoveryClaim(root: string) {
  const claim = join(root, recoveryName);
  safe(claim, "directory");
  if (!existsSync(claim)) return;
  safe(join(claim, "owner.json"), "file");
  let pid: unknown;
  try {
    const doc = JSON.parse(readFileSync(join(claim, "owner.json"), "utf8"));
    if (
      !plain(doc) ||
      !exact(doc, ["recovering_pid"]) ||
      readdirSync(claim).join() !== "owner.json"
    )
      fail("recovery_uncertain");
    pid = doc.recovering_pid;
  } catch {
    fail("recovery_uncertain");
  }
  if (!Number.isSafeInteger(pid) || (pid as number) < 1)
    fail("recovery_uncertain");
  try {
    process.kill(pid as number, 0);
  } catch {
    fail("recovery_uncertain");
  }
  fail("busy");
}
function available(root: string) {
  recoveryClaim(root);
  safe(root, "directory");
  safe(join(root, lockName), "directory");
  safe(join(root, stateName), "directory");
  if (existsSync(join(root, lockName)))
    fail(owner(root) ? "busy" : "recovery_required");
  if (existsSync(join(root, stateName))) fail("recovery_required");
}
function write(root: string, path: string, base64: string, exclusive = false) {
  const target = join(root, path);
  safe(target, "file");
  mkdirSync(dirname(target), { recursive: true, mode: 0o700 });
  const staged = join(root, stateName, "replacement");
  safe(staged, "file");
  writeFileSync(staged, Buffer.from(base64, "base64"), {
    mode: 0o600,
    flag: "w",
    flush: true,
  });
  if (exclusive) {
    // Same-filesystem hard-link publication refuses a destination created after
    // preflight, including dangling symlinks; rename would overwrite owner bytes.
    linkSync(staged, target);
    unlinkSync(staged);
  } else renameSync(staged, target);
}
function restore(root: string) {
  const state = join(root, stateName);
  safe(state, "directory");
  if (
    readdirSync(state).some(
      (name) => !["journal.json", "replacement"].includes(name)
    )
  )
    fail("recovery_uncertain");
  safe(join(state, "journal.json"), "file");
  let journal: unknown;
  try {
    journal = JSON.parse(readFileSync(join(state, "journal.json"), "utf8"));
  } catch {
    fail("recovery_uncertain");
  }
  if (
    !plain(journal) ||
    !exact(journal, ["schema_version", "changes"]) ||
    journal.schema_version !== 1 ||
    !Array.isArray(journal.changes) ||
    !journal.changes.length
  )
    fail("recovery_uncertain");
  const changes = journal.changes as Change[],
    seen = new Set<string>();
  for (const c of changes) {
    if (
      !plain(c) ||
      !exact(c, ["path", "old", "next"]) ||
      typeof c.path !== "string" ||
      (c.path !== manifestName && !pathValid(c.path)) ||
      seen.has(c.path) ||
      !(c.old === null || typeof c.old === "string") ||
      typeof c.next !== "string"
    )
      fail("recovery_uncertain");
    seen.add(c.path);
    for (const value of [c.old, c.next])
      if (
        value !== null &&
        Buffer.from(value, "base64").toString("base64") !== value
      )
        fail("recovery_uncertain");
    const actual = read(join(root, c.path));
    if (actual !== c.old && actual !== c.next) fail("recovery_uncertain");
  }
  const manifestChange = changes.find((c) => c.path === manifestName);
  if (!manifestChange) fail("recovery_uncertain");
  let before: Manifest | null, after: Manifest;
  try {
    before =
      manifestChange.old === null ? null : decodeManifest(manifestChange.old);
    after = decodeManifest(manifestChange.next);
  } catch {
    fail("recovery_uncertain");
  }
  if (
    before &&
    (Object.keys(before.files).sort().join("\n") !==
      Object.keys(after.files).sort().join("\n") ||
      JSON.stringify(before.extensions) !== JSON.stringify(after.extensions) ||
      ["generator", "template", "recipe"].some(
        (key) =>
          before!.identity[key as keyof Identity] !==
          after.identity[key as keyof Identity]
      ))
  )
    fail("recovery_uncertain");
  const expected = Object.entries(after.files)
    .filter(
      ([path, e]) => e.classification === "generated" || !before?.files[path]
    )
    .map(([path]) => path)
    .concat(before ? [] : Object.keys(extensionFiles(after)))
    .concat(manifestName)
    .sort();
  if (expected.join("\n") !== [...seen].sort().join("\n"))
    fail("recovery_uncertain");
  for (const c of changes) {
    if (c.path === manifestName) continue;
    const prior = before?.files[c.path],
      next = after.files[c.path] ?? (Object.hasOwn(extensionFiles(after), c.path) ?
        {classification: "custom", sha256: extensionFiles(after)[c.path]} : undefined);
    if (
      !next ||
      hash(Buffer.from(c.next, "base64")) !== next.sha256 ||
      (prior
        ? prior.classification !== next.classification ||
          prior.classification !== "generated" ||
          c.old === null ||
          hash(Buffer.from(c.old, "base64")) !== prior.sha256
        : c.old !== null)
    )
      fail("recovery_uncertain");
  }
  safe(join(state, "replacement"), "file");
  // Derive the only children/directories that this initial text-file snapshot
  // could have created. Preflight the whole inventory before restoring any bytes.
  const directories = new Map<string, Set<string>>();
  if (!before) for (const entry of after.extensions?.imports ?? []) {
    directories.set(entry.destination, new Set());
    for (const path of Object.keys(entry.files)) {
      const parts = path.split("/");
      let directory = entry.destination;
      for (let index = 0; index < parts.length; index++) {
        directories.get(directory)!.add(parts[index]!);
        if (index < parts.length - 1) {
          directory += "/" + parts[index];
          if (!directories.has(directory)) directories.set(directory, new Set());
        }
      }
    }
  }
  try {
    for (const [directory, children] of directories) {
      const target = join(root, directory);
      safe(target, "directory");
      if (!existsSync(target)) continue;
      const handle = opendirSync(target);
      try {
        let child;
        while ((child = handle.readSync()) !== null)
          if (!children.has(child.name)) fail("recovery_uncertain");
      } finally { handle.closeSync(); }
    }
  } catch { fail("recovery_uncertain"); }
  // Every affected file and import directory is now known. Never erase unknown bytes.
  for (const c of [...changes].reverse()) {
    if (c.old === null) {
      if (existsSync(join(root, c.path))) rmSync(join(root, c.path));
    } else if (read(join(root, c.path)) !== c.old) write(root, c.path, c.old);
  }
  for (const directory of [...directories.keys()].sort((a, b) => b.length - a.length)) {
    const target = join(root, directory);
    safe(target, "directory");
    if (existsSync(target)) rmdirSync(target);
  }
}
function cleanup(root: string) {
  rmSync(join(root, stateName), { recursive: true, force: true });
  rmSync(join(root, lockName), { recursive: true });
}
/** Explicit dead-writer recovery. Unknown/live locks and changed targets are refused. */
function recoverInternal(output: string) {
  const root = resolve(output);
  safe(root, "directory");
  safe(join(root, lockName), "directory");
  safe(join(root, stateName), "directory");
  recoveryClaim(root);
  const claim = join(root, recoveryName);
  try {
    mkdirSync(claim, { mode: 0o700 });
  } catch {
    recoveryClaim(root);
    fail("recovery_uncertain");
  }
  // A crash during claim initialization is uncertain, never a stealable stale lock.
  writeFileSync(
    join(claim, "owner.json"),
    JSON.stringify({ recovering_pid: process.pid }),
    { mode: 0o600, flag: "wx", flush: true }
  );
  if (!existsSync(join(root, lockName))) {
    if (existsSync(join(root, stateName))) fail("recovery_uncertain");
    rmSync(claim, { recursive: true });
    return;
  }
  if (owner(root)) {
    rmSync(claim, { recursive: true });
    fail("busy");
  }
  if (!existsSync(join(root, stateName))) fail("recovery_uncertain");
  restore(root);
  cleanup(root);
  rmSync(claim, { recursive: true });
}
/** Build admission for the internal proof: no incomplete state or generated drift. */
function checkInternal(output: string) {
  const root = resolve(output);
  available(root);
  const previous = load(root);
  if (!previous) fail("manifest_invalid");
  for (const [path, file] of Object.entries(previous.files)) {
    const bytes = read(join(root, path));
    if (
      bytes === null ||
      (file.classification === "generated" &&
        hash(Buffer.from(bytes, "base64")) !== file.sha256)
    )
      fail("conflict");
  }
}
/** Narrow test seam runs only after a replacement; production callers omit it. */
function installInternal(
  output: string,
  files: Record<string, ServiceFile>,
  identity: Identity,
  fault?: { afterWrite: (count: number) => void },
  extensions?: ExtensionInput
) {
  const root = resolve(output);
  available(root);
  if (!identityValid(identity)) fail("identity_invalid");
  if (
    !plain(files) ||
    !Object.keys(files).length ||
    Object.keys(files).length > 1000
  )
    fail("map_invalid");
  const paths = Object.keys(files);
  for (const path of paths) {
    const file = files[path];
    if (
      !pathValid(path) ||
      !plain(file) ||
      !exact(file, ["classification", "content"]) ||
      !["seed", "generated"].includes(file.classification) ||
      typeof file.content !== "string" ||
      paths.some((p) => p.startsWith(path + "/"))
    )
      fail("map_invalid");
    safe(join(root, path), "file");
  }
  mkdirSync(root, { recursive: true, mode: 0o700 });
  try {
    mkdirSync(join(root, lockName), { mode: 0o700 });
  } catch {
    fail("busy");
  }
  let journalReady = false,
    stateCreated = false;
  try {
    writeFileSync(
      join(root, lockName, "owner.json"),
      JSON.stringify({ pid: process.pid }),
      { mode: 0o600, flag: "wx" }
    );
    // Recheck after lock acquisition: recovery may have claimed between preflight and mkdir.
    recoveryClaim(root);
    const previous = load(root);
    if (previous) {
      for (const key of ["generator", "template", "recipe"] as const)
        if (previous.identity[key] !== identity[key]) fail("identity_invalid");
      if (
        Object.keys(previous.files).sort().join("\n") !==
        paths.sort().join("\n")
      )
        fail("ownership_invalid");
    }
    const imported = extensionPlan(root, paths, extensions, previous);
    const next: Manifest = {
      schema_version: 1,
      identity,
      files: Object.create(null),
      ...(imported.metadata ? {extensions: imported.metadata} : {}),
    };
    const changes: Change[] = [];
    for (const path of paths) {
      const file = files[path],
        old = read(join(root, path)),
        prior = previous?.files[path];
      if (prior && prior.classification !== file.classification)
        fail("ownership_invalid");
      if (prior) {
        if (
          old === null ||
          (prior.classification === "generated" &&
            hash(Buffer.from(old, "base64")) !== prior.sha256)
        )
          fail("conflict");
      } else if (old !== null) fail("conflict");
      const content = Buffer.from(file.content).toString("base64");
      next.files[path] = {
        classification: file.classification,
        sha256:
          prior && file.classification === "seed"
            ? prior.sha256
            : hash(file.content),
      };
      if (!prior || file.classification === "generated")
        changes.push({ path, old, next: content });
    }
    changes.push(...imported.changes);
    changes.push({
      path: manifestName,
      old: read(join(root, manifestName)),
      next: Buffer.from(JSON.stringify(next, null, 2) + "\n").toString(
        "base64"
      ),
    });
    // Full bytes and previous bytes are staged durably in the local journal before replacement.
    mkdirSync(join(root, stateName), { mode: 0o700 });
    stateCreated = true;
    writeFileSync(
      join(root, stateName, "journal.json"),
      JSON.stringify({ schema_version: 1, changes }),
      { mode: 0o600, flag: "wx", flush: true }
    );
    journalReady = true;
    let count = 0;
    for (const change of changes) {
      write(root, change.path, change.next, change.old === null);
      fault?.afterWrite(++count);
    }
    cleanup(root);
  } catch (error) {
    if (journalReady) {
      try {
        restore(root);
        cleanup(root);
      } catch {
        fail("recovery_uncertain");
      }
      fail("install_failed");
    }
    // Only known files in directories created by this invocation may be removed.
    // Unexpected additions are uncertainty, even though no business target changed.
    const initialized = stateCreated
      ? [
          [stateName, "journal.json"],
          [lockName, "owner.json"],
        ]
      : [[lockName, "owner.json"]];
    for (const [directory, file] of initialized) {
      const path = join(root, directory);
      safe(path, "directory");
      if (readdirSync(path).some((name) => name !== file))
        fail("recovery_uncertain");
      safe(join(path, file), "file");
    }
    for (const [directory, file] of initialized) {
      rmSync(join(root, directory, file), { force: true });
      rmdirSync(join(root, directory));
    }
    throw error;
  }
}

function safeCall<T>(action: () => T): T {
  try {
    return action();
  } catch (error) {
    if (error instanceof Error && /^scaffold_[a-z_]+$/.test(error.message))
      throw error;
    fail("io_failed");
  }
}
export function recoverScaffold(output: string) {
  return safeCall(() => recoverInternal(output));
}
export function checkScaffold(output: string) {
  return safeCall(() => checkInternal(output));
}
export function installScaffold(
  output: string,
  files: Record<string, ServiceFile>,
  identity: Identity,
  fault?: { afterWrite: (count: number) => void },
  extensions?: ExtensionInput
) {
  return safeCall(() => installInternal(output, files, identity, fault, extensions));
}
