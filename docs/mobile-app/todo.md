I'd like you to create a mobile app for me using React-Native, I do want to share code with package/frontend where plausible and wise, e.g. the zod schemas, react hooks and supabase access and service files.
I do want to change the name of package/frontend to web. The folder for the mobile app should be package/mobile.
I do have a mobile app at the moment that was created using next.js. It is in the fronend-mobile file.

Please also update the docs where plausible. Pheraps have a mobile tech-spec.md doc in the doc/mobile-app folder. The tech-spec.md doc can refer to this doc.

Attached are screenshots of the existing look and feel. Once logged in, the user is navigated to the receipt screen, once clicking on ADD or Edit, then the item add/update screen displays. THe screenshots is missing the suppliers fields, this should be added, you'll see this field in the zod schemas. This field should be displayed/requested as well.

Only today's captured receipts should be updatable (update/delete). Today's receipts should be highlighted for the user to know they are today's.

For the receipt scanning, I want to use the react-native-vision-camera and react-native-document-scanner-plugin. Also, the text for uploading the image should diver as it is for a mobile app now. Someting like: 'Upload from Gallery' or 'Choose from Photos'
