const path = require('path');
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

const isAnalyze = process.env.ANALYZE === 'true';

module.exports = {
  mode: 'production',
  target: ['web', 'es2020'],
  entry: './frontend/src/index.ts',
  output: {
    filename: '[name].bundle.js',
    chunkFilename: '[name].chunk.js',
    path: path.resolve(__dirname, 'backend/static/dist'),
    clean: true,
    publicPath: '/static/dist/',
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/,
      },
    ],
  },
  optimization: {
    minimize: true,
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'initial',
          priority: 10,
          reuseExistingChunk: true,
        },
      },
    },
  },
  plugins: isAnalyze ? [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      reportFilename: 'bundle-report.html',
      openAnalyzer: true,
    }),
  ] : [],
};
