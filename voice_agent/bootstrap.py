from __future__ import annotations

from voice_agent.agent.llm import build_llm, build_qwen_llm
from voice_agent.agent.runtime import AgentRuntime
from voice_agent.config import AppConfig
from voice_agent.conversation.controller import ConversationController
from voice_agent.expression.controller import ExpressionVideoController
from voice_agent.expression.selector import ExpressionSelector
from voice_agent.infrastructure.event_bus import EventBus
from voice_agent.model_loading import configure_local_model_loading
from voice_agent.skills.registry import build_default_skill_registry
from voice_agent.speech.feedback import FeedbackController
from voice_agent.speech.scheduler import SpeechScheduler
from voice_agent.speech.tts import TTSRunner
from voice_agent.tools.builtin import AcademicResearchTool, FakeLongTaskTool, WebSearchTool
from voice_agent.tools.registry import ToolRegistry
from voice_agent.research.clients.crossref import CrossrefClient
from voice_agent.research.clients.dashscope import DashScopeEmbeddingClient, DashScopeReranker
from voice_agent.research.full_text import FullTextFetcher
from voice_agent.research.pipeline import AcademicResearchPipeline
from voice_agent.turn.asr import ASRRunner
from voice_agent.turn.eot import AlwaysEndDetector, EndOfTurnDetector
from voice_agent.turn.engine import UserTurnEngine


def build_academic_research_pipeline(config) -> AcademicResearchPipeline:
    embedding_client = None
    reranker = None
    if config.use_embeddings:
        embedding_client = DashScopeEmbeddingClient(
            model=config.embedding_model,
            api_key_env=config.api_key_env,
            base_url=config.base_url,
        )
    if config.use_rerank:
        reranker = DashScopeReranker(model=config.rerank_model, api_key_env=config.api_key_env)
    full_text_fetcher = FullTextFetcher(config.full_text_cache_dir) if config.fetch_full_text else None
    return AcademicResearchPipeline(
        crossref=CrossrefClient(),
        embedding_client=embedding_client,
        reranker=reranker,
        full_text_fetcher=full_text_fetcher,
        fetch_full_text=config.fetch_full_text,
        max_full_text_papers=config.max_full_text_papers,
        max_search_queries=config.max_search_queries,
        search_timeout_seconds=config.search_timeout_seconds,
        max_chunks_per_report=config.max_chunks_per_report,
        chunk_chars=config.chunk_chars,
        chunk_overlap=config.chunk_overlap,
    )


def build_research_llm(config):
    if not config.enabled:
        return None
    return build_qwen_llm(
        model=config.writer_model,
        api_key_env=config.api_key_env,
        base_url=config.base_url,
        max_tokens=config.writer_max_tokens,
        timeout_seconds=config.timeout_seconds,
    )


def build_tool_registry(llm=None, research_config=None) -> ToolRegistry:
    registry = ToolRegistry()
    pipeline = build_academic_research_pipeline(research_config) if research_config is not None else None
    if research_config is not None and llm is not None and llm.__class__.__name__ != "FakeLLM":
        research_llm = build_research_llm(research_config)
    else:
        research_llm = llm
    registry.register(
        AcademicResearchTool(
            pipeline=pipeline,
            llm=research_llm,
            enable_llm_writer=research_config.use_llm_writer if research_config is not None else False,
            pipeline_timeout_seconds=research_config.pipeline_timeout_seconds if research_config is not None else 180.0,
            writer_timeout_seconds=research_config.writer_timeout_seconds if research_config is not None else 120.0,
        )
    )
    registry.register(FakeLongTaskTool())
    registry.register(WebSearchTool())
    return registry


def build_text_runtime(config: AppConfig, transport) -> tuple[ConversationController, SpeechScheduler, AgentRuntime, EventBus]:
    configure_local_model_loading(config.model_loading)
    event_bus = EventBus()
    llm = build_llm(config.llm)
    tts_runner = None if config.runtime.no_tts else TTSRunner(config.tts, config.model_loading)
    expression_controller = ExpressionVideoController(config.expression)
    expression_selector = ExpressionSelector(
        llm=llm,
        available_expressions=expression_controller.available_expressions,
        choose_with_llm=config.expression.choose_with_llm,
    )
    speech_scheduler = SpeechScheduler(
        tts_runner=tts_runner,
        transport=transport,
        no_tts=config.runtime.no_tts,
        no_play=config.runtime.no_play,
        expression_controller=expression_controller,
        expression_selector=expression_selector,
        reset_expression_after_speech=config.expression.reset_to_neutral_after_speech,
    )
    skill_registry = build_default_skill_registry()
    agent_runtime = AgentRuntime(
        llm=llm,
        tool_registry=build_tool_registry(llm, config.research),
        skill_registry=skill_registry,
        speech_scheduler=speech_scheduler,
        event_bus=event_bus,
    )
    feedback = FeedbackController(event_bus, speech_scheduler)
    speech_scheduler.start()
    feedback.start()
    controller = ConversationController(agent_runtime, speech_scheduler)
    return controller, speech_scheduler, agent_runtime, event_bus


def build_turn_engine(config: AppConfig) -> UserTurnEngine:
    configure_local_model_loading(config.model_loading)
    asr_runner = ASRRunner(config.asr, config.model_loading, mock_text=config.runtime.mock_asr_text)
    if config.runtime.mock_asr_text:
        eot_detector = AlwaysEndDetector()
    else:
        eot_detector = EndOfTurnDetector(config.eot, config.model_loading)
    engine = UserTurnEngine(config.pvad, asr_runner, eot_detector)
    engine.debug_save_asr_audio_dir = config.runtime.debug_save_asr_audio_dir
    return engine
