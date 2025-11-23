"""
Pipeline Examples for AgentSwarm Tools Framework.

Demonstrates fluent pipeline API with real-world use cases.
"""

import os
from pathlib import Path
from shared.pipeline import Pipeline, ParallelPipeline, pipeline_builder


# Enable mock mode for examples
os.environ["USE_MOCK_APIS"] = "true"


def example_1_research_pipeline():
    """
    Example 1: Research Pipeline
    Search -> Extract URLs -> Crawl -> Summarize -> Document
    """
    print("=" * 60)
    print("Example 1: Research Pipeline")
    print("=" * 60)

    # Mock functions for example
    def mock_search(query, max_results=10):
        return {
            "success": True,
            "results": [
                {"url": f"https://example.com/{i}", "title": f"Result {i}", "score": 0.9 - i * 0.1}
                for i in range(max_results)
            ]
        }

    def extract_urls(data):
        return [item['url'] for item in data.get('results', [])]

    def mock_crawl(data):
        # Data parameter receives previous result
        urls = data if isinstance(data, list) else []
        return "\n".join([f"Content from {url}" for url in urls])

    # Build pipeline
    pipeline = (
        Pipeline("research-pipeline")
        .add_step("search", mock_search, query="AI trends 2024", max_results=5)
        .add_function("extract", extract_urls)
        .add_step("crawl", mock_crawl)
        .on_error(lambda e: print(f"Error: {e}"))
    )

    # Execute
    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Steps: {result['total_steps']}")
    print(f"Duration: {result['duration_ms']:.2f}ms")
    if result.get('result'):
        print(f"Result: {str(result['result'])[:100]}...")
    else:
        print(f"Error: {result.get('error', 'Unknown')}")
    print()


def example_2_data_processing():
    """
    Example 2: Data Processing Pipeline
    Load -> Clean -> Transform -> Aggregate -> Visualize
    """
    print("=" * 60)
    print("Example 2: Data Processing Pipeline")
    print("=" * 60)

    # Mock data
    sales_data = [
        {"month": "Jan", "sales": 1000, "region": "North"},
        {"month": "Jan", "sales": 1500, "region": "South"},
        {"month": "Feb", "sales": 1200, "region": "North"},
        {"month": "Feb", "sales": 1800, "region": "South"},
        {"month": "Mar", "sales": 1400, "region": "North"},
        {"month": "Mar", "sales": 2000, "region": "South"},
    ]

    def load_data():
        return sales_data

    def clean_data(data):
        # Remove invalid entries
        return [row for row in data if row.get('sales', 0) > 0]

    def aggregate_by_month(data):
        result = {}
        for row in data:
            month = row['month']
            result[month] = result.get(month, 0) + row['sales']
        return [{"month": k, "total": v} for k, v in sorted(result.items())]

    # Build pipeline with transformations
    pipeline = (
        Pipeline("data-processing")
        .add_function("load", load_data)
        .add_function("clean", clean_data)
        .filter("valid", lambda row: row.get('sales', 0) > 1100)
        .add_function("aggregate", aggregate_by_month)
    )

    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")
    print()


def example_3_map_filter_reduce():
    """
    Example 3: Map/Filter/Reduce Pattern
    Demonstrates functional programming style transformations.
    """
    print("=" * 60)
    print("Example 3: Map/Filter/Reduce Pattern")
    print("=" * 60)

    def mock_search(query):
        return {
            "results": [
                {"url": f"url{i}", "score": 0.9 - i * 0.1, "title": f"Result {i}"}
                for i in range(10)
            ]
        }

    pipeline = (
        Pipeline("transform")
        .add_step("search", mock_search, query="AI")
        .add_function("extract", lambda data: data['results'])
        .filter("high_score", lambda item: item['score'] > 0.6)
        .map("titles", lambda item: item['title'])
        .reduce("join", lambda acc, title: f"{acc}, {title}" if acc else title, initial="")
    )

    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")
    print()


def example_4_conditional_pipeline():
    """
    Example 4: Conditional Execution
    Different processing based on data characteristics.
    """
    print("=" * 60)
    print("Example 4: Conditional Execution")
    print("=" * 60)

    def check_data(data):
        return {
            "has_data": True,
            "count": 5,
            "data": ["item1", "item2", "item3", "item4", "item5"]
        }

    def process_large(data):
        return f"Processed {data['count']} items (large batch)"

    def process_small(data):
        return f"Processed {data['count']} items (small batch)"

    pipeline = (
        Pipeline("conditional")
        .add_step("check", check_data)
        .conditional(
            "decide",
            condition=lambda data: data.get('count', 0) > 3,
            then_step=process_large,
            else_step=process_small
        )
    )

    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")
    print()


