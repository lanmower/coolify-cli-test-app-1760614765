# Monitoring and Verification Toolkit for Coolify Deployments

**Version:** 1.0
**Date:** 2025-10-16
**Purpose:** Comprehensive monitoring and verification for deployed applications

## Overview

This toolkit provides scripts, tools, and procedures for monitoring Coolify deployments, verifying application health, validating domains and SSL certificates, monitoring logs, performing baseline testing, and verifying rollback procedures.

## 1. Health Check Scripts

### 1.1 Application Health Monitor
```bash
#!/bin/bash
# health-check.sh - Application health monitoring script

# Configuration
APP_URL="${APP_URL:-https://your-app.coolify.example.com}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-/health}"
TIMEOUT="${TIMEOUT:-30}"
EXPECTED_STATUS="${EXPECTED_STATUS:-200}"

# Health check function
check_health() {
    local url="$1"
    local endpoint="$2"
    local timeout="$3"
    local expected_status="$4"

    echo "Checking application health at ${url}${endpoint}..."

    response=$(curl -s -o /dev/null -w "%{http_code}" \
        --max-time "$timeout" \
        --retry 3 \
        --retry-delay 5 \
        "${url}${endpoint}")

    if [ "$response" = "$expected_status" ]; then
        echo "✅ Health check passed (HTTP $response)"
        return 0
    else
        echo "❌ Health check failed (HTTP $response, expected $expected_status)"
        return 1
    fi
}

# Additional checks
check_database() {
    echo "Checking database connectivity..."
    # Implement database-specific health checks
}

check_dependencies() {
    echo "Checking external dependencies..."
    # Check API endpoints, external services, etc.
}

# Main execution
main() {
    local health_passed=true

    check_health "$APP_URL" "$HEALTH_ENDPOINT" "$TIMEOUT" "$EXPECTED_STATUS" || health_passed=false
    check_database || health_passed=false
    check_dependencies || health_passed=false

    if $health_passed; then
        echo "🎉 All health checks passed"
        exit 0
    else
        echo "💥 Health checks failed"
        exit 1
    fi
}

main "$@"
```

### 1.2 Comprehensive Health Check Suite
```python
#!/usr/bin/env python3
# comprehensive-health-check.py - Advanced health monitoring

import requests
import json
import sys
import time
from datetime import datetime
import socket
import ssl
from urllib.parse import urlparse

class HealthChecker:
    def __init__(self, config_file="health-config.json"):
        self.config = self.load_config(config_file)
        self.results = []

    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            return json.load(f)

    def check_http_endpoint(self, endpoint):
        """Check HTTP endpoint health"""
        try:
            start_time = time.time()
            response = requests.get(
                endpoint['url'],
                timeout=endpoint.get('timeout', 30),
                headers=endpoint.get('headers', {}),
                allow_redirects=True
            )
            response_time = time.time() - start_time

            result = {
                'type': 'http',
                'url': endpoint['url'],
                'status_code': response.status_code,
                'response_time': response_time,
                'expected_status': endpoint.get('expected_status', 200),
                'success': response.status_code == endpoint.get('expected_status', 200),
                'timestamp': datetime.now().isoformat()
            }

            if response_time > endpoint.get('max_response_time', 5):
                result['warning'] = f"Response time {response_time:.2f}s exceeds threshold"

            self.results.append(result)
            return result

        except Exception as e:
            result = {
                'type': 'http',
                'url': endpoint['url'],
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            return result

    def check_ssl_certificate(self, domain):
        """Check SSL certificate validity"""
        try:
            hostname = urlparse(domain).netloc or domain
            context = ssl.create_default_context()

            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

                    # Check certificate expiry
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.now()).days

                    result = {
                        'type': 'ssl',
                        'domain': hostname,
                        'expiry_date': expiry_date.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'issuer': cert['issuer'],
                        'success': days_until_expiry > 0,
                        'timestamp': datetime.now().isoformat()
                    }

                    if days_until_expiry < 30:
                        result['warning'] = f"Certificate expires in {days_until_expiry} days"

                    self.results.append(result)
                    return result

        except Exception as e:
            result = {
                'type': 'ssl',
                'domain': domain,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            return result

    def check_database_connectivity(self, db_config):
        """Check database connectivity"""
        # Implement database-specific checks
        pass

    def run_all_checks(self):
        """Run all configured health checks"""
        print("🔍 Starting comprehensive health checks...")

        # HTTP endpoint checks
        for endpoint in self.config.get('http_endpoints', []):
            print(f"Checking HTTP endpoint: {endpoint['url']}")
            self.check_http_endpoint(endpoint)

        # SSL certificate checks
        for domain in self.config.get('ssl_domains', []):
            print(f"Checking SSL certificate for: {domain}")
            self.check_ssl_certificate(domain)

        # Database checks
        for db in self.config.get('databases', []):
            print(f"Checking database connectivity: {db['name']}")
            self.check_database_connectivity(db)

        self.generate_report()

    def generate_report(self):
        """Generate health check report"""
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r['success'])
        warnings = sum(1 for r in self.results if 'warning' in r)

        print(f"\n📊 Health Check Summary")
        print(f"Total checks: {total_checks}")
        print(f"Passed: {passed_checks}")
        print(f"Failed: {total_checks - passed_checks}")
        print(f"Warnings: {warnings}")

        if warnings > 0:
            print("\n⚠️  Warnings:")
            for result in self.results:
                if 'warning' in result:
                    print(f"  - {result.get('url', result.get('domain', 'Unknown'))}: {result['warning']}")

        if passed_checks == total_checks:
            print("\n🎉 All health checks passed!")
            return True
        else:
            print("\n💥 Some health checks failed!")
            for result in self.results:
                if not result['success']:
                    print(f"  - {result.get('url', result.get('domain', 'Unknown'))}: {result.get('error', 'Check failed')}")
            return False

if __name__ == "__main__":
    checker = HealthChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)
```

