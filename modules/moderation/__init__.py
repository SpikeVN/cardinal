import logger
from .commands import Moderation


def setup(bot):
    logger.debug("loaded")
    bot.add_cog(Moderation(bot))
