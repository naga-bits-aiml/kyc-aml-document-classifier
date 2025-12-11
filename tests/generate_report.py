#!/usr/bin/env python
"""
Generate custom test report with visualizations
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import xml.etree.ElementTree as ET

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def parse_junit_xml(xml_file: Path):
    """Parse JUnit XML test results"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    results = {
        "total": int(root.attrib.get("tests", 0)),
        "passed": 0,
        "failed": int(root.attrib.get("failures", 0)),
        "errors": int(root.attrib.get("errors", 0)),
        "skipped": int(root.attrib.get("skipped", 0)),
        "duration": float(root.attrib.get("time", 0)),
        "test_cases": []
    }
    
    for testcase in root.iter("testcase"):
        case = {
            "name": testcase.attrib.get("name"),
            "classname": testcase.attrib.get("classname"),
            "time": float(testcase.attrib.get("time", 0)),
            "status": "passed"
        }
        
        # Check for failures or errors
        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")
        
        if failure is not None:
            case["status"] = "failed"
            case["message"] = failure.attrib.get("message", "")
        elif error is not None:
            case["status"] = "error"
            case["message"] = error.attrib.get("message", "")
        elif skipped is not None:
            case["status"] = "skipped"
            case["message"] = skipped.attrib.get("message", "")
        else:
            results["passed"] += 1
        
        results["test_cases"].append(case)
    
    return results


def generate_html_report(results: dict, output_file: Path):
    """Generate HTML report with visualizations"""
    
    # Calculate statistics
    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    errors = results["errors"]
    skipped = results["skipped"]
    duration = results["duration"]
    
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Group tests by class
    tests_by_class = defaultdict(list)
    for test in results["test_cases"]:
        class_name = test["classname"].split(".")[-1]
        tests_by_class[class_name].append(test)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KYC/AML Classifier - Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        }}
        
        .stat-card .number {{
            font-size: 3em;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.passed .number {{ color: #28a745; }}
        .stat-card.failed .number {{ color: #dc3545; }}
        .stat-card.skipped .number {{ color: #ffc107; }}
        .stat-card.duration .number {{ color: #17a2b8; }}
        
        .progress-bar {{
            margin: 30px 40px;
            background: #e9ecef;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            position: relative;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 1.1em;
            transition: width 1s ease-in-out;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .test-class {{
            margin-bottom: 30px;
            border: 1px solid #dee2e6;
            border-radius: 12px;
            overflow: hidden;
        }}
        
        .test-class-header {{
            background: #f8f9fa;
            padding: 20px;
            font-weight: 700;
            font-size: 1.2em;
            color: #495057;
            border-bottom: 2px solid #dee2e6;
        }}
        
        .test-case {{
            padding: 15px 20px;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
            transition: background-color 0.2s;
        }}
        
        .test-case:hover {{
            background-color: #f8f9fa;
        }}
        
        .test-case:last-child {{
            border-bottom: none;
        }}
        
        .test-status {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        
        .test-status.passed {{
            background: #28a745;
        }}
        
        .test-status.failed {{
            background: #dc3545;
        }}
        
        .test-status.skipped {{
            background: #ffc107;
        }}
        
        .test-status.error {{
            background: #dc3545;
        }}
        
        .test-name {{
            flex: 1;
            font-size: 0.95em;
        }}
        
        .test-time {{
            color: #6c757d;
            font-size: 0.9em;
            margin-left: 15px;
        }}
        
        .error-message {{
            margin-top: 10px;
            padding: 10px;
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
            font-size: 0.9em;
            border-radius: 4px;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        
        .chart-container {{
            padding: 40px;
            text-align: center;
        }}
        
        .chart {{
            max-width: 600px;
            margin: 0 auto;
        }}
        
        @media (max-width: 768px) {{
            .summary {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .container {{
                margin: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 KYC/AML Document Classifier</h1>
            <p class="subtitle">API Test Suite Report</p>
            <p style="margin-top: 15px; opacity: 0.8;">Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="number">{total}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="stat-card passed">
                <div class="number">{passed}</div>
                <div class="label">Passed</div>
            </div>
            <div class="stat-card failed">
                <div class="number">{failed + errors}</div>
                <div class="label">Failed</div>
            </div>
            <div class="stat-card skipped">
                <div class="number">{skipped}</div>
                <div class="label">Skipped</div>
            </div>
            <div class="stat-card duration">
                <div class="number">{duration:.2f}s</div>
                <div class="label">Duration</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {pass_rate}%">
                {pass_rate:.1f}% Pass Rate
            </div>
        </div>
        
        <div class="content">
            <h2 style="margin-bottom: 25px; color: #495057;">Test Results by Class</h2>
"""
    
    # Add test cases grouped by class
    for class_name, tests in sorted(tests_by_class.items()):
        class_passed = sum(1 for t in tests if t["status"] == "passed")
        class_total = len(tests)
        
        html_content += f"""
            <div class="test-class">
                <div class="test-class-header">
                    {class_name} ({class_passed}/{class_total} passed)
                </div>
"""
        
        for test in tests:
            status_icon = "✓" if test["status"] == "passed" else "✗" if test["status"] in ["failed", "error"] else "⊘"
            
            html_content += f"""
                <div class="test-case">
                    <div class="test-status {test['status']}"></div>
                    <div class="test-name">{test['name']}</div>
                    <div class="test-time">{test['time']:.3f}s</div>
                </div>
"""
            
            if test["status"] in ["failed", "error"] and "message" in test:
                html_content += f"""
                <div style="padding: 0 20px 15px 59px;">
                    <div class="error-message">{test['message']}</div>
                </div>
"""
        
        html_content += """
            </div>
"""
    
    html_content += f"""
        </div>
        
        <div class="footer">
            <p><strong>KYC/AML Document Classifier API</strong></p>
            <p>Automated Testing Suite • FastAPI • PyTorch • EfficientNet</p>
        </div>
    </div>
</body>
</html>
"""
    
    output_file.write_text(html_content, encoding="utf-8")
    return output_file


def main():
    """Main function to generate report"""
    reports_dir = PROJECT_ROOT / "test_reports"
    junit_file = reports_dir / "junit.xml"
    
    if not junit_file.exists():
        print("❌ Error: junit.xml not found. Please run tests first:")
        print("   python tests/run_tests.py")
        return 1
    
    print("📊 Generating custom test report...")
    
    # Parse test results
    results = parse_junit_xml(junit_file)
    
    # Generate HTML report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = reports_dir / f"custom_report_{timestamp}.html"
    report_path = generate_html_report(results, output_file)
    
    print(f"✅ Report generated: {report_path}")
    print(f"\n📈 Summary:")
    print(f"   Total: {results['total']}")
    print(f"   Passed: {results['passed']}")
    print(f"   Failed: {results['failed']}")
    print(f"   Errors: {results['errors']}")
    print(f"   Skipped: {results['skipped']}")
    print(f"   Duration: {results['duration']:.2f}s")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
