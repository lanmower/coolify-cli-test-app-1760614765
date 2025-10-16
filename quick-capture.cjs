#!/usr/bin/env node

const { chromium } = require('playwright');
const fs = require('fs');

async function quickCapture() {
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    let livewirePost = null;

    // Capture POST to /livewire/update
    page.on('request', request => {
        if (request.url().includes('/livewire/update') && request.method() === 'POST') {
            const postData = request.postData();
            if (postData && postData.includes('submit')) {
                livewirePost = {
                    url: request.url(),
                    headers: request.headers(),
                    postData: postData
                };
                console.log('\n✅ CAPTURED FORM SUBMISSION!');
                console.log('POST Data length:', postData.length);

                // Save to file
                fs.writeFileSync('livewire-post.json', JSON.stringify(livewirePost, null, 2));
                console.log('💾 Saved to livewire-post.json');
            }
        }
    });

    try {
        // Login
        console.log('🔐 Logging in...');
        await page.goto('https://coolify.acc.l-inc.co.za/login');
        await page.fill('input[type="email"]', process.env.U);
        await page.fill('input[type="password"]', process.env.P);
        await page.click('button[type="submit"]');
        await page.waitForURL('https://coolify.acc.l-inc.co.za/', { timeout: 10000 });
        console.log('✅ Logged in');

        // Go directly to the form URL (with query params)
        console.log('\n📄 Loading form...');
        const formUrl = 'https://coolify.acc.l-inc.co.za/project/mcssok0k4s00kc0sg4g4ow0o/environment/i0kog8s80kw04gwo4gsskk08/new?type=public&destination=mks0ss0wkgko0c8cocogssoc&server_id=0';
        await page.goto(formUrl);
        await page.waitForTimeout(2000);

        console.log('\n📝 Filling form...');
        await page.fill('input[name="public_repository_url"]', 'https://github.com/lanmower/coolify-cli-test-app-1760614765');
        await page.fill('input[name="git_branch"]', 'master');
        await page.fill('input[name="ports_exposes"]', '3000');
        await page.fill('input[name="domains"]', 'coolify-cli-test-app.acc.l-inc.co.za');

        console.log('\n🚀 Clicking submit...');
        await page.click('button[type="submit"]');

        // Wait for the POST request to be captured
        await page.waitForTimeout(3000);

        if (livewirePost) {
            console.log('\n✅ Capture successful!');
            console.log('\nPOST Data Preview:');
            console.log(livewirePost.postData.substring(0, 500));
        } else {
            console.log('\n⚠️  No POST captured yet');
        }

        await browser.close();

    } catch (error) {
        console.error('❌ Error:', error.message);
        await browser.close();
    }
}

quickCapture();
