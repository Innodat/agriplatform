const {defineConfig}=require('@playwright/test');
process.env.PLAYWRIGHT_NO_COPY_PROMPT='1';
if(!process.env.SCRIBESWELL_SIGNUP_FIXTURE)throw Error('Explicit newly owned signup fixture required');
module.exports=defineConfig({testDir:'tests',testMatch:'studies-signup.integration.cjs',workers:1,retries:0,timeout:240000,reporter:[[require.resolve('./tests/studies-owner-reporter.cjs')]],outputDir:require('path').join(require('path').dirname(process.env.SCRIBESWELL_SIGNUP_FIXTURE),'signup-browser-output'),use:{baseURL:'http://localhost:5192',headless:true,trace:'off',video:'off',screenshot:'off'}});
