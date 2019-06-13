"""
This file provides the ability through the ConfigReader class to read the configuration file used by tabReader.py and generate the default configuration file if needed.
Note: you can add comments throughout the config file by starting every comment line with a hashtag "#" as with Python. Comments can also be added at the end of config lines. Any characters after the "#" in a comment line will be ignored

author: Chami Lamelas
date: Summer 2019
"""

from exceptionsLibrary import TabConfigurationException
from pathlib import Path
from enum import Enum

"""
Enum that represents a configuration option. That is, each option is related to a number that serves as both its id and line number in the config. file. The configuration options are limited to this numbered set and are discussed below.

TIMING_SUPPLIED - line number and id of the option that signifes timing is supplied (that is there is a line above the strings with W's, H's, Q's. etc.)
GAPSIZE - line number and id of the option that signfies the output's sheet music gapsize (see Song doc. in typeLibrary.py)
TAB_SPACING - line number and id of the option that signifies the number of spaces in a tab in the user's text editor
HAS_EXTRA - line number and id of the option that signifies whether extra text exists in the file
PLAYING_LEGEND - line number and id of the option that holds a legend of other characters that may appear in string lines (e.g. h for hammer-ons, p for pull-offs, b for bends, etc.)
SIMPLE_STRING_LINES - line number and id of the option that signifies whether the string lines in the tab file are "simple". That is, lines with string information contain ONLY string information: no extra text on either end of the string data.
TIMING_SYMBOLS -
"""
class ConfigOptionID(Enum):
      TIMING_SUPPLIED = 0
      GAPSIZE = 1
      TAB_SPACING = 2
      HAS_EXTRA = 3
      PLAYING_LEGEND = 4
      SIMPLE_STRING_LINES = 5
      TIMING_SYMBOLS = 6

