"""
Pipeline Orchestrator Module.

This module provides the main orchestration class for the League of Legends data pipeline,
coordinating all data collection stages and services in the proper sequence.

Classes:
    PipelineOrchestrator: Main orchestrator for coordinating all pipeline stages.

Example:
    >>> from pipeline_orchestrator import PipelineOrchestrator
    >>> orchestrator = PipelineOrchestrator()
    >>> orchestrator.activate_data_collection_services()
    >>> orchestrator.start_pipeline()
"""

import asyncio
from league_pipeline.constants.pipeline_constants import Stages
from league_pipeline.config.logger_config_setup import logging_setup
from league_pipeline.rate_limiting.rate_manager import TokenBucket
from league_pipeline.constants.regions import Region, ContinentalRegion
from league_pipeline.services.summoner_service import SummonerCollectionService
from league_pipeline.services.match_id_service import MatchIDCollectionService
from league_pipeline.services.match_data_service import MatchDataService
from league_pipeline.services.match_timeline_service import MatchTimelineService
from league_pipeline.constants.file_folder_paths import Paths
from league_pipeline.constants.database_constants import DatabaseName
from league_pipeline.constants.regions import Region, ContinentalRegion
from league_pipeline.constants.league_ranks import RankedQueue, QueueMatchV5, RankedTier, RankedDivision
from league_pipeline.constants.pipeline_constants import DataProcessingConfig
from league_pipeline.key.key_handler import load_api_key


