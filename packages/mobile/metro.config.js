// repo-root/packages/mobile/metro.config.js
const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
const path = require('path');

const projectRoot = __dirname;
// mobile is at repo-root/packages/mobile -> repoRoot is two levels up
const repoRoot = path.resolve(projectRoot, '..', '..');

const extraConfig = {
  projectRoot,
  watchFolders: [repoRoot], // allow resolving files from the repo root (e.g., packages/shared)
  resolver: {
    // Follow symlinks and files outside the project root
    unstable_enableSymlinks: true,

    // Let Metro look for node_modules both locally and at the monorepo root
    nodeModulesPaths: [
      path.join(projectRoot, 'node_modules'),
      path.join(repoRoot, 'node_modules'),
    ],

    // Ensure TS/JS files are resolved consistently
    sourceExts: ['ts', 'tsx', 'js', 'jsx', 'json'],
  },
  // transformer: { } // keep defaults unless you have custom plugins
};

// Merge your defaults with our additions (preserves all RN defaults you currently rely on)
module.exports = mergeConfig(getDefaultConfig(projectRoot), extraConfig);