def example_5_error_handling():
    """
    Example 5: Error Handling
    Demonstrates error recovery and continue-on-error.
    """
    print("=" * 60)
    print("Example 5: Error Handling")
    print("=" * 60)

    errors_caught = []

    def failing_step(data):
        raise ValueError("Intentional error for demo")

    def recovery_step(data):
        return "Recovered successfully"

    pipeline = (
        Pipeline("error-demo")
        .add_function("start", lambda: {"status": "started"})
        .add_step("fail", failing_step)
        .add_step("recover", recovery_step)
        .on_error(lambda e: errors_caught.append(str(e)))
        .continue_on_error_mode(True)
    )

    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Errors caught: {len(errors_caught)}")
    print(f"Steps executed: {result['steps_completed']}/{result['total_steps']}")
    print()


def example_6_decorator_pattern():
    """
    Example 6: Pipeline Decorator
    Clean, readable pipeline definition using decorator.
    """
    print("=" * 60)
    print("Example 6: Pipeline Decorator")
    print("=" * 60)

    @pipeline_builder
    def research_workflow(topic: str):
        # Step 1: Search
        search_results = {
            "results": [
                {"url": f"url{i}", "title": f"{topic} result {i}"}
                for i in range(5)
            ]
        }

        # Step 2: Extract
        urls = [item['url'] for item in search_results['results']]

        # Step 3: Process
        content = f"Processed {len(urls)} URLs for {topic}"

        return content

    result = research_workflow("Machine Learning")

    print(f"Success: {result['success']}")
    print(f"Pipeline: {result['pipeline_name']}")
    print(f"Result: {result['result']}")
    print()


def example_7_parallel_pipelines():
    """
    Example 7: Parallel Pipeline Execution
    Run multiple pipelines simultaneously.
    """
    print("=" * 60)
    print("Example 7: Parallel Pipelines")
    print("=" * 60)

    def search_web(query):
        return {"source": "web", "results": [f"web_{i}" for i in range(3)]}

    def search_scholar(query):
        return {"source": "scholar", "results": [f"scholar_{i}" for i in range(2)]}

    def search_images(query):
        return {"source": "images", "results": [f"image_{i}" for i in range(4)]}

    # Create individual pipelines
    web_pipeline = Pipeline("web").add_step("search", search_web, query="AI")
    scholar_pipeline = Pipeline("scholar").add_step("search", search_scholar, query="AI")
    image_pipeline = Pipeline("images").add_step("search", search_images, query="AI")

    # Execute in parallel
    parallel = (
        ParallelPipeline("multi-source")
        .add_pipeline(web_pipeline)
        .add_pipeline(scholar_pipeline)
        .add_pipeline(image_pipeline)
    )

    result = parallel.execute()

    print(f"Success: {result['success']}")
    print(f"Pipelines: {result['total_pipelines']}")
    print(f"Successful: {result['successful_pipelines']}")
    print(f"Duration: {result['duration_ms']:.2f}ms")
    for pipeline_result in result['results']:
        print(f"  - {pipeline_result['pipeline_name']}: {pipeline_result['success']}")
    print()


def example_8_complex_workflow():
    """
    Example 8: Complex Multi-Stage Workflow
    Combines multiple patterns.
    """
    print("=" * 60)
    print("Example 8: Complex Multi-Stage Workflow")
    print("=" * 60)

    topics = ["AI", "ML", "DL"]

    def search_topic(topic):
        return {
            "topic": topic,
            "results": [{"url": f"{topic}_url{i}", "score": 0.9 - i * 0.1} for i in range(3)]
        }

    def aggregate_results(search_results):
        total = sum(len(sr['results']) for sr in search_results)
        return {
            "total_results": total,
            "topics": [sr['topic'] for sr in search_results],
            "all_results": [item for sr in search_results for item in sr['results']]
        }

    pipeline = (
        Pipeline("complex-workflow")
        .add_function("set_topics", lambda: topics)
        .map("search_each", search_topic)
        .add_function("aggregate", aggregate_results)
        .filter("high_quality", lambda: True)  # Would filter in real impl
        .add_function("format", lambda data: f"Found {data['total_results']} results across {len(data['topics'])} topics")
    )

    result = pipeline.execute()

    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")
    print(f"Steps: {len(result['steps'])}")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("AgentSwarm Pipeline Examples")
    print("=" * 60)
    print("\n")

    example_1_research_pipeline()
    example_2_data_processing()
    example_3_map_filter_reduce()
    example_4_conditional_pipeline()
    example_5_error_handling()
    example_6_decorator_pattern()
    example_7_parallel_pipelines()
    example_8_complex_workflow()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
