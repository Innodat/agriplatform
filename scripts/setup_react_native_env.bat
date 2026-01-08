@echo off
REM === CONFIGURE PATHS ===
set JAVA_HOME="C:\Program Files\Eclipse Adoptium\jdk-17"
set ANDROID_HOME=C:\Users\%USERNAME%\AppData\Local\Android\Sdk
set PATH="%PATH%;%JAVA_HOME%\bin;%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\emulator;%ANDROID_HOME%\cmdline-tools\latest\bin"

echo === Verifying Java ===
java -version || (echo Java not found. Please install JDK 17 and set JAVA_HOME correctly. & exit /b)

echo === Verifying Android SDK ===
adb --version || (echo ADB not found. Please install Android SDK and set ANDROID_HOME correctly. & exit /b)

echo === Checking for existing AVD ===
emulator -list-avds | findstr Pixel_6 >nul
if %errorlevel% neq 0 (
    echo No AVD found. Creating Pixel_6...
    sdkmanager --install "system-images;android-36_1;google_apis;x86_64"
    avdmanager create avd -n Pixel_6 -k "system-images;android-36_1;google_apis;x86_64" --device "pixel_6"
)

echo === Enable local ports ===
netsh interface portproxy add v4tov4 listenport=54321 listenaddress=192.168.0.113 connectport=54321 connectaddress=127.0.0.1
netsh interface portproxy add v4tov4 listenport=54322 listenaddress=192.168.0.113 connectport=54322 connectaddress=127.0.0.1
netsh interface portproxy add v4tov4 listenport=54323 listenaddress=192.168.0.113 connectport=54323 connectaddress=127.0.0.1
netsh interface portproxy add v4tov4 listenport=54324 listenaddress=192.168.0.113 connectport=54324 connectaddress=127.0.0.1


echo === Build, if needed ===
cd packages/mobile/android
mklink /J node_modules ..\node_modules
./gradlew clean
./gradlew :app:assembleDebug --stacktrace

cd packages/mobile
echo === Starting Emulator ===
start cmd /k emulator -avd Pixel_6

echo === Starting Metro Bundler ===
start cmd /k npx react-native start

echo === Building and Running App ===
npx react-native run-android

pause