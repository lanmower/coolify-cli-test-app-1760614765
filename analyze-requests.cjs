const fs = require('fs');
const requests = JSON.parse(fs.readFileSync('all-livewire-requests.json', 'utf8'));

console.log('Total requests:', requests.length);
console.log('\nAnalyzing largest requests:\n');

// Sort by size
const sorted = requests.sort((a, b) => b.postDataLength - a.postDataLength);

// Show top 3
sorted.slice(0, 3).forEach((req, i) => {
    console.log(`\n=== Request ${i+1} (${req.postDataLength} bytes) ===`);
    console.log('Time:', req.timestamp);

    try {
        const data = JSON.parse(req.postData);
        console.log('Components:', data.components?.length || 0);

        if (data.components && data.components[0]) {
            const component = data.components[0];

            // Look for updates
            if (component.updates) {
                console.log('Updates:', component.updates.length);
                component.updates.forEach(u => {
                    console.log('  -', u.type, u.payload?.method || u.payload?.name);
                });
            }

            // Show full POST data for largest
            if (i === 0) {
                console.log('\nFull POST data:');
                console.log(req.postData);
            }
        }
    } catch (e) {
        console.log('Could not parse:', e.message);
    }
});
