/**
 * Webpack configuration for Complex CLI Test Tool
 * Optimized for CLI application bundling
 */

const path = require('path');
const nodeExternals = require('webpack-node-externals');

/** @type {import('webpack').Configuration} */
module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';
  
  return {
    target: 'node',
    mode: isProduction ? 'production' : 'development',
    
    entry: {
      index: './index.ts',
      cli: './bin/cli.ts',
    },
    
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: '[name].js',
      clean: true,
      libraryTarget: 'commonjs2',
    },
    
    resolve: {
      extensions: ['.ts', '.js'],
      alias: {
        '@': path.resolve(__dirname),
        '@lib': path.resolve(__dirname, 'lib'),
        '@types': path.resolve(__dirname, 'types'),
        '@commands': path.resolve(__dirname, 'commands'),
      },
    },
    
    module: {
      rules: [
        {
          test: /\.ts$/,
          use: [
            {
              loader: 'ts-loader',
              options: {
                configFile: 'tsconfig.build.json',
                transpileOnly: isProduction ? false : true,
              },
            },
          ],
          exclude: /node_modules/,
        },
        {
          test: /\.js$/,
          use: 'source-map-loader',
          enforce: 'pre',
        },
      ],
    },
    
    externals: [
      nodeExternals({
        // Allow bundling of specific packages if needed
        allowlist: [],
      }),
    ],
    
    plugins: [
      // Add banner to output files
      new (require('webpack')).BannerPlugin({
        banner: '#!/usr/bin/env node',
        raw: true,
        entryOnly: true,
        test: /cli\.js$/,
      }),
    ],
    
    optimization: {
      minimize: isProduction,
      minimizer: isProduction ? [
        new (require('terser-webpack-plugin'))({
          terserOptions: {
            keep_classnames: true,
            keep_fnames: true,
            mangle: {
              keep_classnames: true,
              keep_fnames: true,
            },
          },
        }),
      ] : [],
      
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10,
            reuseExistingChunk: true,
          },
          common: {
            name: 'common',
            minChunks: 2,
            priority: 5,
            reuseExistingChunk: true,
          },
        },
      },
    },
    
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    
    stats: {
      colors: true,
      errorDetails: true,
      modules: false,
      chunks: false,
      children: false,
    },
    
    performance: {
      hints: isProduction ? 'warning' : false,
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    },
  };
};