"""
This class is used to read the configuration file to be used by tabReader.py. The class stores the config. options' settings as attributes in addition to the list of lines read from the input config. file:

lines - a list of Strings that holds non-empty lines of the configuration file stripped of whitespace
settings - a list of the settings for each of the options specified in the above enum

WARNING: It is not advised to access the 'settings' attributedirectly. This is because there is no guarantee that they have actually been read by the reading methods and may return unexpected data values.
Therefore, it is best to use the their respective accessor/getter methods listed at the end of the class. These will check that they have actually been read and provide more appropriate output.
NOTE: calling these multiple times in client code that doesn't change the config. decreases performance as repeated unneccessary checks are being performed. To solve this, store the output of the getter methods that perform these checks in temp./local variables.

In addition, the class has several static variables used in identifying components of the configuration file:

CONFIG_FILENAME - the name of the config. file (for the purpose of making things easier for the user, it is not variable)
COMMENT - the character that signifies the beginning of a line comment in the config. file
SETTING_YES - signifies that a given config option should apply for this run of the program
SETTING_NO - signifies the opposite of aforementioned
defaultConfig - the text to be placed in the default config. file by 'buildDefaultConfigFile()'. Loaded on file import.
"""
class ConfigReader:

    CONFIG_FILENAME = "tabReader.config"
    COMMENT = "#"
    SETTING_YES = "true"
    SETTING_NO = "false"
    defaultConfig = ""

    """
    Constructs an empty ConfigReader. Use 'open()' to load the configuration file into this object.
    """
    def __init__(self):
        self.lines = list()
        self.settings = list() # initialize empty settings list to correspond to size specified by ConfigOptionID
        for i in range(0, len(ConfigOptionID)):
            self.settings.append(None)

    """
    Returns True if the OS can find a path to the config file, False if not.
    """
    def configFileFound():
        return Path(ConfigReader.CONFIG_FILENAME).is_file()

    """
    Checks if the config file has been loaded into this object so methods that retrieve config data can function properly.

    Raises TabConfigurationException if no data has been read from the config file.
    """
    def checkConfigFileLoaded(self):
        if not self.lines:
            raise TabConfigurationException(reason="config file not loaded properly. Can try opening again (use 'open()') or delete the file to reset it to default (uses 'buildDefaultConfigFile()').")

    """
    If the config file can be found, loads the files contents into self.lines. Otherwise, this method builds the configuration file and then re-runs the program.
    Infinite recursion is prevented by only trying to build the default configuration file again once. If that cannot be done (signified by a raised
    TabConfigurationException - see buildDefaultConfigFile() doc.), method just exits.

    Returns whether or not the config file was found. Thus, True indicates a config file could be found and was loaded. False indicates the default file was built and read.

    raises TabConfigurationException if there was an I/O error opening config file or if buildDefaultConfigFile() fails.
    """
    def open(self):
        if ConfigReader.configFileFound():
            try: # since a config file has been found, try to read it. Ignore lines marked as comments or that are empty. Wrap any IOErrors as TabConfigurationExceptions.
                with open(ConfigReader.CONFIG_FILENAME, "r") as configFile:
                    for line in configFile:
                        if not line.startswith(ConfigReader.COMMENT):
                            sLine = "".join(line.split()) # remove any separating whitespace
                            if len(sLine) > 0:
                                # strip off any end of line comments
                                idx = sLine.find(ConfigReader.COMMENT)
                                if (idx > 0):
                                    sLine = sLine[:-(len(sLine)-idx)]
                                self.lines.append(sLine)
                        # else: full line is a comment, ignore
                return True
            except IOError as i:
                raise TabConfigurationException(reason="I/O error opening config. file: " + i)
            except UnicodeDecodeError:
                raise TabConfigurationException(reason="Unicode character not allowed in text file. Mapping legend should have timing Unicode codes represented in the form outlined in the README")
        else: # since a config file could not be found, build the default one and call this method again.
            ConfigReader.buildDefaultConfigFile()
            self.open()
            return False

    """
    Returns the setting for an option specified by the user in the config file.

    params:
    option - a ConfigOptionID that identifies the config. option

    Raises TabConfigurationException if checkConfigFileLoaded() failed, the config. file is too small and the option cannot be found, the option id in the file was wrong, or there was no "=" in the option line
    """
    def readSetting(self, option: ConfigOptionID):
        self.checkConfigFileLoaded()
        if option.value >= len(self.lines):
            raise TabConfigurationException(reason="config. file too small. Config. option \"{0}\" cannot be found because its id ({1}) is greater than the number of lines in the file ({2}).".format(option.name, option.value, len(lines)))
        if not self.lines[option.value].startswith(option.name): # option's setting line must start with option's id
            raise TabConfigurationException(reason="improper ID. Must be {0}.".format(option.name), line=option.value+1)
        idx = self.lines[option.value].find("=")
        if idx != len(option.name): # option id and setting must be separated by an "="
            raise TabConfigurationException(reason="missing \"=\".", line=option.value+1)
        return self.lines[option.value][idx+1:] # setting is whatever follows the "="

    """
    Reads the True/False setting for the timing supplied option.

    Raises TabConfigurationException if readSetting() failed on the config file for the timing supplied option or if the setting found in the config file for this option could not
    be recognized.
    """
    def readTiming(self):
        setting = self.readSetting(ConfigOptionID.TIMING_SUPPLIED)
        if setting == ConfigReader.SETTING_YES:
            self.settings[ConfigOptionID.TIMING_SUPPLIED.value] = True
        elif setting == ConfigReader.SETTING_NO:
            self.settings[ConfigOptionID.TIMING_SUPPLIED.value] = False
        else: # only 2 allowed settings are True or False
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be {2} or {3}".format(setting, ConfigOptionID.TIMING_SUPPLIED.name, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=ConfigOptionID.TIMING_SUPPLIED.value+1)

    """
    Reads the integer gapsize to be placed between Slices in the resulting Song generated by tabReader.py.

    Raises TabConfigurationException if readSetting() failed on the config file for the gapsize option or if the setting found in the config file was not a non-negative integer
    """
    def readGapsize(self):
        setting = self.readSetting(ConfigOptionID.GAPSIZE)
        try:
            intSetting = int(setting)
            if intSetting < 0:
                raise ValueError()
        # 2 sources of ValueErrors in try-statement: (1) setting is not an int, raised by int(). (2) ValueError manually raised by gapSize < 0. One is manually raised because both
        # possible problems with the gapSize both fall under a "value" problem. These can be easily grouped into the same error message.
        except ValueError:
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be a non-negative integer.".format(setting, ConfigOptionID.GAPSIZE.name), line=ConfigOptionID.GAPSIZE.value+1)
        self.settings[ConfigOptionID.GAPSIZE.value] = intSetting

    """
    Reads the integer tab spacing of the editor used to create the input text file. By default the spacing is 8, but modern text editors allow for the number of spaces in a tab character to be reduced.
    This provides a way for the user to specify that.

    Raises TabConfigurationException if readSetting() failed on the config file for the tab spacing option or if the setting found in the config file was not a non-negative integer
    """
    def readTabSpacing(self):
        setting = self.readSetting(ConfigOptionID.TAB_SPACING)
        try:
            intSetting = int(setting)
            if intSetting < 0:
                raise ValueError()
        except ValueError: # see note on ValueError handling in getGapsize() above
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be a non-negative integer.".format(setting, ConfigOptionID.TAB_SPACING.name), line=ConfigOptionID.TAB_SPACING.value+1)
        else:
            self.settings[ConfigOptionID.TAB_SPACING.value] = intSetting

    """
    Reads True/False value of whether user has specified that the input text file has extra text. That is, notes or identifications of verses, etc. If the user removes all extra text that is all
    non string and timing lines from the input file, the performance of loadLinesIntoLists() in tabReader.py increases.

    Raises TabConfigurationException if readSetting() failed on the config file for the has extra option or if the setting found in the config file could not be recognized.
    """
    def readHasExtra(self):
        setting = self.readSetting(ConfigOptionID.HAS_EXTRA)
        if setting == ConfigReader.SETTING_YES:
            self.settings[ConfigOptionID.HAS_EXTRA.value] = True
        elif setting == ConfigReader.SETTING_NO:
            self.settings[ConfigOptionID.HAS_EXTRA.value] = False
        else: # only 2 allowed settings are True or False
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be {2} or {3}".format(setting, ConfigOptionID.HAS_EXTRA.name, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=ConfigOptionID.HAS_EXTRA.value+1)

    """
    Reads the legend as described in the ConfigReader attributes doc. as a set of characters.

    Raises TabConfigurationException if readSetting() failed on the config file for the legend option or if the legend contains a whitespace character or digit (0-9).
    """
    def readPlayingLegend(self):
        setting = self.readSetting(ConfigOptionID.PLAYING_LEGEND) # legend option must be on line 4
        leg = set()
        for ch in setting:
            if ch.isdigit() or ch.isspace():
                raise TabConfigurationException(reason="illegal legend value \"{0}\". Cannot be a whitespace character or digit (0-9)".format(ch), line=ConfigOptionID.PLAYING_LEGEND.value+1)
            else:
                leg.add(ch)
        self.settings[ConfigOptionID.PLAYING_LEGEND.value] = leg

    """
    Reads the simple string lines config. option.

    Raises TabConfigurationException if readSetting() fails or the setting is neither ConfigReader.SETTING_YES nor ConfigReader.SETTING_NO.
    """
    def readSimpleString(self):
        setting = self.readSetting(ConfigOptionID.SIMPLE_STRING_LINES)
        if setting == ConfigReader.SETTING_YES:
            self.settings[ConfigOptionID.SIMPLE_STRING_LINES.value] = True
        elif setting == ConfigReader.SETTING_NO:
            self.settings[ConfigOptionID.SIMPLE_STRING_LINES.value] = False
        else:
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be {2} or {3}".format(setting, ConfigOptionID.SIMPLE_STRING_LINES.name, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO), line=ConfigOptionID.SIMPLE_STRING_LINES.value+1)

    """
    Reads the timing symbols list config. option.

    Raises TabConfigurationException if readSetting() fails or the setting is invalid.
    """
    def readTimingSymbolsList(self):
        setting = self.readSetting(ConfigOptionID.TIMING_SYMBOLS)
        if len(setting) != 10 or len(set(setting)) < 10:
            raise TabConfigurationException(reason="setting \"{0}\" for option \"{1}\" not recognized. Must be made up of exactly 10 unique characters", line=ConfigOptionID.TIMING_SYMBOLS.value+1)
        self.settings[ConfigOptionID.TIMING_SYMBOLS.value] = setting

    """
    Builds the default config file. WARNING: calling this method will overwrite any pre-existing file with the same path as this program's config file.

    Raises TabConfigurationException if the file could not be created
    """
    def buildDefaultConfigFile():
        try: # try to write the default configuration to the config file, wrap any IOError that occurs as a TabConfigurationException
            with open(ConfigReader.CONFIG_FILENAME, "w+") as configFile:
                configFile.write(ConfigReader.defaultConfig)
        except IOError as i:
            raise TabConfigurationException(reason="configuration file could not be created; an I/O Error occurred: " + str(i))

    """
    Checks if the reading operation for a given option was successful based on its current setting.

    params:
    option - a ConfigOptionID that identifies an option to check

    Raises TabConfigurationException as explained above.
    """
    def checkIfOptionRead(self, id: ConfigOptionID):
        if self.settings[id.value] is None:
            raise TabConfigurationException(reason="configuration option \"{0}\" has not been read. Please use the appropriate reading method.".format(id.name), line=id.value+1)

    """
    Checks that the timing supplied option has been read before returning its value to the user. Use instead of directly accessing 'self.settings' for more suitable output.

    Raises TabConfigurationException if 'checkIfOptionRead()' fails for this option.
    """
    def isTimingSupplied(self):
        self.checkIfOptionRead(ConfigOptionID.TIMING_SUPPLIED)
        return self.settings[ConfigOptionID.TIMING_SUPPLIED.value]

    """
    Checks that the gapsize option has been read before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Raises TabConfigurationException if 'checkIfOptionRead()' fails for this option.
    """
    def getGapsize(self):
        self.checkIfOptionRead(ConfigOptionID.GAPSIZE)
        return self.settings[ConfigOptionID.GAPSIZE.value]

    """
    Checks that the tab spacing option has been read before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Raises TabConfigurationException if 'checkIfOptionRead()' fails for this option.
    """
    def getTabSpacing(self):
        self.checkIfOptionRead(ConfigOptionID.TAB_SPACING)
        return self.settings[ConfigOptionID.TAB_SPACING.value]

    """
    Checks that (i) the extra text present option has been read and that (ii) there is no conflict with the setting for 'ConfigOptionID.SIMPLE_STRING_LINES' before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Note: for (ii) to be checked, the setting for 'ConfigOptionID.SIMPLE_STRING_LINES' must have also been read prior to calling this method.

    Raises TabConfigurationException if:
    - 'checkIfOptionRead()' fails for this option
    - 'checkIfOptionRead()' fails for 'ConfigOptionID.HAS_EXTRA'
    - the user has specified there is no extra text (the setting of 'ConfigOptionID.HAS_EXTRA' is 'ConfigReader.SETTING_NO') but there are non-simple string lines (the setting of 'ConfigOptionID.SIMPLE_STRING_LINES' is 'ConfigReader.SETTING_YES'). If there are non-simple string lines, both settings must be false.
    """
    def isExtraTextPresent(self):
        self.checkIfOptionRead(ConfigOptionID.HAS_EXTRA)
        self.checkIfOptionRead(ConfigOptionID.SIMPLE_STRING_LINES)
        if not self.settings[ConfigOptionID.HAS_EXTRA.value] and not self.settings[ConfigOptionID.SIMPLE_STRING_LINES.value]:
            raise TabConfigurationException(reason="conflicting config. settings: \"{1}={3}\" and \"{0}={3}\". If {0}={3}, then {1}={2}".format(ConfigOptionID.HAS_EXTRA.name, ConfigOptionID.SIMPLE_STRING_LINES.name, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO))
        return self.settings[ConfigOptionID.HAS_EXTRA.value]

    """
    Checks that the playing legend has been read before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Raises TabConfigurationException if 'checkIfOptionRead()' fails for this option.
    """
    def getPlayingLegend(self):
        self.checkIfOptionRead(ConfigOptionID.PLAYING_LEGEND)
        return self.settings[ConfigOptionID.PLAYING_LEGEND.value]

    """
    Checks that (i) the simple string lines option has been read and that (ii) there is no conflict with the setting for 'ConfigOptionID.HAS_EXTRA' before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Note: for (ii) to be checked, the setting for 'ConfigOptionID.HAS_EXTRA' must have also been read prior to calling this method.

    Raises TabConfigurationException if:
    - 'checkIfOptionRead()' fails for this option
    - 'checkIfOptionRead()' fails for 'ConfigOptionID.HAS_EXTRA'
    - the user has specified there is no extra text (the setting of 'ConfigOptionID.HAS_EXTRA' is 'ConfigReader.SETTING_NO') but there are non-simple string lines (the setting of 'ConfigOptionID.SIMPLE_STRING_LINES' is 'ConfigReader.SETTING_YES'). If there are non-simple string lines, both settings must be false.
    """
    def hasSimpleStringLines(self):
        self.checkIfOptionRead(ConfigOptionID.SIMPLE_STRING_LINES)
        self.checkIfOptionRead(ConfigOptionID.HAS_EXTRA)
        if not self.settings[ConfigOptionID.HAS_EXTRA.value] and not self.settings[ConfigOptionID.SIMPLE_STRING_LINES.value]:
            raise TabConfigurationException(reason="conflicting config. settings: \"{1}={3}\" and \"{0}={3}\". If {0}={3}, then {1}={2}".format(ConfigOptionID.HAS_EXTRA.name, ConfigOptionID.SIMPLE_STRING_LINES.name, ConfigReader.SETTING_YES, ConfigReader.SETTING_NO))
        return self.settings[ConfigOptionID.SIMPLE_STRING_LINES.value]

    """
    Checks that the timing symbol list has been read before returning its value to the user. Use instead of directly accessing 'self.settings'.

    Raises TabConfigurationException if 'checkIfOptionRead()' fails for this option
    """
    def getTimingSymbolsList(self):
        self.checkIfOptionRead(ConfigOptionID.TIMING_SYMBOLS)
        return self.settings[ConfigOptionID.TIMING_SYMBOLS.value]

