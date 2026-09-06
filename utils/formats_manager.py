# Raw yt-dlp format IDs (e.g. '137', 'h264_540p_299944-0') are NOT
# stable across videos or platforms — Facebook and TikTok generate a
# new random ID per video, so letting the user pick/save one and
# reuse it breaks on the very next download. Quality tiers instead
# translate to a yt-dlp format *selector* + a 'format_sort' rule,
# which yt-dlp re-resolves dynamically against whatever formats the
# current video/platform actually has.
#
# 'res:<n>' in format_sort works for both landscape and portrait
# video (YouTube vs. Facebook Reels / TikTok) because yt-dlp compares
# against the meaningful dimension either way, instead of a strict
# 'height<=n' filter which would silently match nothing on portrait
# video (e.g. TikTok's 576x1024 has height=1024, not <=720).
# 'proto' as a tiebreaker prefers direct/https formats over m3u8
# streaming formats, which tends to be more stable to download.
QUALITY_PRESETS = {
    "best": {
        "label": "Best Available Quality",
        "format": "bv*+ba/b",
        "sort": None,
    },
    "720p": {
        "label": "Medium Quality (720p) - Recommended",
        "format": "bv*+ba/b",
        "sort": ["res:720", "proto"],
    },
    "480p": {
        "label": "Low Quality (480p) - Saves Space",
        "format": "bv*+ba/b",
        "sort": ["res:480", "proto"],
    },
    "audio": {
        "label": "Audio Only",
        "format": "ba/b",
        "sort": None,
    },
}


class FormatsManager:

    def select_format(self):
        """Display the quality menu and return the selected preset
        key (e.g. '720p'), or a custom raw format string typed
        manually via the advanced option."""
        options = {}
        actions = {}
        for i, (key, preset) in enumerate(QUALITY_PRESETS.items(), 1):
            options[str(i)] = preset["label"]
            actions[str(i)] = (lambda k=key: k)
        custom_key = str(len(QUALITY_PRESETS) + 1)
        options[custom_key] = "Advanced: Enter Format ID Manually"
        actions[custom_key] = self._prompt_custom_format
        from menus.menu import Menu
        format_menu = Menu(
            title="Select Quality",
            options=options,
            actions=actions
        )
        while True:
            result = format_menu.run()
            # Loop only on an invalid/empty choice
            if result:
                return result

    def _prompt_custom_format(self):
        """One-off manual format ID / yt-dlp format selector, for
        advanced use. Intentionally NOT saved for reuse, since raw
        format IDs are video-specific on most platforms."""
        header = "=" * 38 + f"\n{' ' * 5}Enter Format ID / Selector Manually\n" + "=" * 38
        print(header)
        custom_format = input("Enter Format ID or selector: ").strip()
        if not custom_format:
            print("❌ No value entered")
            return None
        return custom_format

    @staticmethod
    def resolve(format_value):
        """
        Translate a value returned by select_format() into the
        actual yt-dlp 'format' selector plus an optional
        'format_sort' list.

        Known quality-preset keys ('best' / '720p' / '480p' /
        'audio') are translated via QUALITY_PRESETS. Anything else —
        a manually-entered raw format ID/selector, or a legacy value
        already stored in download history from before this change
        (e.g. an old saved 'hd') — is passed straight through to
        yt-dlp untouched, exactly like before.
        """
        preset = QUALITY_PRESETS.get(format_value)
        if preset:
            return preset["format"], preset["sort"]
        return format_value, None
