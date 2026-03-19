import re
import traceback
from enum import Enum, auto
from inspect import ismethod
from functools import wraps

from tts_utilities.logger import create_logger
from tts_data_utils.invulnerable_data_manager.utilities import invulnerable, exec_invulnerable
from tts_papertrail.base import RichText

log = create_logger(__name__)

RE_HEXCOLOR = re.compile(r'^#?([0-9a-fA-F]{6})$')

class PALETTE(Enum):
    """
    Enumeration of standard color codes used for disposition output styling.
    """
    NO_COLOR = 'N/A'
    BLACK = '#000000'
    WHITE = '#FFFFFF'
    GREEN = '#68BC00'
    YELLOW = '#FCC400'
    ORANGE = '#FE9200'
    RED = '#FF6347'
    PURPLE = '#AD44AD'

class DISPO_FORMAT(Enum):
    """
    Enumeration of supported output formats for dispositions.
    """
    HTML = auto()
    TEXT = auto()
    EXCEL = auto()

class DISPO_SEVERITY(Enum):
    """
    Enumeration of disposition severity levels.

    Automatically configures default text and background colors based on the 
    severity name upon initialization.
    """
    NONE = auto()
    VERY_LOW = auto()
    LOW = auto()
    UNKNOWN = auto()
    MEDIUM = auto()
    HIGH = auto()
    VERY_HIGH = auto()
    CRITICAL = auto()

    def __new__(cls, value):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value):        
        """
        Initializes the severity level and assigns default colors.

        Args:
            value: The auto-generated value for the Enum member.
        """
        self.color = PALETTE.NO_COLOR
        self.bg_color = PALETTE.NO_COLOR
        if self.name == "NONE":
            self.color = PALETTE.GREEN
        if self.name == "VERY_LOW":
            self.color = PALETTE.GREEN
        elif self.name == "LOW":
            self.color = PALETTE.GREEN
        elif self.name == "MEDIUM":
            self.color = PALETTE.YELLOW
        elif self.name == "HIGH":
            self.color = PALETTE.RED
        elif self.name == "VERY_HIGH":
            self.color = PALETTE.RED
        elif self.name == "CRITICAL":
            self.color = PALETTE.RED
            self.bg_color = PALETTE.BLACK
        elif self.name == "UNKNOWN":
            self.color = PALETTE.PURPLE

def get_dispo_joiner(dispo_format):
    """
    Returns the appropriate string separator for joining multiple dispositions.

    Args:
        dispo_format (DISPO_FORMAT): The target output format.

    Returns:
        str: '<br>' for HTML, '\n' for TEXT/EXCEL.

    Raises:
        ValueError: If the dispo_format is not recognized.
    """
    if dispo_format == DISPO_FORMAT.HTML:
        return '<br>'
    elif dispo_format == DISPO_FORMAT.TEXT:
        return '\n'
    elif dispo_format == DISPO_FORMAT.EXCEL:
        return '\n'
    else:
        raise ValueError(f'Unhandled dispo format: {dispo_format}')

