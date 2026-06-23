// packages/mobile/react-native.config.js
module.exports = {
  dependencies: {
    'react-native-config': {
      platforms: {
        android: null, // ✅ disable Android autolinking for RN Config
      },
    },
  },
};