"""
Script to load default config. file text ('ConfigReader.defaultConfig')
"""
defaultValues = list() # create an empty list to hold default values
for i in range(0, len(ConfigOptionID)):
    defaultValues.append(None)

# associate with each config. option a default value by placing it in the index equal to the value of the ConfigOptionID corresponding to it
defaultValues[ConfigOptionID.TIMING_SUPPLIED.value] = ConfigReader.SETTING_NO
defaultValues[ConfigOptionID.GAPSIZE.value] = 3
defaultValues[ConfigOptionID.TAB_SPACING.value] = 8
defaultValues[ConfigOptionID.HAS_EXTRA.value] = ConfigReader.SETTING_YES
defaultValues[ConfigOptionID.PLAYING_LEGEND.value] = ""
defaultValues[ConfigOptionID.SIMPLE_STRING_LINES.value] = ConfigReader.SETTING_YES
defaultValues[ConfigOptionID.TIMING_SYMBOLS.value] = "+.WHQESTFO"

# place it into the default file text static variable
ConfigReader.defaultConfig = "# This is the configuration file for the tab reader program. \n# You can add line comments in the configuration file similarly to how it is done in Python: \n# (1) Placing a hashtag \"#\" at the beginning of each comment line. \n# (2) Placing a \"#\" at the end of configuration lines. The program will ignore any text following the hashtag."
for id in ConfigOptionID:
    ConfigReader.defaultConfig += "\n" + id.name + "=" + str(defaultValues[id.value])