class Disposition:
    """
    Represents a single disposition outcome, including text content, severity, and styling.
    """
    def __init__(self, *args):
        self.headline = None
        self._color = None
        self.text = None
        self.severity = DISPO_SEVERITY.UNKNOWN
        self.__populated = False

        if len(args) > 0:
            self.set(*args)

    def populate(self, headline, text, severity, bg_color=None, color=None):
        """
        Populates the disposition with specific details.

        Args:
            headline (str): The short summary or title of the disposition (e.g., "Unexpected").
            text (str): The detailed explanation of the disposition.
            severity (DISPO_SEVERITY): The severity level associated with this finding.
            bg_color (str or PALETTE, optional): Background color override.
            color (str or PALETTE, optional): Text color override.

        Raises:
            ValueError: If the disposition has already been populated.
        """
        if self.populated:
            raise ValueError(f'Attempt to overwrite disposition, not allowed')
        self.headline = headline

        self.text = text

        self.severity = severity
        self.color = self.severity.color if color is None else color
        self.bg_color = self.severity.bg_color if bg_color is None else bg_color

        self.__populated = True

    @property
    def populated(self):
        """bool: True if the disposition has been set, False otherwise."""
        return self.__populated
    
    @classmethod
    def from_definition(cls, headline, text, severity, color=None, bg_color=None):
        """
        Factory method to create and populate a Disposition instance.

        Args:
            headline (str): The disposition headline.
            text (str): The disposition text.
            severity (DISPO_SEVERITY): The severity level.
            color (str or PALETTE, optional): Text color.
            bg_color (str or PALETTE, optional): Background color.

        Returns:
            Disposition: A populated Disposition object.
        """
        new_dispo = cls()
        new_dispo.populate(headline, text, severity, color=color, bg_color=bg_color)
        return new_dispo

    @property
    def color(self):
        """The text color for the disposition."""
        return self._color

    @color.setter
    def color(self, x):
        """
        Sets the text color, accepting Enum values, strings, or hex codes.

        Args:
            x (str or PALETTE): The color to set.

        Raises:
            TypeError: If input is not a string or PALETTE enum.
            ValueError: If the string is not a valid PALETTE name or hex code.
        """
        # If this is just a direct palette option, use that
        if isinstance(x, PALETTE):
            self._color = x
            return
        # Make sure we're working with a string
        elif not isinstance(x, str):
            raise TypeError(f'Cannot process color input of type {type(x)}')
        # See if it's a non-case-sensitive match for a palette option
        try:
            self._color = PALETTE[x.upper()]
            return
        except KeyError:
            pass
        # See if it's a hexcode
        match = RE_HEXCOLOR.match(x)
        if match:
            self._color = f'#{match.group(1)}'
            return
        # Don't know, die
        raise ValueError(f'Unrecognized color value "{x}')
        
    def format(self, dispo_format):
        """
        Formats the disposition string for the specified output format.

        Args:
            dispo_format (DISPO_FORMAT): The desired output format.

        Returns:
            str or List[RichText]: The formatted disposition.

        Raises:
            ValueError: If the format is not supported.
        """
        if dispo_format == DISPO_FORMAT.HTML:
            return self.format_html()
        elif dispo_format == DISPO_FORMAT.TEXT:
            return self.format_text()
        elif dispo_format == DISPO_FORMAT.EXCEL:
            return self.format_excel()
        else:
            raise ValueError(f'Unrecognized disposition format {dispo_format}')
        
    def format_html(self):
        """Formats the disposition as an HTML string with inline styles."""
        ftext = ''
        if self.color == PALETTE.NO_COLOR and self.bg_color == PALETTE.NO_COLOR:
            style_color = ''
        elif self.bg_color == PALETTE.NO_COLOR:
            color_string = self.color.value if isinstance(self.color, PALETTE) else self.color
            style_color = f' style="color:{color_string}"'
        elif self.color == PALETTE.NO_COLOR:            
            bg_color_string = self.bg_color.value if isinstance(self.bg_color, PALETTE) else self.bg_color
            style_color = f' style="background-color:{bg_color_string}"'
        else:
            color_string = self.color.value if isinstance(self.color, PALETTE) else self.color
            bg_color_string = self.bg_color.value if isinstance(self.bg_color, PALETTE) else self.bg_color
            style_color = f' style="color:{color_string};background-color:{bg_color_string}"'

        if self.headline is not None:
            ftext += f'<strong><span{style_color}>{self.headline}</span></strong>'
        if self.headline and self.text:
            ftext += ' - '
        if self.text:
            ftext += self.text
        return f'<p>{ftext}</p>'
    
    def format_text(self):
        """Formats the disposition as a plain text string."""
        ftext = ''
        if self.headline:
            ftext += self.headline
        if self.headline and self.text:
            ftext += ' - '
        if self.text:
            ftext += self.text
        return ftext

    def format_excel(self):
        """Formats the disposition as a list of RichText objects for Excel export."""
        rich_texts = []
        
        # Build headline with styling
        if self.headline:
            headline_color = self.color.value if isinstance(self.color, PALETTE) else self.color if self.color != PALETTE.NO_COLOR else None
            headline_bg_color = self.bg_color.value if isinstance(self.bg_color, PALETTE) else self.bg_color if self.bg_color != PALETTE.NO_COLOR else None
            
            rich_texts.append(RichText(
                text=self.headline,
                bold=True,
                color=headline_color,
                bg_color=headline_bg_color
            ))
        
        # Add separator if both headline and text exist
        if self.headline and self.text:
            rich_texts.append(RichText(' - '))
        
        # Add text content
        if self.text:
            rich_texts.append(RichText(self.text))
        
        return rich_texts

    def custom(self, headline, text):
        """
        Sets a custom disposition by mapping a headline string to a predefined severity method.

        Args:
            headline (str): One of 'Nominal', 'Expected', 'Benign', 'Ops Check', or 'Unexpected'.
            text (str): The disposition message.

        Raises:
            ValueError: If the headline is not one of the valid options.
        """
        if headline == 'Nominal':
            self.nominal(text)
        elif headline == 'Expected':
            self.expected(text)
        elif headline == 'Benign':
            self.benign(text)
        elif headline == 'Ops Check':
            self.ops_check(text)
        elif headline == 'Unexpected':
            self.unexpected(text)
        else:
            raise ValueError(f'{headline} is not a valid disposition headline.')

    def nominal(self, text):
        """Sets the disposition to Nominal (NONE severity)."""
        self.populate('Nominal', text, DISPO_SEVERITY.NONE)

    def expected(self, text):
        """Sets the disposition to Expected (LOW severity)."""
        self.populate('Expected', text, DISPO_SEVERITY.LOW)

    def benign(self, text):
        """Sets the disposition to Benign (LOW severity)."""
        self.populate('Benign', text, DISPO_SEVERITY.LOW)

    def ops_check(self, text):
        """Sets the disposition to Ops Check (UNKNOWN severity)."""
        self.populate('Ops Check', text, DISPO_SEVERITY.UNKNOWN)

    def unexpected(self, text):
        """Sets the disposition to Unexpected (HIGH severity)."""
        self.populate('Unexpected', text, DISPO_SEVERITY.HIGH)

    def critical(self, text):
        """Sets the disposition to Critical (VERY_HIGH severity)."""
        self.populate('Critical', text, DISPO_SEVERITY.VERY_HIGH, bg_color=PALETTE.BLACK)

