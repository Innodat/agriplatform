// android/settings.gradle.kts

pluginManagement {
  includeBuild("../node_modules/@react-native/gradle-plugin")
  repositories {
    gradlePluginPortal()
    google()
    mavenCentral()
  }
}

plugins {
  id("com.facebook.react.settings")
}

// 👉 Run autolinking from the app root (monorepo-aware)
configure<com.facebook.react.ReactSettingsExtension> {
  autolinkLibrariesFromCommand(
    workingDirectory = file(".."),                 // where package.json + react-native.config.js live
    lockFiles = files("../package-lock.json")     // use files("../yarn.lock") if you use Yarn
  )
}

rootProject.name = "AgriPlatformMobile"
include(":app")

// Manual link for react-native-config (workaround for new-arch CMake issue)
include(":react-native-config")
project(":react-native-config").projectDir =
  File(rootProject.projectDir, "../node_modules/react-native-config/android")