class PipelineOrchestrator:
    """
    Main orchestrator class for the League of Legends data pipeline.
    
    This class coordinates all data collection stages, manages service initialization,
    and ensures proper execution order of the pipeline components.
    
    Attributes:
        logger: Configured logger instance for pipeline operations.
        TokenBucketLocal: Rate limiter for local/regional API endpoints.
        TokenBucketContinent: Rate limiter for continental API endpoints.
        api_key: Riot Games API key loaded from environment.
        SummonerCollectionService: Service for collecting summoner data.
        MatchIDCollectionService: Service for collecting match IDs.
        MatchDataService: Service for collecting match data.
        MatchTimelineService: Service for collecting match timeline data.
    """
    
    def __init__(self):
        """
        Initialize the pipeline orchestrator with logging, rate limiting, and API credentials.
        
        Sets up all necessary components for pipeline execution including loggers,
        token buckets for rate limiting, and API authentication.
        """
        self.logger = logging_setup("log_config.json", "pipeline_logger")
        self.TokenBucketLocal = TokenBucket(Region, self.logger)
        self.TokenBucketContinent = TokenBucket(ContinentalRegion, self.logger)
        self.api_key = load_api_key()
        
        # Initialize service attributes
        self.SummonerCollectionService = None
        self.MatchIDCollectionService = None
        self.MatchDataService = None
        self.MatchTimelineService = None

    def activate_data_collection_services(self):
        """
        Initialize and activate data collection services based on pipeline stage configuration.
        
        This method creates service instances for each active stage defined in Stages.TO_PROCESS:
        - Stage 1: Summoner data collection from ranked ladders
        - Stage 2: Match ID collection from summoner match history
        - Stage 3: Detailed match data collection
        - Stage 4: Match timeline data collection
        
        Only services for active stages (marked as 1 in TO_PROCESS) are initialized.
        """
        stage_1 = Stages.TO_PROCESS[0]
        stage_2 = Stages.TO_PROCESS[1]
        stage_3 = Stages.TO_PROCESS[2]
        stage_4 = Stages.TO_PROCESS[3]

        if stage_1:
            self.logger.info("Activating Stage 1: Summoner Collection Service")
            self.SummonerCollectionService = \
                SummonerCollectionService(
                    db_location=Paths.DATA,
                    database_name=DatabaseName.DATABASE_NAME.value,
                    regions=Region,
                    queue=RankedQueue.RANKED_SOLO_5x5.value,
                    api_key=self.api_key,
                    tiers=RankedTier,
                    pages=DataProcessingConfig.PAGE_LIMIT,
                    divisions=RankedDivision,
                    logger=self.logger,
                    token_bucket=self.TokenBucketLocal
                )
            
        if stage_2:
            self.logger.info("Activating Stage 2: Match ID Collection Service")
            self.MatchIDCollectionService = \
                MatchIDCollectionService(
                    db_location=Paths.DATA,
                    database_name=DatabaseName.DATABASE_NAME.value,
                    continents=ContinentalRegion,
                    queue=RankedQueue.RANKED_SOLO_5x5.value,
                    api_key=self.api_key,
                    tiers=RankedTier,
                    pages=DataProcessingConfig.PAGE_LIMIT,
                    divisions=RankedDivision,
                    logger=self.logger,
                    token_bucket_continental=self.TokenBucketContinent,
                    token_bucket_local=self.TokenBucketLocal,
                    game_type=QueueMatchV5.RANKED.value
                )
            
        if stage_3:
            self.logger.info("Activating Stage 3: Match Data Service")
            self.MatchDataService = \
                MatchDataService(
                    db_location=Paths.DATA,
                    database_name=DatabaseName.DATABASE_NAME.value,
                    continents=ContinentalRegion,
                    api_key=self.api_key,
                    logger=self.logger,
                    token_bucket=self.TokenBucketContinent
                )
            
        if stage_4:
            self.logger.info("Activating Stage 4: Match Timeline Service")
            self.MatchTimelineService = \
                MatchTimelineService(
                    db_location=Paths.DATA,
                    database_name=DatabaseName.DATABASE_NAME.value,
                    continents=ContinentalRegion,
                    api_key=self.api_key,
                    logger=self.logger,
                    token_bucket=self.TokenBucketContinent
                )

    def start_pipeline(self):
        """
        Execute the data collection pipeline stages in sequence.
        
        This method runs the active pipeline stages in the correct order:
        1. Collect summoner data from ranked ladders
        2. Collect match IDs from summoner match history
        3. Collect detailed match data
        4. Collect match timeline events
        
        Each stage runs asynchronously and only executes if the corresponding
        service was activated in activate_data_collection_services().
        
        The @stage_starter decorator provides additional logging and timing
        functionality for monitoring pipeline execution.
        """
        stage_1 = Stages.TO_PROCESS[0]
        stage_2 = Stages.TO_PROCESS[1]
        stage_3 = Stages.TO_PROCESS[2]
        stage_4 = Stages.TO_PROCESS[3]

        if stage_1 and self.SummonerCollectionService:
            self.logger.info("Starting Stage 1: Summoner Data Collection")
            try:
                asyncio.run(self.SummonerCollectionService.async_get_and_save_summoner_entries())
                self.logger.info("Stage 1 completed successfully")
            except Exception as e:
                self.logger.error(f"Stage 1 failed with error: {str(e)}")
                raise

        if stage_2 and self.MatchIDCollectionService:
            self.logger.info("Starting Stage 2: Match ID Collection")
            try:
                asyncio.run(self.MatchIDCollectionService.async_get_and_save_match_ids())
                self.logger.info("Stage 2 completed successfully")
            except Exception as e:
                self.logger.error(f"Stage 2 failed with error: {str(e)}")
                raise

        if stage_3 and self.MatchDataService:
            self.logger.info("Starting Stage 3: Match Data Collection")
            try:
                asyncio.run(self.MatchDataService.async_get_and_save_match_data())
                self.logger.info("Stage 3 completed successfully")
            except Exception as e:
                self.logger.error(f"Stage 3 failed with error: {str(e)}")
                raise

        if stage_4 and self.MatchTimelineService:
            self.logger.info("Starting Stage 4: Match Timeline Collection")
            try:
                asyncio.run(self.MatchTimelineService.async_get_and_save_match_data())
                self.logger.info("Stage 4 completed successfully")
            except Exception as e:
                self.logger.error(f"Stage 4 failed with error: {str(e)}")
                raise

        self.logger.info("Pipeline execution completed")

    def run_full_pipeline(self):
        """
        Execute the complete pipeline from service activation to completion.
        
        This convenience method combines service activation and pipeline execution
        into a single call, providing a simple interface for running the entire
        data collection pipeline.
        
        Raises:
            Exception: Propagates any exceptions from service activation or execution.
        """
        try:
            self.logger.info("Starting full pipeline execution")
            self.activate_data_collection_services()
            self.start_pipeline()
            self.logger.info("Full pipeline execution completed successfully")
        except Exception as e:
            self.logger.error(f"Full pipeline execution failed: {str(e)}")
            raise