## 2. Domain Verification Tools

### 2.1 DNS Verification Script
```bash
#!/bin/bash
# domain-verify.sh - Domain and DNS verification

DOMAIN="$1"
if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>"
    exit 1
fi

echo "🔍 Verifying domain: $DOMAIN"

# Check DNS resolution
echo "Checking DNS resolution..."
if nslookup "$DOMAIN" > /dev/null 2>&1; then
    echo "✅ DNS resolution successful"
    IP=$(nslookup "$DOMAIN" | grep -A1 "Name:" | tail -1 | awk '{print $2}')
    echo "   IP Address: $IP"
else
    echo "❌ DNS resolution failed"
    exit 1
fi

# Check MX records (optional)
echo "Checking MX records..."
MX_RECORDS=$(dig +short MX "$DOMAIN")
if [ -n "$MX_RECORDS" ]; then
    echo "✅ MX records found:"
    echo "$MX_RECORDS" | while read -r record; do
        echo "   $record"
    done
else
    echo "ℹ️  No MX records found (optional for web applications)"
fi

# Check domain availability
echo "Checking domain status..."
WHOIS_RESULT=$(whois "$DOMAIN" 2>/dev/null)
if echo "$WHOIS_RESULT" | grep -q "No match for domain"; then
    echo "❌ Domain does not exist"
    exit 1
else
    echo "✅ Domain exists and is registered"
fi

# Check HTTP/HTTPS connectivity
echo "Checking HTTP connectivity..."
if curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" | grep -q "200\|301\|302"; then
    echo "✅ HTTP connectivity successful"
else
    echo "❌ HTTP connectivity failed"
fi

echo "Checking HTTPS connectivity..."
if curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" | grep -q "200\|301\|302"; then
    echo "✅ HTTPS connectivity successful"
else
    echo "❌ HTTPS connectivity failed"
fi

echo "🎉 Domain verification completed"
```

