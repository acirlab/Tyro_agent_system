from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from voice_agent.audio.runtime import build_audio_transport, read_file_chunks
from voice_agent.audio.transport import NullAudioTransport
from voice_agent.bootstrap import build_text_runtime, build_turn_engine
from voice_agent.config import DEFAULT_CONFIG_PATH, DEFAULT_TUNING_CONFIG_PATH, load_app_config
from voice_agent.turn.engine import UserTurn
from voice_agent.turn.interruption import InterruptionController


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Tyro duplex voice agent MVP.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="JSON config path.")
    parser.add_argument(
        "--tuning-config",
        default=str(DEFAULT_TUNING_CONFIG_PATH),
        help="JSON/JSONC tuning config path for VAD/EOT/interruption thresholds.",
    )
    parser.add_argument("--text", help="Run one text turn without microphone input.")
    parser.add_argument("--file", help="Run one user turn from a wav/audio file.")
    parser.add_argument("--live", action="store_true", help="Use microphone and speaker transport.")
    parser.add_argument("--mock-asr-text", help="Bypass ASR with fixed text while still exercising pVAD/EOT flow.")
    parser.add_argument("--llm-provider", choices=["qwen", "fake"], help="Override LLM provider.")
    parser.add_argument("--tts-provider", choices=["kokoro", "fake"], help="Override TTS provider.")
    parser.add_argument("--no-tts", action="store_true", default=None, help="Do not synthesize speech.")
    parser.add_argument("--no-play", action="store_true", default=None, help="Do not play synthesized speech.")
    parser.add_argument("--disable-expression", action="store_true", default=False, help="Disable expression video window.")
    parser.add_argument("--enable-expression", action="store_true", default=False, help="Enable expression video window.")
    parser.add_argument("--max-turns", type=int, help="Stop live mode after this many completed user turns.")
    return parser


def apply_overrides(config, args: argparse.Namespace):
    if args.mock_asr_text is not None:
        config.runtime.mock_asr_text = args.mock_asr_text
    if args.llm_provider is not None:
        config.llm.provider = args.llm_provider
    if args.tts_provider is not None:
        config.tts.provider = args.tts_provider
    if args.no_tts is not None:
        config.runtime.no_tts = args.no_tts
    if args.no_play is not None:
        config.runtime.no_play = args.no_play
    if args.max_turns is not None:
        config.runtime.max_turns = args.max_turns
    if args.disable_expression:
        config.expression.enabled = False
    if args.enable_expression:
        config.expression.enabled = True
    return config


async def run_text(text: str, config) -> None:
    transport = NullAudioTransport()
    controller, scheduler, agent_runtime, _event_bus = build_text_runtime(config, transport)
    try:
        turn = UserTurn(text=text, audio=b"", eot_probability=1.0, finish_reason="text")
        await controller.handle_turn(turn)
        task = agent_runtime.current_task
        if task is not None and task.runner is not None:
            await task.runner
        await asyncio.sleep(0.1)
    finally:
        await scheduler.stop()


async def run_file(path: str, config) -> None:
    transport = NullAudioTransport()
    controller, scheduler, agent_runtime, _event_bus = build_text_runtime(config, transport)
    turn_engine = build_turn_engine(config)
    try:
        for chunk in read_file_chunks(path, config.audio.chunk_seconds):
            await turn_engine.push_audio(chunk)
        turn = await turn_engine.finish_stream()
        if turn is None:
            print("No complete user turn detected.")
            return
        await controller.handle_turn(turn)
        task = agent_runtime.current_task
        if task is not None and task.runner is not None:
            await task.runner
        await asyncio.sleep(0.1)
    finally:
        await scheduler.stop()


async def run_live(config) -> None:
    transport = build_audio_transport(config.audio, config.aec)
    turn_engine = build_turn_engine(config)
    controller, scheduler, _agent_runtime, _event_bus = build_text_runtime(config, transport)
    interruption = InterruptionController(config.interruption, config.pvad, turn_engine, scheduler)
    completed = 0
    transport.start()
    print("Listening. Press Ctrl+C to stop.")
    try:
        async for frame in transport.read_frames():
            # During assistant playback, interruption gets first pass over mic
            # audio. Confirmed interruption audio is injected back into the turn
            # engine, so it should not be pushed a second time here.
            interrupted = await interruption.on_audio(frame)
            if not interrupted:
                await turn_engine.push_audio(frame)
            while not turn_engine.completed_turns.empty():
                turn = await turn_engine.get_completed_turn()
                await controller.handle_turn(turn)
                completed += 1
                if config.runtime.max_turns and completed >= config.runtime.max_turns:
                    return
    finally:
        await scheduler.stop()
        if transport.status_messages:
            print("Audio stream status messages:")
            for message in transport.status_messages:
                print(f"  {message}")
        transport.close()


async def async_main() -> None:
    args = build_arg_parser().parse_args()
    config = apply_overrides(load_app_config(args.config, args.tuning_config), args)
    if args.text:
        await run_text(args.text, config)
        return
    if args.file:
        if not Path(args.file).exists():
            raise FileNotFoundError(args.file)
        await run_file(args.file, config)
        return
    if args.live:
        await run_live(config)
        return
    raise SystemExit("Use --text, --file, or --live.")


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
