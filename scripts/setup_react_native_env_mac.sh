# Install Xcode
# Have an Apple Developer Account, and ideally, "Paid ($99/yr): distribute to TestFlight/App Store"

# Symlink node modules:
cd packages/mobile
ln -s ../node_modules node_modules

# Add to packages/mobile/metro.config.js:
const path = require('path');

module.exports = {
  watchFolders: [
    path.resolve(__dirname, '..', '..'),
  ],
};

# In /ios/Podfile:
project '../mobile.xcodeproj'
pod 'React-Codegen', :path => '../..'

# Install cocoapods
sudo gem install cocoapods


cd packages/mobile/ios
pod install


# Metro
cd packages/mobile
npx react-native start

# Run on iPhone: Connect your iPhone → unlock it → trust the Mac.
npx react-native run-ios --device
# If there are multiple devices: npx react-native run-ios --device "Christoff’s iPhone"
# Or, run the simulator:
npx react-native run-ios