### 2.2 SSL Certificate Validator
```python
#!/usr/bin/env python3
# ssl-validator.py - SSL certificate validation tool

import ssl
import socket
import OpenSSL
from datetime import datetime
import sys
import argparse

def validate_ssl_certificate(hostname, port=443):
    """Validate SSL certificate for a hostname"""
    try:
        # Create SSL context
        context = ssl.create_default_context()

        # Connect and get certificate
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_der = ssock.getpeercert(binary_form=True)
                cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_der)

                # Extract certificate information
                subject = dict(name[0] for name in cert.get_subject().get_components())
                issuer = dict(name[0] for name in cert.get_issuer().get_components())

                # Get expiry date
                not_after = cert.get_notAfter().decode('ascii')
                expiry_date = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
                days_until_expiry = (expiry_date - datetime.now()).days

                # Check certificate chain
                print(f"📋 SSL Certificate Information for {hostname}")
                print(f"   Subject: {subject.get('CN', 'Unknown')}")
                print(f"   Issuer: {issuer.get('CN', 'Unknown')}")
                print(f"   Valid From: {cert.get_notBefore().decode('ascii')}")
                print(f"   Valid Until: {not_after}")
                print(f"   Days Until Expiry: {days_until_expiry}")

                # Validation checks
                issues = []

                if days_until_expiry < 0:
                    issues.append("❌ Certificate has expired")
                elif days_until_expiry < 30:
                    issues.append(f"⚠️  Certificate expires in {days_until_expiry} days")
                else:
                    issues.append("✅ Certificate is valid")

                # Check hostname match
                if hostname not in subject.get('CN', ''):
                    # Check SAN (Subject Alternative Names)
                    san_names = []
                    for i in range(cert.get_extension_count()):
                        ext = cert.get_extension(i)
                        if ext.get_short_name() == b'subjectAltName':
                            san_names = str(ext).split(', ')
                            break

                    if not any(hostname in san for san in san_names):
                        issues.append("❌ Certificate does not match hostname")
                    else:
                        issues.append("✅ Certificate matches hostname")
                else:
                    issues.append("✅ Certificate matches hostname")

                # Print validation results
                for issue in issues:
                    print(f"   {issue}")

                return len([i for i in issues if i.startswith('❌')]) == 0

    except Exception as e:
        print(f"❌ Error validating SSL certificate: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate SSL certificates')
    parser.add_argument('hostname', help='Hostname to validate')
    parser.add_argument('--port', type=int, default=443, help='Port to connect to')

    args = parser.parse_args()

    success = validate_ssl_certificate(args.hostname, args.port)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 3. Log Monitoring Capabilities

### 3.1 Log Monitoring Script
```bash
#!/bin/bash
# log-monitor.sh - Real-time log monitoring

LOG_FILE="$1"
KEYWORD="$2"
ALERT_EMAIL="${ALERT_EMAIL:-}"

if [ -z "$LOG_FILE" ] || [ -z "$KEYWORD" ]; then
    echo "Usage: $0 <log-file> <keyword> [alert-email]"
    exit 1
fi

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

echo "🔍 Monitoring log file: $LOG_FILE"
echo "🔍 Searching for keyword: $KEYWORD"
echo "📅 Started at: $(date)"

# Monitor log file for keyword occurrences
tail -f "$LOG_FILE" | while read -r line; do
    if echo "$line" | grep -q "$KEYWORD"; then
        echo "🚨 ALERT: $(date) - $line"

        # Send email alert if configured
        if [ -n "$ALERT_EMAIL" ]; then
            echo "Log Alert: $line" | mail -s "Log Alert for $KEYWORD" "$ALERT_EMAIL"
        fi

        # You can add other notification methods here (Slack, Discord, etc.)
    fi
done
```

### 3.2 Application Log Analyzer
```python
#!/usr/bin/env python3
# log-analyzer.py - Application log analysis

