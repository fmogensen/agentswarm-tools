"""
Example usage of the PodcastGenerator tool.

This script demonstrates various use cases and features.
"""

import os

from tools.media_generation.podcast_generator import PodcastGenerator


def example_1_basic_podcast():
    """Example 1: Basic 2-speaker tech podcast."""
    print("\n" + "=" * 70)
    print("Example 1: Basic 2-Speaker Tech Podcast")
    print("=" * 70)

    tool = PodcastGenerator(
        topic="The Impact of AI on Software Development",
        duration_minutes=10,
        num_speakers=2,
        speaker_personalities=["enthusiastic tech host", "experienced developer"],
        background_music=True,
        music_style="upbeat",
    )

    result = tool.run()

    print(f"✓ Success: {result['success']}")
    print(f"✓ Podcast URL: {result['podcast_url']}")
    print(
        f"✓ Duration: {result['duration_seconds']} seconds ({result['duration_seconds']//60} minutes)"
    )
    print(f"✓ Format: {result['metadata']['format'].upper()}")
    print(f"✓ File Size: {result['metadata']['file_size_mb']} MB")
    print(f"\nSpeakers:")
    for speaker in result["speakers_used"]:
        print(f"  - {speaker['personality']} (voice: {speaker['voice_model']})")


def example_2_educational_podcast():
    """Example 2: Educational podcast with 3 speakers."""
    print("\n" + "=" * 70)
    print("Example 2: Educational Panel Discussion")
    print("=" * 70)

    tool = PodcastGenerator(
        topic="Climate Change and Renewable Energy",
        duration_minutes=20,
        num_speakers=3,
        speaker_personalities=[
            "professional moderator",
            "climate scientist",
            "renewable energy expert",
        ],
        background_music=True,
        music_style="calm",
        output_format="mp3",
    )

    result = tool.run()

    print(f"✓ Success: {result['success']}")
    print(f"✓ Podcast URL: {result['podcast_url']}")
    print(f"✓ Duration: {result['duration_seconds']//60} minutes")
    print(f"✓ Music Style: {result['metadata']['music_style']}")
    print(f"\nTranscript Preview:")
    print(result["transcript"][:400] + "...")


def example_3_solo_meditation():
    """Example 3: Solo meditation guide podcast."""
    print("\n" + "=" * 70)
    print("Example 3: Solo Meditation Guide")
    print("=" * 70)

    tool = PodcastGenerator(
        topic="5-Minute Morning Meditation",
        duration_minutes=5,
        num_speakers=1,
        speaker_personalities=["calm meditation instructor"],
        background_music=True,
        music_style="calm",
        add_intro=False,
        add_outro=False,
        output_format="wav",
    )

    result = tool.run()

    print(f"✓ Success: {result['success']}")
    print(f"✓ Podcast URL: {result['podcast_url']}")
    print(f"✓ Duration: {result['duration_seconds']} seconds")
    print(f"✓ Format: {result['metadata']['format']}")
    print(f"✓ Has Intro: {result['metadata']['has_intro']}")
    print(f"✓ Has Outro: {result['metadata']['has_outro']}")


def example_4_custom_script():
    """Example 4: Podcast with custom script."""
    print("\n" + "=" * 70)
    print("Example 4: Custom Script Interview")
    print("=" * 70)

    custom_script = """
Speaker 1: Welcome to Founder Stories! Today we have an amazing guest.
Speaker 2: Thanks for having me, I'm excited to be here.
Speaker 1: Let's start with your journey. When did you first get the idea for your startup?
Speaker 2: It was actually during my last year of college. I noticed a gap in the market.
Speaker 1: That's fascinating. What was the biggest challenge you faced early on?
Speaker 2: Definitely fundraising. It took months to find the right investors.
Speaker 1: And how did you overcome that?
Speaker 2: Persistence and refining our pitch based on feedback.
"""

    tool = PodcastGenerator(
        topic="Founder Interview: Building a Tech Startup",
        duration_minutes=15,
        num_speakers=2,
        speaker_personalities=["experienced interviewer", "energetic entrepreneur"],
        script_content=custom_script.strip(),
        background_music=True,
        music_style="corporate",
    )

    result = tool.run()

    print(f"✓ Success: {result['success']}")
    print(f"✓ Podcast URL: {result['podcast_url']}")
    print(f"✓ Using custom script: Yes")
    print(f"\nGenerated Transcript:")
    print(result["transcript"])


def example_5_roundtable():
    """Example 5: 4-speaker roundtable discussion."""
    print("\n" + "=" * 70)
    print("Example 5: 4-Speaker Roundtable Discussion")
    print("=" * 70)

    tool = PodcastGenerator(
        topic="The Future of Remote Work",
        duration_minutes=25,
        num_speakers=4,
        speaker_personalities=[
            "moderator and facilitator",
            "tech company CEO",
            "HR consultant",
            "remote work advocate",
        ],
        background_music=False,  # No music for focused discussion
        music_style="none",
        voice_consistency=True,
    )

    result = tool.run()

    print(f"✓ Success: {result['success']}")
    print(f"✓ Podcast URL: {result['podcast_url']}")
    print(f"✓ Duration: {result['duration_seconds']//60} minutes")
    print(f"✓ Background Music: {result['metadata']['music_included']}")
    print(f"✓ Voice Consistency: Enabled")
    print(f"\nSpeaker Configuration:")
    for i, speaker in enumerate(result["speakers_used"], 1):
        print(f"  Speaker {i}: {speaker['personality']}")
        print(f"    Voice Model: {speaker['voice_model']}")
        print(f"    Settings: {speaker['voice_settings']}")


def example_6_error_handling():
    """Example 6: Demonstrate error handling."""
    print("\n" + "=" * 70)
    print("Example 6: Error Handling Demo")
    print("=" * 70)

    print("\nAttempting to create podcast with mismatched speaker count...")
    try:
        tool = PodcastGenerator(
            topic="Test",
            duration_minutes=10,
            num_speakers=3,
            speaker_personalities=["host", "guest"],  # Only 2, but need 3
        )
        result = tool.run()
    except Exception as e:
        print(f"✓ Caught expected error: {type(e).__name__}")
        print(f"  Message: {str(e)[:100]}")

    print("\nAttempting to create podcast with empty topic...")
    os.environ["USE_MOCK_APIS"] = "true"
    tool2 = PodcastGenerator(
        topic="   ", duration_minutes=10, num_speakers=1, speaker_personalities=["host"]  # Empty
    )
    result2 = tool2.run()
    print(f"✓ Error response received: {result2['success']}")
    print(f"  Error code: {result2['error']['code']}")


def main():
    """Run all examples."""
    print("\n" + "#" * 70)
    print("# Podcast Generator Tool - Usage Examples")
    print("#" * 70)
    print("\nNote: Running in MOCK mode (USE_MOCK_APIS=true)")
    print("Set OPENAI_API_KEY environment variable for production use\n")

    # Enable mock mode for all examples
    os.environ["USE_MOCK_APIS"] = "true"

    # Run all examples
    example_1_basic_podcast()
    example_2_educational_podcast()
    example_3_solo_meditation()
    example_4_custom_script()
    example_5_roundtable()
    example_6_error_handling()

    print("\n" + "#" * 70)
    print("# All examples completed successfully!")
    print("#" * 70)
    print("\nNext Steps:")
    print("1. Set OPENAI_API_KEY environment variable")
    print("2. Remove USE_MOCK_APIS or set to 'false'")
    print("3. Run your podcast generation in production mode")
    print("\nFor more details, see README.md")


if __name__ == "__main__":
    main()
