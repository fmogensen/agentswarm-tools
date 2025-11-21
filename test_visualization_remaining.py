#!/usr/bin/env python3
"""Test remaining 7 visualization tools"""

import os
import sys
sys.path.insert(0, '/app')

# Bypass rate limiting
from shared import security
security.RateLimiter.check_rate_limit = lambda *args, **kwargs: None

results = {"passed": [], "failed": []}

def test(name, func):
    try:
        print(f"\n{'='*60}\n{name}\n{'='*60}")
        func()
        results["passed"].append(name)
        print(f"✅ {name} PASSED")
        return True
    except Exception as e:
        results["failed"].append(f"{name}: {str(e)[:100]}")
        print(f"❌ {name} FAILED: {e}")
        return False

# Test 1: Dual Axes Chart
def test_dual_axes():
    from tools.visualization.generate_dual_axes_chart.generate_dual_axes_chart import GenerateDualAxesChart
    tool = GenerateDualAxesChart(
        prompt="Generate dual axes chart",
        params={
            "data": {
                "x": [1, 2, 3, 4],
                "column_values": [10, 20, 15, 25],
                "line_values": [100, 150, 120, 180]
            },
            "title": "Test Dual Axes"
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated dual axes chart")

# Test 2: Fishbone Diagram - only accepts format and max_branches params
def test_fishbone():
    from tools.visualization.generate_fishbone_diagram.generate_fishbone_diagram import GenerateFishboneDiagram
    tool = GenerateFishboneDiagram(
        prompt="Analyze causes of low sales",
        params={"format": "json", "max_branches": 4}
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated fishbone diagram")

# Test 3: Flow Diagram
def test_flow_diagram():
    from tools.visualization.generate_flow_diagram.generate_flow_diagram import GenerateFlowDiagram
    tool = GenerateFlowDiagram(
        prompt="Generate flow diagram",
        params={
            "nodes": [
                {"id": "1", "label": "Start"},
                {"id": "2", "label": "Process"},
                {"id": "3", "label": "End"}
            ],
            "edges": [
                {"from": "1", "to": "2"},
                {"from": "2", "to": "3"}
            ]
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated flow diagram")

# Test 4: Mind Map
def test_mind_map():
    from tools.visualization.generate_mind_map.generate_mind_map import GenerateMindMap
    tool = GenerateMindMap(
        prompt="Generate mind map",
        params={
            "central_idea": "Project Planning",
            "branches": {
                "Timeline": ["Q1", "Q2", "Q3"],
                "Resources": ["Team", "Budget"],
                "Goals": ["Launch", "Growth"]
            }
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated mind map")

# Test 5: Network Graph
def test_network_graph():
    from tools.visualization.generate_network_graph.generate_network_graph import GenerateNetworkGraph
    tool = GenerateNetworkGraph(
        prompt="Generate network graph",
        params={
            "nodes": [
                {"id": "A", "label": "Node A"},
                {"id": "B", "label": "Node B"},
                {"id": "C", "label": "Node C"}
            ],
            "edges": [
                {"source": "A", "target": "B"},
                {"source": "B", "target": "C"}
            ]
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated network graph")

# Test 6: Radar Chart - expects data as dict with at least 4 dimensions
def test_radar():
    from tools.visualization.generate_radar_chart.generate_radar_chart import GenerateRadarChart
    tool = GenerateRadarChart(
        prompt="Generate radar chart",
        params={
            "data": {
                "Speed": 80,
                "Power": 90,
                "Range": 70,
                "Accuracy": 85
            }
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated radar chart")

# Test 7: Treemap Chart
def test_treemap():
    from tools.visualization.generate_treemap_chart.generate_treemap_chart import GenerateTreemapChart
    tool = GenerateTreemapChart(
        prompt="Generate treemap",
        params={
            "data": [
                {"name": "Category A", "value": 100},
                {"name": "Category B", "value": 150},
                {"name": "Category C", "value": 75}
            ]
        }
    )
    result = tool.run()
    assert result["success"], f"Failed: {result}"
    print(f"✓ Generated treemap")

if __name__ == "__main__":
    print("\n🧪 TESTING 7 REMAINING VISUALIZATION TOOLS\n")

    test("1. Dual Axes Chart", test_dual_axes)
    test("2. Fishbone Diagram", test_fishbone)
    test("3. Flow Diagram", test_flow_diagram)
    test("4. Mind Map", test_mind_map)
    test("5. Network Graph", test_network_graph)
    test("6. Radar Chart", test_radar)
    test("7. Treemap Chart", test_treemap)

    print(f"\n\n{'='*60}")
    print(f"RESULTS: {len(results['passed'])}/7 passed")
    print(f"{'='*60}")
    for p in results["passed"]:
        print(f"✅ {p}")
    for f in results["failed"]:
        print(f"❌ {f}")
