const path = require('path')

module.exports = {
  presets: ['module:@react-native/babel-preset'],
  plugins: [
    ['module-resolver', {
      root: ['./'],
      extensions: ['.ts', '.tsx', '.js', '.jsx', '.json'],
      alias: {
        '@agriplatform/shared': path.resolve(__dirname, '..', 'shared')
      }
    }],
    'react-native-reanimated/plugin', // Must be last
  ]
};
