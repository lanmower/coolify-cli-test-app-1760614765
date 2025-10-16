#!/usr/bin/env node

const CoolifyDeploy = require('./coolify-deploy.cjs');

async function testAppCreation() {
    const cli = new CoolifyDeploy();

    try {
        await cli.login();
        await cli.createProject();
        await cli.getEnvironment();

        console.log('\n🧪 Testing application creation...');
        console.log(`📊 Project: ${cli.projectId}`);
        console.log(`📊 Environment: ${cli.environmentId}`);

        // Navigate to environment page to check for applications
        const envPage = await cli.request(`${cli.baseURL}/project/${cli.projectId}/environment/${cli.environmentId}`);

        // Look for application links
        const appMatches = [...envPage.raw.matchAll(/\/application\/([a-z0-9]{24})/g)];

        if (appMatches.length > 0) {
            console.log(`\n✅ Found ${appMatches.length} application(s):`);
            const apps = [...new Set(appMatches.map(m => m[1]))];
            apps.forEach((appId, i) => {
                console.log(`   ${i + 1}. ${cli.baseURL}/project/${cli.projectId}/application/${appId}`);
            });
        } else {
            console.log('\n📝 No applications found yet');
        }

        // Try to create application
        console.log('\n🚀 Attempting to create new application...');
        await cli.createApplication();

    } catch (error) {
        console.error('\n❌ Error:', error.message);
    }
}

testAppCreation();
