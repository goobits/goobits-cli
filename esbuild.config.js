/**
 * ESBuild configuration for TestTSCLI
 * Ultra-fast TypeScript compilation and bundling
 */

import { build } from 'esbuild';
import { nodeExternalsPlugin } from 'esbuild-node-externals';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

// ES Module equivalents of __filename and __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const isProduction = process.env.NODE_ENV === 'production';

/**
 * Shared build configuration
 */
const sharedConfig = {
  bundle: true,
  minify: isProduction,
  sourcemap: !isProduction,
  platform: 'node',
  target: 'node16',
  format: 'cjs',
  tsconfig: './tsconfig.build.json',
  
  // Enable tree shaking
  treeShaking: true,
  
  // Optimize for CLI usage
  keepNames: true,
  
  // External dependencies
  plugins: [
    nodeExternalsPlugin({
      packagePath: './package.json',
      allowList: [],
    }),
  ],
  
  // Define environment variables
  define: {
    'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development'),
  },
  
  // Logging
  logLevel: 'info',
  color: true,
};

/**
 * Build configurations for different targets
 */
const builds = [
  // Main library build
  {
    ...sharedConfig,
    entryPoints: ['./cli.ts'],
    outfile: './dist/index.js',
    format: 'cjs',
  },
  
  // ESM build
  {
    ...sharedConfig,
    entryPoints: ['./cli.ts'],
    outfile: './dist/index.mjs',
    format: 'esm',
  },
  
  // CLI binary build
  {
    ...sharedConfig,
    entryPoints: ['./bin/cli.ts'],
    outfile: './dist/bin/cli.js',
    banner: {
      js: '#!/usr/bin/env node',
    },
  },
];

/**
 * Development build with watch mode
 */
async function buildDev() {
  console.log('🔨 Building in development mode with watch...');
  
  for (const config of builds) {
    const ctx = await build({
      ...config,
      watch: {
        onRebuild(error, result) {
          if (error) {
            console.error(`❌ Watch build failed:`, error);
          } else {
            console.log(`✅ Watch build succeeded:`, config.outfile);
          }
        },
      },
    });
    
    console.log(`👀 Watching ${config.entryPoints[0]} -> ${config.outfile}`);
  }
}

/**
 * Production build
 */
async function buildProd() {
  console.log('🏗️  Building for production...');
  
  try {
    for (const config of builds) {
      await build(config);
      console.log(`✅ Built ${config.entryPoints[0]} -> ${config.outfile}`);
    }
    
    console.log('🎉 Production build completed!');
  } catch (error) {
    console.error('❌ Production build failed:', error);
    process.exit(1);
  }
}

/**
 * Development server with fast rebuild
 */
async function serve() {
  console.log('🚀 Starting development server...');
  
  const ctx = await build({
    ...sharedConfig,
    entryPoints: ['./cli.ts'],
    outfile: './dist/dev/index.js',
    watch: true,
    
    plugins: [
      ...sharedConfig.plugins,
      {
        name: 'dev-server',
        setup(build) {
          build.onEnd((result) => {
            if (result.errors.length === 0) {
              console.log('🔄 Development build updated');
            }
          });
        },
      },
    ],
  });
  
  console.log('📡 Development server running. Press Ctrl+C to stop.');
}

/**
 * Bundle analyzer
 */
async function analyze() {
  console.log('📊 Analyzing bundle...');
  
  await build({
    ...sharedConfig,
    entryPoints: ['./cli.ts'],
    outfile: './dist/analysis/index.js',
    metafile: true,
    write: false,
  }).then(async (result) => {
    const { analyzeMetafile } = await import('esbuild');
    console.log(analyzeMetafile(result.metafile));
  });
}

/**
 * Type checking without emit
 */
async function typeCheck() {
  console.log('🔍 Type checking...');
  
  const { execSync } = await import('child_process');
  
  try {
    execSync('tsc --noEmit', { stdio: 'inherit', cwd: __dirname });
    console.log('✅ Type checking passed');
  } catch (error) {
    console.error('❌ Type checking failed');
    process.exit(1);
  }
}

// Export configurations and functions
export {
  builds,
  sharedConfig,
  buildDev,
  buildProd,
  serve,
  analyze,
  typeCheck,
};

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  
  switch (command) {
    case 'dev':
    case 'watch':
      buildDev();
      break;
      
    case 'prod':
    case 'production':
      buildProd();
      break;
      
    case 'serve':
      serve();
      break;
      
    case 'analyze':
      analyze();
      break;
      
    case 'typecheck':
      typeCheck();
      break;
      
    default:
      console.log('Available commands:');
      console.log('  dev/watch    - Build with watch mode');
      console.log('  prod         - Production build');
      console.log('  serve        - Development server');
      console.log('  analyze      - Bundle analysis');
      console.log('  typecheck    - Type checking only');
      break;
  }
}