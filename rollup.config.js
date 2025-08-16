/**
 * Rollup configuration for TestTSCLI
 * Optimized for ES modules and tree shaking
 */

import typescript from '@rollup/plugin-typescript';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import terser from '@rollup/plugin-terser';
import { fileURLToPath } from 'url';
import { dirname, resolve as pathResolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isProduction = process.env.NODE_ENV === 'production';

const sharedPlugins = [
  resolve({
    preferBuiltins: true,
    exportConditions: ['node'],
  }),
  commonjs(),
  json(),
  typescript({
    tsconfig: './tsconfig.build.json',
    declaration: true,
    declarationDir: './dist/types',
    sourceMap: !isProduction,
  }),
];

if (isProduction) {
  sharedPlugins.push(
    terser({
      keep_classnames: true,
      keep_fnames: true,
      mangle: {
        keep_classnames: true,
        keep_fnames: true,
      },
    })
  );
}

export default [
  // Main library build
  {
    input: 'index.ts',
    output: [
      {
        file: 'dist/index.js',
        format: 'cjs',
        sourcemap: !isProduction,
        exports: 'auto',
      },
      {
        file: 'dist/index.mjs',
        format: 'es',
        sourcemap: !isProduction,
      },
    ],
    plugins: sharedPlugins,
    external: [
      'commander',
      'chalk',
      'reflect-metadata',
      'fs',
      'fs/promises',
      'path',
      'url',
      'child_process',
      'os',
      'util',
    ],
  },
  
  // CLI binary build
  {
    input: 'bin/cli.ts',
    output: {
      file: 'dist/bin/cli.js',
      format: 'cjs',
      sourcemap: !isProduction,
      banner: '#!/usr/bin/env node',
    },
    plugins: sharedPlugins,
    external: [
      'commander',
      'chalk',
      'reflect-metadata',
      'fs',
      'fs/promises',
      'path',
      'url',
      'child_process',
      'os',
      'util',
    ],
  },
];