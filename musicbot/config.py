import os
import sys
import codecs
import shutil
import logging
import configparser

from .exceptions import HelpfulError

LOG = logging.getLogger(__name__)


class Config:
    """ TODO """
    # noinspection PyUnresolvedReferences
    def __init__(self, config_file):
        self.config_file = config_file
        self.find_config()

        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file, encoding='utf-8')

        confsections = {"Credentials", "Permissions", "Chat", "MusicBot"} \
            .difference(config.sections())
        if confsections:
            raise HelpfulError(
                "One or more required config sections are missing.",
                "Fix your config!"
                "Each [Section] should be on its own line with "
                "nothing else on it. The following sections are missing: {}"
                .format(', '.join(['[%s]' % s for s in confsections])),
                preface="An error has occured parsing the config:\n"
            )

        self._confpreface = "An error has occured reading the config:\n"
        self._confpreface2 = "An error has occured validating the config:\n"

        self._login_token = config.get(
            'Credentials', 'Token', fallback=ConfigDefaults.token)
        self._email = config.get(
            'Credentials', 'Email', fallback=ConfigDefaults.email)
        self._password = config.get(
            'Credentials', 'Password', fallback=ConfigDefaults.password)
        self.auth = ()
        self.owner_id = config.get(
            'Permissions', 'OwnerID', fallback=ConfigDefaults.owner_id)
        self.dev_ids = config.get(
            'Permissions', 'DevIDs', fallback=ConfigDefaults.dev_ids)
        self.command_prefix = config.get(
            'Chat', 'CommandPrefix', fallback=ConfigDefaults.command_prefix)
        self.bound_channels = config.get(
            'Chat', 'BindToChannels', fallback=ConfigDefaults.bound_channels)
        self.autojoin_channels = config.get(
            'Chat', 'AutojoinChannels',
            fallback=ConfigDefaults.autojoin_channels)
        self.default_volume = config.getfloat(
            'MusicBot', 'DefaultVolume',
            fallback=ConfigDefaults.default_volume)
        self.max_volume = config.getint(
            'MusicBot', 'MaxVolume', fallback=ConfigDefaults.max_volume)
        self.skips_required = config.getint(
            'MusicBot', 'SkipsRequired',
            fallback=ConfigDefaults.skips_required)
        self.skip_ratio_required = config.getfloat(
            'MusicBot', 'SkipRatio',
            fallback=ConfigDefaults.skip_ratio_required)
        self.timeout = config.getfloat(
            'MusicBot', 'TimeOut', fallback=ConfigDefaults.timeout)
        self.save_videos = config.getboolean(
            'MusicBot', 'SaveVideos',
            fallback=ConfigDefaults.save_videos)
        self.show_thumbnails = config.getboolean(
            'MusicBot', 'ShowThumbnails',
            fallback=ConfigDefaults.show_thumbnails)
        self.now_playing_mentions = config.getboolean(
            'MusicBot', 'NowPlayingMentions',
            fallback=ConfigDefaults.now_playing_mentions)
        self.auto_summon = config.getboolean(
            'MusicBot', 'AutoSummon',
            fallback=ConfigDefaults.auto_summon)
        self.auto_playlist = config.getboolean(
            'MusicBot', 'AutoPlaylist',
            fallback=ConfigDefaults.auto_playlist)
        self.auto_pause = config.getboolean(
            'MusicBot', 'AutoPause',
            fallback=ConfigDefaults.auto_pause)
        self.delete_messages = config.getboolean(
            'MusicBot', 'DeleteMessages',
            fallback=ConfigDefaults.delete_messages)
        self.delete_invoking = config.getboolean(
            'MusicBot', 'DeleteInvoking',
            fallback=ConfigDefaults.delete_invoking)
        self.persistent_queue = config.getboolean(
            'MusicBot', 'PersistentQueue',
            fallback=ConfigDefaults.persistent_queue)
        self.debug_mode = config.getboolean(
            'MusicBot', 'DebugMode', fallback=ConfigDefaults.debug_mode)
        self.debug_level = config.get(
            'MusicBot', 'DebugLevel', fallback=ConfigDefaults.debug_level)
        self.debug_level_str = self.debug_level
        self.blacklist_file = config.get(
            'Files', 'BlacklistFile', fallback=ConfigDefaults.blacklist_file)
        self.auto_playlist_file = config.get(
            'Files', 'AutoPlaylistFile',
            fallback=ConfigDefaults.auto_playlist_file)
        self.banned_file = config.get(
            'Files', 'BannedFile', fallback=ConfigDefaults.banned_file)
        self.auto_playlist_removed_file = None

        self.run_checks()

        self.find_autoplaylist()

    def run_checks(self):
        """
        Validation logic for bot settings.
        """

        if self._email or self._password:
            if not self._email:
                raise HelpfulError(
                    "The login email was not specified in the config.",

                    "Please put your bot account credentials in the config.  "
                    "Remember that the Email is the email address used to \
                    register the bot account.",
                    preface=self._confpreface)

            if not self._password:
                raise HelpfulError(
                    "The password was not specified in the config.",

                    "Please put your bot account credentials in the config.",
                    preface=self._confpreface)

            self.auth = (self._email, self._password)

        elif not self._login_token:
            raise HelpfulError(
                "No login credentials were specified in the config.",

                "Please fill in either the Email and Password fields, or "
                "the Token field.  The Token field is for Bot accounts only.",
                preface=self._confpreface
            )

        else:
            self.auth = (self._login_token,)

        if self.owner_id:
            self.owner_id = self.owner_id.lower()

            if self.owner_id.isdigit():
                if int(self.owner_id) < 10000:
                    raise HelpfulError(
                        "An invalid OwnerID was set: {}".format(self.owner_id),

                        "Correct your OwnerID.  "
                        "The ID should be just a number, approximately "
                        "18 characters long.  "
                        "If you don't know what your ID is, read the "
                        "instructions in the options or ask in the "
                        "help server.",
                        preface=self._confpreface
                    )

            elif self.owner_id == 'auto':
                pass  # defer to async check

            else:
                self.owner_id = None

        if not self.owner_id:
            raise HelpfulError(
                "No OwnerID was set.",
                "Please set the OwnerID option in {}".format(self.config_file),
                preface=self._confpreface
            )

        if self.bound_channels:
            try:
                self.bound_channels = set(
                    x for x in self.bound_channels.split() if x)
            except:
                LOG.warning(
                    "BindToChannels data is invalid, \
                    will not bind to any channels")
                self.bound_channels = set()

        if self.autojoin_channels:
            try:
                self.autojoin_channels = set(
                    x for x in self.autojoin_channels.split() if x)
            except:
                LOG.warning("AutojoinChannels data is invalid, \
                will not autojoin any channels")
                self.autojoin_channels = set()

        if self.max_volume < 1 or self.max_volume > 1000:
            if self.max_volume < 1:
                LOG.warning("Max Volume is {}%, \
                which is less than 1%, defaulting to 100%."
                            .format(self.max_volume))
            elif self.max_volume > 1000:
                LOG.warning("Max Volume is {}%, \
                which is greater than 1000%, defaulting to 100%."
                            .format(self.max_volume))
            self.max_volume = 100

        self.delete_invoking = self.delete_invoking and self.delete_messages

        self.bound_channels = set(item.replace(',', ' ').strip()
                                  for item in self.bound_channels)

        self.autojoin_channels = set(item.replace(
            ',', ' ').strip() for item in self.autojoin_channels)

        ap_path, ap_name = os.path.split(self.auto_playlist_file)
        apn_name, apn_ext = os.path.splitext(ap_name)
        self.auto_playlist_removed_file = os.path.join(
            ap_path, apn_name + '_removed' + apn_ext)

        if hasattr(logging, self.debug_level.upper()):
            self.debug_level = getattr(logging, self.debug_level.upper())
        else:
            LOG.warning(
                "Invalid DebugLevel option %s given, falling back to INFO",
                self.debug_level_str)
            self.debug_level = logging.INFO
            self.debug_level_str = 'INFO'

        self.debug_mode = self.debug_level <= logging.DEBUG

    # TODO: Add save function for future editing of options with commands
    #       Maybe add warnings about fields missing from the config file

    async def async_validate(self, bot):
        """ TODO """
        LOG.debug("Validating options...")

        if self.owner_id == 'auto':
            if not bot.user.bot:
                raise HelpfulError(
                    "Invalid parameter \"auto\" for OwnerID option.",

                    "Only bot accounts can use the \"auto\" option.  Please "
                    "set the OwnerID in the config.",

                    preface=self._confpreface2
                )

            self.owner_id = bot.cached_app_info.owner.id
            LOG.debug("Aquired owner id via API")

        if self.owner_id == bot.user.id:
            raise HelpfulError(
                "Your OwnerID is incorrect or you've used the "
                "wrong credentials.",

                "The bot's user ID and the id for OwnerID is identical.  "
                "This is wrong.  The bot needs its own account to function, "
                "meaning you cannot use your own account to run the bot on.  "
                "The OwnerID is the id of the owner, not the bot.  "
                "Figure out which one is which and use "
                "the correct information.",

                preface=self._confpreface2
            )

    def find_config(self):
        """ TODO """
        config = configparser.ConfigParser(interpolation=None)

        if not os.path.isfile(self.config_file):
            if os.path.isfile(self.config_file + '.ini'):
                shutil.move(self.config_file + '.ini', self.config_file)
                LOG.info("Moving {0} to {1}, \
                         you should probably turn file extensions on."
                         .format(self.config_file + '.ini', self.config_file))

            elif os.path.isfile('config/example_options.ini'):
                shutil.copy('config/example_options.ini', self.config_file)
                LOG.warning(
                    'Options file not found, copying example_options.ini')

            else:
                raise HelpfulError(
                    "Your config files are missing.  Neither options.ini nor "
                    "example_options.ini were found.",
                    "Grab the files back from the archive or remake them "
                    "yourself and copy paste the content "
                    "from the repo.  Stop removing important files!"
                )

        if not config.read(self.config_file, encoding='utf-8'):
            config = configparser.ConfigParser()
            try:
                # load the config again and check to see if the user edited
                # that one
                config.read(self.config_file, encoding='utf-8')

                # jake pls no flame
                if not int(config.get('Permissions', 'OwnerID', fallback=0)):
                    print(flush=True)
                    LOG.critical(
                        "Please configure config/options.ini \
                        and re-run the bot.")
                    sys.exit(1)

            except ValueError:  # Config id value was changed but its not valid
                raise HelpfulError(
                    'Invalid value "{}" for OwnerID, config cannot be loaded.'
                    .format(config.get('Permissions', 'OwnerID', fallback=None)),
                    "The OwnerID option takes a user id, \
                    fuck it i'll finish this message later."
                )

            except Exception as error:
                print(flush=True)
                LOG.critical(
                    "Unable to copy config/example_options.ini to %s",
                    self.config_file, exc_info=error)
                sys.exit(2)

    def find_autoplaylist(self):
        """ TODO """
        if not os.path.exists(self.auto_playlist_file):
            if os.path.exists('config/example_autoplaylist.txt'):
                shutil.copy('config/example_autoplaylist.txt',
                            self.auto_playlist_file)
                LOG.debug("Copying example_autoplaylist.txt to autoplaylist.txt")
            else:
                LOG.warning("No autoplaylist file found.")

    def write_default_config(self, location):
        """ TODO """
        pass