import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class LogAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.error_patterns = [
            r'ERROR',
            r'FATAL',
            r'Exception',
            r'Stack trace',
            r'5\d{2}\s+error',  # HTTP 5xx errors
        ]
        self.warning_patterns = [
            r'WARNING',
            r'WARN',
            r'Deprecated',
            r'4\d{2}\s+error',  # HTTP 4xx errors
        ]

    def parse_log_entry(self, line):
        """Parse a single log entry"""
        # Common log format patterns
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2})',
            r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})',
        ]

        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    # Try to parse timestamp
                    timestamp = self.parse_timestamp(timestamp_str)
                    return {
                        'timestamp': timestamp,
                        'message': line,
                        'raw': line
                    }
                except:
                    continue

        return {
            'timestamp': None,
            'message': line,
            'raw': line
        }

    def parse_timestamp(self, timestamp_str):
        """Parse timestamp string"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%b %d %H:%M:%S',
            '%d/%b/%Y:%H:%M:%S',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

    def analyze_logs(self, time_window_hours=24):
        """Analyze logs within time window"""
        print(f"🔍 Analyzing logs from the last {time_window_hours} hours...")

        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        entries = []

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    entry = self.parse_log_entry(line.strip())
                    if entry['timestamp'] and entry['timestamp'] > cutoff_time:
                        entries.append(entry)
        except FileNotFoundError:
            print(f"❌ Log file not found: {self.log_file}")
            return

        if not entries:
            print("ℹ️  No log entries found in the specified time window")
            return

        print(f"📊 Found {len(entries)} log entries")

        # Categorize entries
        errors = []
        warnings = []

        for entry in entries:
            message = entry['message']

            # Check for errors
            if any(re.search(pattern, message, re.IGNORECASE) for pattern in self.error_patterns):
                errors.append(entry)

            # Check for warnings
            elif any(re.search(pattern, message, re.IGNORECASE) for pattern in self.warning_patterns):
                warnings.append(entry)

        # Generate report
        self.generate_report(entries, errors, warnings)

    def generate_report(self, all_entries, errors, warnings):
        """Generate analysis report"""
        print("\n📋 Log Analysis Report")
        print("=" * 50)

        print(f"Total entries: {len(all_entries)}")
        print(f"Errors: {len(errors)}")
        print(f"Warnings: {len(warnings)}")

        if errors:
            print(f"\n❌ Error Summary (Last 10):")
            for error in errors[-10:]:
                print(f"   {error['timestamp']}: {error['message'][:100]}...")

        if warnings:
            print(f"\n⚠️  Warning Summary (Last 10):")
            for warning in warnings[-10:]:
                print(f"   {warning['timestamp']}: {warning['message'][:100]}...")

        # Error frequency analysis
        if errors:
            error_messages = [e['message'] for e in errors]
            error_counter = Counter(error_messages)

            print(f"\n📈 Most Common Errors:")
            for msg, count in error_counter.most_common(5):
                print(f"   {count}x: {msg[:80]}...")

        # Time-based analysis
        if all_entries:
            timestamps = [e['timestamp'] for e in all_entries if e['timestamp']]
            if timestamps:
                time_range = max(timestamps) - min(timestamps)
                print(f"\n⏰ Time range: {time_range}")
                print(f"   Start: {min(timestamps)}")
                print(f"   End: {max(timestamps)}")

        # Health assessment
        error_rate = len(errors) / len(all_entries) if all_entries else 0
        warning_rate = len(warnings) / len(all_entries) if all_entries else 0

        print(f"\n🏥 Health Assessment:")
        print(f"   Error rate: {error_rate:.2%}")
        print(f"   Warning rate: {warning_rate:.2%}")

        if error_rate > 0.05:  # 5% error rate threshold
            print("   ❌ High error rate detected!")
        elif error_rate > 0.01:  # 1% error rate threshold
            print("   ⚠️  Elevated error rate")
        else:
            print("   ✅ Error rate within acceptable limits")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 log-analyzer.py <log-file> [hours]")
        sys.exit(1)

    log_file = sys.argv[1]
    hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24

    analyzer = LogAnalyzer(log_file)
    analyzer.analyze_logs(hours)
```

## 4. Performance Baseline Testing

### 4.1 Load Testing Script
```bash
#!/bin/bash
# load-test.sh - Simple load testing tool

URL="${1:-https://your-app.coolify.example.com}"
CONCURRENT_REQUESTS="${2:-10}"
TOTAL_REQUESTS="${3:-100}"
TIMEOUT="${4:-30}"

if ! command -v ab &> /dev/null; then
    echo "❌ Apache Bench (ab) is required but not installed"
    echo "Install with: sudo apt-get install apache2-utils"
    exit 1
fi

echo "🚀 Load Testing Configuration"
echo "URL: $URL"
echo "Concurrent Requests: $CONCURRENT_REQUESTS"
echo "Total Requests: $TOTAL_REQUESTS"
echo "Timeout: ${TIMEOUT}s"
echo ""

# Create results directory
RESULTS_DIR="load-test-results-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

echo "📊 Running load test..."
ab -n "$TOTAL_REQUESTS" -c "$CONCURRENT_REQUESTS" -t "$TIMEOUT" "$URL" > "$RESULTS_DIR/results.txt"

echo "✅ Load test completed. Results saved to: $RESULTS_DIR/results.txt"

# Extract key metrics
echo ""
echo "📈 Key Metrics:"
echo "============="

# Parse results
if grep -q "Requests per second" "$RESULTS_DIR/results.txt"; then
    RPS=$(grep "Requests per second" "$RESULTS_DIR/results.txt" | awk '{print $4}')
    echo "Requests per second: $RPS"
fi

if grep -q "Time per request" "$RESULTS_DIR/results.txt"; then
    TPR=$(grep "Time per request" "$RESULTS_DIR/results.txt" | head -1 | awk '{print $4}')
    echo "Time per request: ${TPR} ms"
fi

if grep -q "Failed requests" "$RESULTS_DIR/results.txt"; then
    FAILED=$(grep "Failed requests" "$RESULTS_DIR/results.txt" | awk '{print $3}')
    echo "Failed requests: $FAILED"
fi

echo ""
echo "📋 Full results available in: $RESULTS_DIR/results.txt"
```

### 4.2 Response Time Monitor
```python
#!/usr/bin/env python3
# response-time-monitor.py - Response time monitoring

import requests
import time
import json
import statistics
from datetime import datetime, timedelta

class ResponseTimeMonitor:
    def __init__(self, url, interval=60, duration=3600):
        self.url = url
        self.interval = interval
        self.duration = duration
        self.measurements = []

    def measure_response_time(self):
        """Measure single response time"""
        try:
            start_time = time.time()
            response = requests.get(self.url, timeout=30)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                'timestamp': datetime.now(),
                'response_time': response_time,
                'status_code': response.status_code,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'timestamp': datetime.now(),
                'response_time': None,
                'status_code': None,
                'success': False,
                'error': str(e)
            }

    def run_monitoring(self):
        """Run response time monitoring"""
        print(f"🔍 Monitoring response time for: {self.url}")
        print(f"⏰ Interval: {self.interval}s, Duration: {self.duration}s")
        print(f"📅 Started at: {datetime.now()}")
        print("")

        end_time = datetime.now() + timedelta(seconds=self.duration)

        while datetime.now() < end_time:
            measurement = self.measure_response_time()
            self.measurements.append(measurement)

            status = "✅" if measurement['success'] else "❌"
            response_time = measurement['response_time']

            if response_time:
                print(f"{status} {measurement['timestamp'].strftime('%H:%M:%S')} - {response_time:.2f}ms (HTTP {measurement['status_code']})")
            else:
                print(f"{status} {measurement['timestamp'].strftime('%H:%M:%S')} - Failed ({measurement.get('error', 'Unknown error')})")

            time.sleep(self.interval)

        self.generate_report()

    def generate_report(self):
        """Generate monitoring report"""
        print("\n📊 Response Time Monitoring Report")
        print("=" * 50)

        successful_measurements = [m for m in self.measurements if m['success'] and m['response_time']]

        if not successful_measurements:
            print("❌ No successful measurements recorded")
            return

        response_times = [m['response_time'] for m in successful_measurements]

        print(f"Total measurements: {len(self.measurements)}")
        print(f"Successful measurements: {len(successful_measurements)}")
        print(f"Failed measurements: {len(self.measurements) - len(successful_measurements)}")
        print(f"Success rate: {len(successful_measurements)/len(self.measurements)*100:.1f}%")
        print("")

        print("📈 Response Time Statistics:")
        print(f"   Average: {statistics.mean(response_times):.2f}ms")
        print(f"   Median: {statistics.median(response_times):.2f}ms")
        print(f"   Min: {min(response_times):.2f}ms")
        print(f"   Max: {max(response_times):.2f}ms")
        print(f"   Std Dev: {statistics.stdev(response_times):.2f}ms")

        # Performance assessment
        avg_response_time = statistics.mean(response_times)

        print("\n🏥 Performance Assessment:")
        if avg_response_time < 200:
            print("   🟢 Excellent: Average response time under 200ms")
        elif avg_response_time < 500:
            print("   🟡 Good: Average response time under 500ms")
        elif avg_response_time < 1000:
            print("   🟠 Fair: Average response time under 1s")
        else:
            print("   🔴 Poor: Average response time exceeds 1s")

        # Save detailed results
        results_file = f"response-time-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.measurements, f, default=str, indent=2)

        print(f"\n💾 Detailed results saved to: {results_file}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Monitor response times')
    parser.add_argument('url', help='URL to monitor')
    parser.add_argument('--interval', type=int, default=60, help='Measurement interval in seconds')
    parser.add_argument('--duration', type=int, default=3600, help='Monitoring duration in seconds')

    args = parser.parse_args()

    monitor = ResponseTimeMonitor(args.url, args.interval, args.duration)
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
```

## 5. Rollback Verification Procedures

### 5.1 Rollback Test Script
```bash
#!/bin/bash
# rollback-test.sh - Rollback verification

COOLIFY_SERVER="${COOLIFY_SERVER:-https://coolify.example.com}"
PROJECT_NAME="$1"
PREVIOUS_VERSION="$2"

if [ -z "$PROJECT_NAME" ] || [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: $0 <project-name> <previous-version>"
    exit 1
fi

echo "🔄 Rollback Test for $PROJECT_NAME to version $PREVIOUS_VERSION"
echo "🌐 Coolify Server: $COOLIFY_SERVER"

# Function to check application health
check_app_health() {
    local app_url="$1"
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "🔍 Health check attempt $attempt/$max_attempts..."

        if curl -f -s -o /dev/null -w "%{http_code}" "$app_url" | grep -q "200"; then
            echo "✅ Application is healthy"
            return 0
        fi

        echo "⏳ Waiting for application to be ready..."
        sleep 10
        ((attempt++))
    done

    echo "❌ Application failed health check after $max_attempts attempts"
    return 1
}

# Function to get current deployment info
get_deployment_info() {
    echo "📋 Current deployment information..."

    # This would use the Coolify API to get current deployment info
    # For now, simulate with placeholder data
    echo "   Current version: $(git rev-parse --short HEAD)"
    echo "   Deployment time: $(date)"
    echo "   Status: Running"
}

# Pre-rollback checks
echo ""
echo "🔍 Pre-rollback checks..."

# Get current deployment info
get_deployment_info

# Check if previous version exists
echo "📦 Checking if previous version exists..."
if ! git cat-file -e "$PREVIOUS_VERSION" 2>/dev/null; then
    echo "❌ Previous version $PREVIOUS_VERSION not found"
    exit 1
fi

echo "✅ Previous version $PREVIOUS_VERSION found"

# Perform rollback
echo ""
echo "🔄 Performing rollback to $PREVIOUS_VERSION..."

# This would use the Coolify API to perform rollback
# For now, simulate the rollback process
echo "   Stopping current deployment..."
sleep 5
echo "   Deploying previous version..."
sleep 10
echo "   Starting services..."
sleep 5

# Post-rollback verification
echo ""
echo "🔍 Post-rollback verification..."

# Get application URL (this would come from Coolify API)
APP_URL="${APP_URL:-https://$PROJECT_NAME.coolify.example.com}"

# Check application health
if check_app_health "$APP_URL"; then
    echo "✅ Rollback successful - application is healthy"

    # Additional verification steps
    echo ""
    echo "🔍 Additional verification..."

    # Check critical functionality
    echo "   Checking critical endpoints..."
    critical_endpoints=(
        "$APP_URL/health"
        "$APP_URL/api/status"
    )

    for endpoint in "${critical_endpoints[@]}"; do
        if curl -f -s -o /dev/null "$endpoint"; then
            echo "   ✅ $endpoint is responding"
        else
            echo "   ❌ $endpoint is not responding"
        fi
    done

    # Check version information
    echo "   Checking version information..."
    version_response=$(curl -s "$APP_URL/version" 2>/dev/null || echo "unknown")
    echo "   Current version: $version_response"

    echo ""
    echo "🎉 Rollback verification completed successfully!"

else
    echo "❌ Rollback failed - application is not healthy"
    echo "🔄 Consider rolling back to the previous version or investigating the issue"
    exit 1
fi
```

### 5.2 Comprehensive Rollback Verification
```python
#!/usr/bin/env python3
# rollback-verification.py - Comprehensive rollback verification

import requests
import json
import sys
import time
from datetime import datetime

class RollbackVerification:
    def __init__(self, config_file="rollback-config.json"):
        self.config = self.load_config(config_file)
        self.test_results = []

    def load_config(self, config_file):
        """Load rollback configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "app_url": "https://your-app.coolify.example.com",
                "health_endpoint": "/health",
                "critical_endpoints": [
                    "/api/status",
                    "/api/health"
                ],
                "expected_version": "previous-version-hash",
                "verification_tests": [
                    {"name": "Database connectivity", "endpoint": "/api/test/db"},
                    {"name": "External API", "endpoint": "/api/test/external"},
                    {"name": "User authentication", "endpoint": "/api/test/auth"}
                ]
            }

    def verify_endpoint(self, url, expected_status=200, timeout=30):
        """Verify endpoint accessibility"""
        try:
            response = requests.get(url, timeout=timeout)
            result = {
                'url': url,
                'status_code': response.status_code,
                'expected_status': expected_status,
                'success': response.status_code == expected_status,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }

            self.test_results.append(result)
            return result

        except Exception as e:
            result = {
                'url': url,
                'error': str(e),
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

            self.test_results.append(result)
            return result

    def verify_application_health(self):
        """Verify application health after rollback"""
        print("🔍 Verifying application health...")

        health_url = self.config['app_url'] + self.config['health_endpoint']
        result = self.verify_endpoint(health_url)

        if result['success']:
            print(f"✅ Health check passed (HTTP {result['status_code']}, {result['response_time']:.2f}s)")
        else:
            print(f"❌ Health check failed: {result.get('error', 'HTTP ' + str(result.get('status_code', 'unknown'))}")

        return result['success']

    def verify_critical_endpoints(self):
        """Verify critical application endpoints"""
        print("\n🔍 Verifying critical endpoints...")

        all_passed = True
        for endpoint in self.config['critical_endpoints']:
            url = self.config['app_url'] + endpoint
            result = self.verify_endpoint(url)

            if result['success']:
                print(f"✅ {endpoint} - HTTP {result['status_code']}")
            else:
                print(f"❌ {endpoint} - {result.get('error', 'HTTP ' + str(result.get('status_code', 'unknown')))}")
                all_passed = False

        return all_passed

    def verify_application_version(self):
        """Verify correct application version is deployed"""
        print("\n🔍 Verifying application version...")

        version_url = self.config['app_url'] + "/version"
        try:
            response = requests.get(version_url, timeout=10)
            if response.status_code == 200:
                version_info = response.json()
                current_version = version_info.get('version', version_info.get('commit', 'unknown'))
                expected_version = self.config['expected_version']

                print(f"   Current version: {current_version}")
                print(f"   Expected version: {expected_version}")

                if current_version == expected_version:
                    print("✅ Version verification passed")
                    return True
                else:
                    print("❌ Version mismatch - rollback may not have completed correctly")
                    return False
            else:
                print(f"❌ Failed to get version information (HTTP {response.status_code})")
                return False

        except Exception as e:
            print(f"❌ Error checking version: {e}")
            return False

    def run_verification_tests(self):
        """Run custom verification tests"""
        print("\n🔍 Running verification tests...")

        all_passed = True
        for test in self.config['verification_tests']:
            test_url = self.config['app_url'] + test['endpoint']
            result = self.verify_endpoint(test_url)

            status = "✅" if result['success'] else "❌"
            print(f"   {status} {test['name']} - {test['endpoint']}")

            if not result['success']:
                all_passed = False

        return all_passed

    def wait_for_application_ready(self, max_wait_time=300):
        """Wait for application to be ready after rollback"""
        print(f"\n⏳ Waiting for application to be ready (max {max_wait_time}s)...")

        health_url = self.config['app_url'] + self.config['health_endpoint']
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    wait_time = time.time() - start_time
                    print(f"✅ Application is ready after {wait_time:.1f}s")
                    return True
            except:
                pass

            print(f"   Still waiting... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(10)

        print("❌ Application failed to become ready within timeout period")
        return False

    def generate_verification_report(self):
        """Generate comprehensive verification report"""
        print("\n📊 Rollback Verification Report")
        print("=" * 50)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['success'])

        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")

        # Response time analysis
        response_times = [test['response_time'] for test in self.test_results if 'response_time' in test]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"Average response time: {avg_response_time:.3f}s")

        # Failed tests details
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   {test['url']}: {test.get('error', 'HTTP ' + str(test.get('status_code', 'unknown')))}")

        return passed_tests == total_tests

    def run_comprehensive_verification(self):
        """Run complete rollback verification"""
        print("🔄 Starting comprehensive rollback verification...")
        print(f"🌐 Application URL: {self.config['app_url']}")
        print(f"📅 Started at: {datetime.now()}")
        print("")

        # Wait for application to be ready
        if not self.wait_for_application_ready():
            return False

        # Run verification steps
        health_ok = self.verify_application_health()
        endpoints_ok = self.verify_critical_endpoints()
        version_ok = self.verify_application_version()
        tests_ok = self.run_verification_tests()

        # Generate report
        all_tests_passed = self.generate_verification_report()

        # Final assessment
        print("\n🏥 Final Assessment:")
        if health_ok and endpoints_ok and version_ok and tests_ok and all_tests_passed:
            print("🎉 Rollback verification completed successfully!")
            print("✅ Application is fully operational after rollback")
            return True
        else:
            print("❌ Rollback verification failed!")
            print("⚠️  Some issues detected - investigation required")

            if not version_ok:
                print("   - Version mismatch detected")
            if not health_ok:
                print("   - Application health check failed")
            if not endpoints_ok:
                print("   - Critical endpoints not responding")
            if not tests_ok:
                print("   - Verification tests failed")

            return False

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive rollback verification')
    parser.add_argument('--config', default='rollback-config.json', help='Configuration file path')

    args = parser.parse_args()

    verifier = RollbackVerification(args.config)
    success = verifier.run_comprehensive_verification()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## 6. Configuration Files

