from __future__ import annotations

from .block_group import BlockGroup


class DefaultBlockGroups:
    """The groups shipped with the app."""

    @staticmethod
    def create() -> tuple[BlockGroup, ...]:
        return (
            BlockGroup("YouTube", ("youtube.com", "youtu.be", "music.youtube.com", "youtube-nocookie.com")),
            BlockGroup("Instagram", ("instagram.com",)),
            BlockGroup("Facebook", ("facebook.com", "fb.com", "messenger.com")),
            BlockGroup("TikTok", ("tiktok.com", "tiktokv.com")),
            BlockGroup("X / Twitter", ("x.com", "twitter.com", "mobile.twitter.com")),
            BlockGroup("Reddit", ("reddit.com", "old.reddit.com", "new.reddit.com", "redd.it")),
            BlockGroup("Twitch", ("twitch.tv",)),
            BlockGroup("Kwai", ("kwai.com",)),
            BlockGroup("Pinterest", ("pinterest.com", "br.pinterest.com")),
            BlockGroup("Netflix", ("netflix.com",)),
            BlockGroup("Prime Video", ("primevideo.com",)),
            BlockGroup("Disney+", ("disneyplus.com",)),
            BlockGroup("Max", ("max.com", "play.max.com", "hbomax.com")),
            BlockGroup("Globoplay", ("globoplay.globo.com",)),
            BlockGroup("Sports", ("ge.globo.com", "espn.com.br", "placardefutebol.com.br")),
            BlockGroup("Discord", ("discord.com", "discord.gg", "discordapp.com"), ("discord",)),
            BlockGroup("Steam", ("store.steampowered.com", "steamcommunity.com"), ("steam", "steam_osx")),
        )