class ConfigDefaults:
    """ TODO """
    token = None
    email = None
    password = None
    owner_id = None
    dev_ids = set()
    command_prefix = '!'
    bound_channels = set()
    autojoin_channels = set()
    default_volume = 0.15
    max_volume = 100
    skips_required = 4
    skip_ratio_required = 0.5
    timeout = 10.0
    save_videos = True
    show_thumbnails = True
    now_playing_mentions = False
    auto_summon = True
    auto_playlist = True
    auto_pause = True
    delete_messages = True
    delete_invoking = False
    persistent_queue = True
    debug_mode = False
    debug_level = 'INFO'

    blacklist_file = 'config/blacklist.txt'
    # TODO this will change when I add playlists
    auto_playlist_file = 'config/autoplaylist.txt'
    banned_file = 'config/banned.txt'
    options_file = 'config/options.ini'


setattr(ConfigDefaults, codecs.decode(
    b'ZW1haWw=', '\x62\x61\x73\x65\x36\x34').decode('ascii'), None)
setattr(ConfigDefaults, codecs.decode(
    b'cGFzc3dvcmQ=', '\x62\x61\x73\x65\x36\x34').decode('ascii'), None)
setattr(ConfigDefaults, codecs.decode(
    b'dG9rZW4=', '\x62\x61\x73\x65\x36\x34').decode('ascii'), None)
