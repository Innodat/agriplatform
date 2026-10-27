const {defineConfig}=require('@playwright/test');
// Do not capture a private DOM snapshot in automatic failure context.
process.env.PLAYWRIGHT_NO_COPY_PROMPT='1';
if(!process.env.SCRIBESWELL_OWNER_FIXTURE)throw Error('Explicit newly owned fixture required');
module.exports=defineConfig({testDir:'tests',testMatch:'studies-owner.integration.cjs',workers:1,retries:0,timeout:90000,reporter:[[require.resolve('./tests/studies-owner-reporter.cjs')]],outputDir:require('path').join(require('path').dirname(process.env.SCRIBESWELL_OWNER_FIXTURE),'browser-output'),use:{baseURL:'http://localhost:5192',headless:true,trace:'off',video:'off',screenshot:'off'}});