# Default Disposition
SUGGESTED_DEFAULT_DISPO = Disposition.from_definition('Pending', 'No Auto-Disposition', DISPO_SEVERITY.MEDIUM)

def dispo_method(required, optional=None, batch=None, approved=True):
    """
    Decorator to register a method as an automated disposition logic unit.

    Handles retrieving necessary data containers from Dexter and passing them
    to the decorated method. Wraps execution in `invulnerable` to prevent
    single-failure crashes.

    Args:
        required (list[str]): List of data container names required for this disposition.
        optional (list[str], optional): List of optional data container names.
        batch (str, optional): The name of the specific batcher to use. If None, uses all input data.
        approved (bool, optional): Flag indicating if this disposition is approved for execution. 
                                   Defaults to True.

    Returns:
        function: The wrapped function ready for execution by Dexter.
    """
    def wrapper_outer(func):
        @invulnerable
        @wraps(func)
        def wrapper_inner(self):
            func_fullname = "{}.{}".format(self.__class__.__name__, func.__name__)
            
            if batch is None:
                batches = [self.dex.all_input_data]
            else:
                batcher = self.dex.get_batcher(batch)
                if batcher is None:
                    log.critical(f'Missing batch type {batch} for disposition {func_fullname}')
                    return
                batches = batcher.batches
                
            for data_batch in batches:
                data = []
                for name in required:
                    data.append(data_batch.get_data(name))
                missing_names = [_[0] for _ in zip(required, data) if _[1] is None]
                if len(missing_names) > 0:
                    missing_names_str = ' '.join([f'"{_}"' for _ in missing_names])
                    log.critical(f'Missing data {missing_names_str} in {data_batch.NAME} for disposition {func_fullname}')
                    return
                if optional:
                    for name in optional:
                        data.append(self.dex.get_data(name))

                func(self, *data)

        wrapper_inner._is_approved_disposition = approved
        return wrapper_inner
    return wrapper_outer

class Dispositioner:
    """
    Base class for defining groups of disposition logic.

    Subclasses should implement specific disposition methods decorated with 
    `@dispo_method`.
    """
    def __init__(self, dex):
        """
        Args:
            dex (Dexter): The parent Dexter manager instance.
        """
        self.dex = dex
        self.__post_init__()
        
    def __post_init__(self):
        """Hook for post-initialization logic in subclasses."""
        return

    def do_dispositions(self):
        """
        Executes all approved disposition methods defined in this class.

        Iterates over the class methods, checks for the `_is_approved_disposition`
        attribute set by the `@dispo_method` decorator, and runs them.
        """
        for _name in dir(self):
            _attr = getattr(self, _name)
            if ismethod(_attr) and hasattr(_attr, '_is_approved_disposition'):
                methodname = f'{self.__class__.__name__}.{_name}'
                if _attr._is_approved_disposition:
                    log.info(f'Running disposition {methodname}')
                    _attr()
                else:
                    log.info(f'Skipping unapproved disposition {methodname}')