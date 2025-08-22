from league_pipeline.pipeline.orchestrator_pipeline import PipelineOrchestrator

def main():
    """
    Main entry point for pipeline execution.
    
    Creates and runs the pipeline orchestrator, handling any top-level exceptions
    and providing appropriate logging.
    """
    try:
        orchestrator = PipelineOrchestrator()
        orchestrator.run_full_pipeline()
    except Exception as e:
        print(f"Pipeline execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()