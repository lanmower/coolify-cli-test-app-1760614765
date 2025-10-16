#!/usr/bin/env node

const { chromium } = require('playwright');
const fs = require('fs');

async function captureSubmit() {
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();

    const requests = [];

    page.on('request', request => {
        if (request.url().includes('/livewire/update') && request.method() === 'POST') {
            requests.push({
                url: request.url(),
                method: request.method(),
                headers: request.headers(),
                postData: request.postData()
            });
        }
    });

    console.log('🔐 Login...');
    await page.goto('https://coolify.acc.l-inc.co.za/login');
    await page.fill('input[type="email"]', process.env.U);
    await page.fill('input[type="password"]', process.env.P);
    await page.click('button[type="submit"]');
    await page.waitForURL(/coolify.acc.l-inc.co.za\/$/, { timeout: 10000 });

    console.log('📄 Navigate to form...');
    await page.goto('https://coolify.acc.l-inc.co.za/project/mcssok0k4s00kc0sg4g4ow0o/environment/i0kog8s80kw04gwo4gsskk08/new?type=public&destination=mks0ss0wkgko0c8cocogssoc&server_id=0');

    console.log('⏳ Waiting for page to load...');
    await page.waitForTimeout(4000);

    console.log('📝 Please fill in the form manually and click submit...');
    console.log('   Repository: https://github.com/lanmower/coolify-cli-test-app-1760614765');
    console.log('   Branch: master');
    console.log('   Port: 3000');
    console.log('   Domain: coolify-cli-test-app.acc.l-inc.co.za');
    console.log('\n⏳ Waiting for form submission (60 seconds)...\n');

    await page.waitForTimeout(60000);

    console.log(`\n📊 Captured ${requests.length} Livewire requests`);

    const submitRequest = requests.find(r => r.postData && r.postData.includes('submit'));
    if (submitRequest) {
        console.log('\n✅ Found submit request!');
        fs.writeFileSync('submit-request.json', JSON.stringify(submitRequest, null, 2));
        console.log('💾 Saved to submit-request.json');

        console.log('\nPOST Data:');
        console.log(submitRequest.postData);
    } else {
        console.log('\n⚠️  No submit request found');
        console.log('All requests:', requests.length);
    }

    await browser.close();
}

captureSubmit().catch(console.error);