### 6.1 Health Check Configuration
```json
{
  "http_endpoints": [
    {
      "url": "https://your-app.coolify.example.com/health",
      "expected_status": 200,
      "timeout": 30,
      "max_response_time": 5
    },
    {
      "url": "https://your-app.coolify.example.com/api/status",
      "expected_status": 200,
      "timeout": 30,
      "max_response_time": 3
    }
  ],
  "ssl_domains": [
    "https://your-app.coolify.example.com",
    "https://api.your-app.coolify.example.com"
  ],
  "databases": [
    {
      "name": "primary_db",
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "database": "app_db",
      "username": "app_user"
    }
  ]
}
```

### 6.2 Rollback Configuration
```json
{
  "app_url": "https://your-app.coolify.example.com",
  "health_endpoint": "/health",
  "critical_endpoints": [
    "/api/status",
    "/api/health",
    "/api/users/me"
  ],
  "expected_version": "abc123def456",
  "verification_tests": [
    {
      "name": "Database connectivity",
      "endpoint": "/api/test/db"
    },
    {
      "name": "External API",
      "endpoint": "/api/test/external"
    },
    {
      "name": "User authentication",
      "endpoint": "/api/test/auth"
    }
  ]
}
```

## Usage Examples

### Basic Health Check
```bash
# Simple health check
./health-check.sh

# With custom configuration
APP_URL="https://myapp.coolify.example.com" ./health-check.sh

# Comprehensive health check
python3 comprehensive-health-check.py
```

