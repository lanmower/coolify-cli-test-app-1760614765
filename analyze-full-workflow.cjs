const fs = require('fs');

// Parse the user's message to extract fetch calls
const captures = `[USER'S FETCH CALLS FROM MESSAGE]`;

console.log('=== COOLIFY DEPLOYMENT WORKFLOW ===\n');

console.log('Step 1: Set Private Key');
console.log('  URL: /livewire/update');
console.log('  Component: project.new.github-private-repository-deploy-key');
console.log('  Method: setPrivateKey(4)');
console.log('  Purpose: Select SSH key for private repo access\n');

console.log('Step 2: Create Application');
console.log('  URL: /livewire/update');
console.log('  Component: project.new.github-private-repository-deploy-key');
console.log('  Updates: { repository_url, branch }');
console.log('  Calls: [{ method: "submit" }]');
console.log('  Result: Application ID okwskskwwskc8sg4sog488g8\n');

console.log('Step 3: Set Domain');
console.log('  URL: /livewire/update');
console.log('  Component: project.application.general');
console.log('  Updates: { "application.fqdn": "https://test.acc.l-inc.co.za" }');
console.log('  Purpose: Set custom domain\n');

console.log('Step 4: Save Domain Configuration');
console.log('  URL: /livewire/update');
console.log('  Component: project.application.general');
console.log('  Calls: [{ method: "submit" }]');
console.log('  Purpose: Persist domain changes\n');

console.log('Step 5: Trigger Deployment');
console.log('  URL: /livewire/update');
console.log('  Component: project.application.heading');
console.log('  Calls: [{ method: "deploy" }]');
console.log('  Result: Deployment ID vsw0gwo0c8g0g8cs440wow40\n');

console.log('Step 6: Monitor Deployment');
console.log('  URL: /livewire/update');
console.log('  Component: project.application.deployment.show');
console.log('  Calls: [{ method: "polling" }]');
console.log('  Purpose: Watch deployment progress\n');

console.log('=== KEY FINDINGS ===\n');
console.log('1. Form uses type=private-deploy-key (not public-git-repository)');
console.log('2. Must call setPrivateKey() before submitting repository');
console.log('3. Domain is configured AFTER application creation');
console.log('4. Domain requires two requests: update + submit');
console.log('5. Deployment is triggered separately via deploy() call');
console.log('6. Each step uses different Livewire components');