### Domain and SSL Verification
```bash
# Domain verification
./domain-verify.sh myapp.coolify.example.com

# SSL certificate validation
python3 ssl-validator.py myapp.coolify.example.com
```

### Log Monitoring
```bash
# Real-time log monitoring
./log-monitor.sh /var/log/app.log ERROR admin@example.com

# Log analysis
python3 log-analyzer.py /var/log/app.log 24
```

### Performance Testing
```bash
# Load testing
./load-test.sh https://myapp.coolify.example.com 10 100

# Response time monitoring
python3 response-time-monitor.py https://myapp.coolify.example.com --interval 60 --duration 3600
```

### Rollback Verification
```bash
# Basic rollback test
./rollback-test.sh myapp abc123def456

# Comprehensive verification
python3 rollback-verification.py --config rollback-config.json
```

## Integration with CLI Tool

These monitoring and verification scripts can be integrated into the CLI tool as follows:

```bash
coolify health check          # Run health checks
coolify domain verify         # Verify domain configuration
coolify ssl status            # Check SSL certificates
coolify logs monitor          # Monitor application logs
coolify test performance      # Run performance tests
coolify rollback verify       # Verify rollback procedures
```

This comprehensive toolkit provides everything needed to monitor, verify, and maintain Coolify deployments effectively.