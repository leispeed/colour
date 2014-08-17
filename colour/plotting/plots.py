#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Plots
=====

Defines plotting objects for various dataset:

-   :func:`figure_size`
-   :func:`aspect`
-   :func:`bounding_box`
-   :func:`display`
-   :func:`colour_parameter`
-   :func:`colour_parameters_plot`
-   :func:`single_colour_plot`
-   :func:`multi_colour_plot`
-   :func:`colour_checker_plot`
-   :func:`single_spd_plot`
-   :func:`multi_spd_plot`
-   :func:`single_cmfs_plot`
-   :func:`multi_cmfs_plot`
-   :func:`single_illuminant_relative_spd_plot`
-   :func:`multi_illuminants_relative_spd_plot`
-   :func:`visible_spectrum_plot`
-   :func:`CIE_1931_chromaticity_diagram_plot`
-   :func:`colourspaces_CIE_1931_chromaticity_diagram_plot`
-   :func:`planckian_locus_CIE_1931_chromaticity_diagram_plot`
-   :func:`CIE_1960_UCS_chromaticity_diagram_plot`
-   :func:`planckian_locus_CIE_1960_UCS_chromaticity_diagram_plot`
-   :func:`CIE_1976_UCS_chromaticity_diagram_plot`
-   :func:`single_munsell_value_function_plot`
-   :func:`multi_munsell_value_function_plot`
-   :func:`single_lightness_function_plot`
-   :func:`multi_lightness_function_plot`
-   :func:`single_transfer_function_plot`
-   :func:`multi_transfer_function_plot`
-   :func:`blackbody_spectral_radiance_plot`
-   :func:`blackbody_colours_plot`
-   :func:`colour_rendering_index_bars_plot`
"""

import bisect
import functools
import itertools
import os
import random
from collections import namedtuple

import matplotlib
import matplotlib.image
import matplotlib.path
import matplotlib.pyplot
import matplotlib.ticker
import numpy as np
import pylab

from colour.algebra import normalise
from colour.colorimetry import (
    CMFS,
    ILLUMINANTS,
    ILLUMINANTS_RELATIVE_SPDS,
    LIGHTNESS_FUNCTIONS,
    spectral_to_XYZ,
    wavelength_to_XYZ,
    blackbody_spectral_power_distribution)
from colour.characterization import COLOURCHECKERS
from colour.models import POINTER_GAMUT_DATA, RGB_COLOURSPACES
from colour.models import (
    UCS_uv_to_xy,
    XYZ_to_UCS,
    XYZ_to_xy,
    UCS_to_uv,
    xy_to_XYZ,
    xyY_to_XYZ,
    XYZ_to_Luv,
    Luv_to_uv,
    Luv_uv_to_xy,
    XYZ_to_sRGB)
from colour.notation import MUNSELL_VALUE_FUNCTIONS
from colour.quality import get_colour_rendering_index
from colour.temperature import CCT_to_uv
from colour.utilities import Structure


__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2014 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['RESOURCES_DIRECTORY',
           'DEFAULT_FIGURE_SIZE',
           'DEFAULT_COLOUR_CYCLE',
           'COLOUR_PARAMETER',
           'figure_size',
           'aspect',
           'bounding_box',
           'display',
           'colour_parameter',
           'colour_parameters_plot',
           'single_colour_plot',
           'multi_colour_plot',
           'colour_checker_plot',
           'single_spd_plot',
           'multi_spd_plot',
           'single_cmfs_plot',
           'multi_cmfs_plot',
           'single_illuminant_relative_spd_plot',
           'multi_illuminants_relative_spd_plot',
           'visible_spectrum_plot',
           'CIE_1931_chromaticity_diagram_colours_plot',
           'CIE_1931_chromaticity_diagram_plot',
           'colourspaces_CIE_1931_chromaticity_diagram_plot',
           'planckian_locus_CIE_1931_chromaticity_diagram_plot',
           'CIE_1960_UCS_chromaticity_diagram_colours_plot',
           'CIE_1960_UCS_chromaticity_diagram_plot',
           'planckian_locus_CIE_1960_UCS_chromaticity_diagram_plot',
           'CIE_1976_UCS_chromaticity_diagram_colours_plot',
           'CIE_1976_UCS_chromaticity_diagram_plot',
           'single_munsell_value_function_plot',
           'multi_munsell_value_function_plot',
           'single_lightness_function_plot',
           'multi_lightness_function_plot',
           'single_transfer_function_plot',
           'multi_transfer_function_plot',
           'blackbody_spectral_radiance_plot',
           'blackbody_colours_plot',
           'colour_rendering_index_bars_plot']

RESOURCES_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   'resources')
"""
Resources directory.

RESOURCES_DIRECTORY : unicode
"""

DEFAULT_FIGURE_SIZE = 14, 7
"""
Default plots figure size.

DEFAULT_FIGURE_SIZE : tuple
"""

DEFAULT_COLOUR_CYCLE = ('r', 'g', 'b', 'c', 'm', 'y', 'k')

COLOUR_PARAMETER = namedtuple('ColourParameter',
                              ('name', 'RGB', 'x', 'y0', 'y1'))

# Defining default figure size.
pylab.rcParams['figure.figsize'] = DEFAULT_FIGURE_SIZE

# Defining an alternative font that can display scientific notations.
matplotlib.rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})


def _get_cmfs(cmfs):
    """
    Returns the colour matching functions with given name.

    Parameters
    ----------
    cmfs : Unicode
        Colour matching functions name.

    Returns
    -------
    RGB_ColourMatchingFunctions or XYZ_ColourMatchingFunctions
        Colour matching functions.
    """

    cmfs, name = CMFS.get(cmfs), cmfs
    if cmfs is None:
        raise KeyError(
            '"{0}" not found in factory colour matching functions: "{1}".'.format(
                name, sorted(cmfs.CMFS.keys())))
    return cmfs


def _get_illuminant(illuminant):
    """
    Returns the illuminant with given name.

    Parameters
    ----------
    illuminant : Unicode
        Illuminant name.

    Returns
    -------
    SpectralPowerDistribution
        Illuminant.
    """

    illuminant, name = ILLUMINANTS_RELATIVE_SPDS.get(illuminant), illuminant
    if illuminant is None:
        raise KeyError(
            '"{0}" not found in factory illuminants: "{1}".'.format(
                name, sorted(ILLUMINANTS_RELATIVE_SPDS.keys())))

    return illuminant


def _get_RGB_colourspace(colourspace):
    """
    Returns the *RGB* colourspace with given name.

    Parameters
    ----------
    colourspace : Unicode
        *RGB* Colourspace name.

    Returns
    -------
    RGB_Colourspace
        *RGB* Colourspace.
    """

    colourspace, name = RGB_COLOURSPACES.get(colourspace), colourspace
    if colourspace is None:
        raise KeyError(
            '"{0}" colourspace not found in factory colourspaces: "{1}".'.format(
                name, sorted(RGB_COLOURSPACES.keys())))

    return colourspace


def _get_colour_cycle(colour_map='hsv', count=len(DEFAULT_COLOUR_CYCLE)):
    """
    Returns a colour cycle iterator using given colour map.

    Parameters
    ----------
    colour_map : unicode, optional
        Matplotlib colour map.
    count : int, optional
        Cycle length.

    Returns
    -------
    cycle
        Colour cycle iterator.
    """

    if colour_map is None:
        colour_cycle = DEFAULT_COLOUR_CYCLE
    else:
        colour_cycle = getattr(matplotlib.pyplot.cm,
                               colour_map)(np.linspace(0., 1., count))

    return itertools.cycle(colour_cycle)


def figure_size(size=DEFAULT_FIGURE_SIZE):
    """
    Sets figures sizes.

    Parameters
    ----------
    size : tuple, optional
        Figure size.

    Returns
    -------
    object
        Object.
    """

    def figure_size_decorator(object):
        """
        Sets figures sizes.

        Parameters
        ----------
        object : object
            Object to decorate.

        Returns
        -------
        object
            Object.
        """

        @functools.wraps(object)
        def figure_size_wrapper(*args, **kwargs):
            """
            Sets figures sizes.

            Parameters
            ----------
            \*args : \*
                Arguments.
            \*\*kwargs : \*\*
                Keywords arguments.

            Returns
            -------
            object
                Object.
            """

            pylab.rcParams['figure.figsize'] = kwargs.get(
                'figure_size') if kwargs.get(
                'figure_size') is not None else size

            try:
                return object(*args, **kwargs)
            finally:
                pylab.rcParams['figure.figsize'] = DEFAULT_FIGURE_SIZE

        return figure_size_wrapper

    return figure_size_decorator


def aspect(**kwargs):
    """
    Sets the figure aspect.

    Parameters
    ----------
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.
    """

    settings = Structure(
        **{'title': None,
           'x_label': None,
           'y_label': None,
           'legend': False,
           'legend_location': 'upper right',
           'x_ticker': False,
           'y_ticker': False,
           'x_ticker_locator': matplotlib.ticker.AutoMinorLocator(2),
           'y_ticker_locator': matplotlib.ticker.AutoMinorLocator(2),
           'no_ticks': False,
           'no_x_ticks': False,
           'no_y_ticks': False,
           'grid': False,
           'axis_grid': 'both',
           'x_axis_line': False,
           'y_axis_line': False,
           'aspect': None})
    settings.update(kwargs)

    settings.title and pylab.title(settings.title)
    settings.x_label and pylab.xlabel(settings.x_label)
    settings.y_label and pylab.ylabel(settings.y_label)
    settings.legend and pylab.legend(loc=settings.legend_location)
    settings.x_ticker and matplotlib.pyplot.gca().xaxis.set_minor_locator(
        settings.x_ticker_locator)
    settings.y_ticker and matplotlib.pyplot.gca().yaxis.set_minor_locator(
        settings.y_ticker_locator)
    if settings.no_ticks:
        matplotlib.pyplot.gca().set_xticks([])
        matplotlib.pyplot.gca().set_yticks([])
    if settings.no_x_ticks:
        matplotlib.pyplot.gca().set_xticks([])
    if settings.no_y_ticks:
        matplotlib.pyplot.gca().set_yticks([])
    settings.grid and pylab.grid(which=settings.axis_grid)
    settings.x_axis_line and pylab.axvline(0, color='black', linestyle='--')
    settings.y_axis_line and pylab.axhline(0, color='black', linestyle='--')
    settings.aspect and matplotlib.pyplot.axes().set_aspect(settings.aspect)

    return True


def bounding_box(**kwargs):
    """
    Sets the plot bounding box.

    Parameters
    ----------
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.
    """

    settings = Structure(
        **{'bounding_box': None,
           'x_tighten': False,
           'y_tighten': False,
           'limits': [0., 1., 0., 1.],
           'margins': [0., 0., 0., 0.]})
    settings.update(kwargs)

    if settings.bounding_box is None:
        x_limit_min, x_limit_max, y_limit_min, y_limit_max = settings.limits
        x_margin_min, x_margin_max, y_margin_min, y_margin_max = settings.margins
        settings.x_tighten and pylab.xlim(x_limit_min + x_margin_min,
                                          x_limit_max + x_margin_max)
        settings.y_tighten and pylab.ylim(y_limit_min + y_margin_min,
                                          y_limit_max + y_margin_max)
    else:
        pylab.xlim(settings.bounding_box[0], settings.bounding_box[1])
        pylab.ylim(settings.bounding_box[2], settings.bounding_box[3])

    return True


def display(**kwargs):
    """
    Sets the figure display.

    Parameters
    ----------
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.
    """

    settings = Structure(
        **{'standalone': True,
           'filename': None})
    settings.update(kwargs)

    if settings.standalone:
        if settings.filename is not None:
            pylab.savefig(**kwargs)
        else:
            pylab.show()
        pylab.close()

    return True


def colour_parameter(name=None, RGB=None, x=None, y0=None, y1=None):
    """
    Defines a factory for
    :attr:`colour.plotting.plots.COLOUR_PARAMETER` attribute.

    Parameters
    ----------
    name : unicode, optional
        Colour name.
    RGB : array_like, optional
        RGB Colour.
    x : float, optional
        X data.
    y0 : float, optional
        Y0 data.
    y1 : float, optional
        Y1 data.

    Returns
    -------
    ColourParameter
        ColourParameter.
    """

    return COLOUR_PARAMETER(name, RGB, x, y0, y1)


def colour_parameters_plot(colour_parameters,
                           y0_plot=True,
                           y1_plot=True,
                           **kwargs):
    """
    Plots given colour colour_parameters.

    Parameters
    ----------
    colour_parameters : list
        ColourParameter sequence.
    y0_plot : bool, optional
        Plot y0 line.
    y1_plot : bool, optional
        Plot y1 line.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> cp1 = colour_parameter(x=390, RGB=[0.03009021, 0., 0.12300545])
    >>> cp2 = colour_parameter(x=391, RGB=[0.03434063, 0., 0.13328537], y0=0, y1=0.25)
    >>> cp3 = colour_parameter(x=392, RGB=[0.03826312, 0., 0.14276247], y0=0, y1=0.35)
    >>> cp4 = colour_parameter(x=393, RGB=[0.04191844, 0., 0.15158707], y0=0, y1=0.05)
    >>> cp5 = colour_parameter(x=394, RGB=[0.04535085, 0., 0.15986838], y0=0, y1=-.25)
    >>> colour.plotting.colour_parameters_plot([cp1, cp2, cp3, cp3, cp4, cp5])
    True
    """

    for i in range(len(colour_parameters) - 1):
        x0 = colour_parameters[i].x
        x01 = colour_parameters[i + 1].x
        y0 = (0.
              if colour_parameters[i].y0 is None else
              colour_parameters[i].y0)
        y1 = (1.
              if colour_parameters[i].y1 is None else
              colour_parameters[i].y1)
        y01 = (0.
               if colour_parameters[i].y0 is None else
               colour_parameters[i + 1].y0)
        y11 = (1.
               if colour_parameters[i].y1 is None else
               colour_parameters[i + 1].y1)

        x_polygon = [x0, x01, x01, x0]
        y_polygon = [y0, y01, y11, y1]
        pylab.fill(x_polygon,
                   y_polygon,
                   color=colour_parameters[i].RGB,
                   edgecolor=colour_parameters[i].RGB)

    if all([x.y0 is not None for x in colour_parameters]):
        y0_plot and pylab.plot([x.x for x in colour_parameters],
                               [x.y0 for x in colour_parameters],
                               color='black',
                               linewidth=2.)

    if all([x.y1 is not None for x in colour_parameters]):
        y1_plot and pylab.plot([x.x for x in colour_parameters],
                               [x.y1 for x in colour_parameters],
                               color='black',
                               linewidth=2.)

    y_limit_min0 = min(
        [0. if x.y0 is None else x.y0 for x in colour_parameters])
    y_limit_max0 = max(
        [1. if x.y0 is None else x.y0 for x in colour_parameters])
    y_limit_min1 = min(
        [0. if x.y1 is None else x.y1 for x in colour_parameters])
    y_limit_max1 = max(
        [1. if x.y1 is None else x.y1 for x in colour_parameters])

    settings = {'x_label': 'Parameter',
                'y_label': 'Colour',
                'limits': [min([0. if x.x is None else x.x
                                for x in colour_parameters]),
                           max([1. if x.x is None else x.x
                                for x in colour_parameters]),
                           y_limit_min0,
                           y_limit_max1]}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_colour_plot(colour_parameter, **kwargs):
    """
    Plots given colour.

    Parameters
    ----------
    colour_parameter : ColourParameter
        ColourParameter.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> RGB = (0.32315746, 0.32983556, 0.33640183)
    >>> colour.plotting.single_colour_plot(colour_parameter(RGB))
    True
    """

    return multi_colour_plot([colour_parameter], **kwargs)


def multi_colour_plot(colour_parameters,
                      width=1.,
                      height=1.,
                      spacing=0.,
                      across=3,
                      text_display=True,
                      text_size='large',
                      text_offset=0.075,
                      **kwargs):
    """
    Plots given colours.

    Parameters
    ----------
    colour_parameters : list
        ColourParameter sequence.
    width : float, optional
        Colour polygon width.
    height : float, optional
        Colour polygon height.
    spacing : float, optional
        Colour polygons spacing.
    across : int, optional
        Colour polygons count per row.
    text_display : bool, optional
        Display colour text.
    text_size : float, optional
        Colour text size.
    text_offset : float, optional
        Colour text offset.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> cp1 = colour_parameter(RGB=(0.45293517, 0.31732158, 0.26414773))
    >>> cp2 = colour_parameter(RGB=(0.77875824, 0.5772645,  0.50453169)
    >>> colour.plotting.multi_colour_plot([cp1, cp2])
    True
    """

    offsetX = offsetY = 0
    x_limit_min, x_limit_max, y_limit_min, y_limit_max = 0, width, 0, height
    for i, colour_parameter in enumerate(colour_parameters):
        if i % across == 0 and i != 0:
            offsetX = 0
            offsetY -= height + spacing

        x0 = offsetX
        x1 = offsetX + width
        y0 = offsetY
        y1 = offsetY + height

        x_polygon = [x0, x1, x1, x0]
        y_polygon = [y0, y0, y1, y1]
        pylab.fill(x_polygon, y_polygon, color=colour_parameters[i].RGB)
        if colour_parameter.name is not None and text_display:
            pylab.text(x0 + text_offset, y0 + text_offset,
                       colour_parameter.name, clip_on=True, size=text_size)

        offsetX += width + spacing

    x_limit_max = min(len(colour_parameters), across)
    x_limit_max = x_limit_max * width + x_limit_max * spacing - spacing
    y_limit_min = offsetY

    settings = {'x_tighten': True,
                'y_tighten': True,
                'no_ticks': True,
                'limits': [x_limit_min, x_limit_max, y_limit_min, y_limit_max],
                'aspect': 'equal'}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def colour_checker_plot(colour_checker='ColorChecker 2005', **kwargs):
    """
    Plots given colour checker.

    Parameters
    ----------
    colour_checker : unicode, optional
        Color checker name.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.colour_checker_plot()
    True
    """

    colour_checker, name = COLOURCHECKERS.get(colour_checker), colour_checker
    if colour_checker is None:
        raise KeyError(
            'Colour checker "{0}" not found in colour checkers: "{1}".'.format(
                name, sorted(COLOURCHECKERS.keys())))

    _, data, illuminant = colour_checker
    colour_parameters = []
    for index, label, x, y, Y in data:
        XYZ = xyY_to_XYZ((x, y, Y))
        RGB = XYZ_to_sRGB(XYZ, illuminant)

        colour_parameters.append(
            colour_parameter(label.title(), np.clip(np.ravel(RGB), 0, 1)))

    background_colour = '0.1'
    matplotlib.pyplot.gca().patch.set_facecolor(background_colour)

    width = height = 1.0
    spacing = 0.25
    across = 6

    settings = {'standalone': False,
                'width': width,
                'height': height,
                'spacing': spacing,
                'across': across,
                'margins': [-0.125, 0.125, -0.5, 0.125]}
    settings.update(kwargs)

    multi_colour_plot(colour_parameters, **settings)

    text_x = width * (across / 2) + (across * (spacing / 2)) - spacing / 2
    text_y = -(len(colour_parameters) / across + spacing / 2)

    pylab.text(text_x,
               text_y,
               '{0} - {1} - Colour Rendition Chart'.format(
                   name, RGB_COLOURSPACES.get('sRGB').name),
               color='0.95',
               clip_on=True,
               ha='center')

    settings.update({'title': name,
                     'facecolor': background_colour,
                     'edgecolor': None,
                     'standalone': True})

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_spd_plot(spd, cmfs='CIE 1931 2 Degree Standard Observer', **kwargs):
    """
    Plots given spectral power distribution.

    Parameters
    ----------
    spd : SpectralPowerDistribution, optional
        Spectral power distribution to plot.
    cmfs : unicode
        Standard observer colour matching functions used for spectrum creation.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> data = {400: 0.0641, 420: 0.0645, 440: 0.0562}
    >>> spd = colour.SpectralPowerDistribution('Custom', data)
    >>> colour.plotting.single_spd_plot(spd)
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    start, end, steps = cmfs.shape
    spd = spd.clone().interpolate(start, end, steps)
    wavelengths = np.arange(start, end + steps, steps)

    colours = []
    y1 = []

    for wavelength, value in spd:
        XYZ = wavelength_to_XYZ(wavelength, cmfs)
        colours.append(XYZ_to_sRGB(XYZ))
        y1.append(value)

    colours = np.array([np.ravel(x) for x in colours])
    colours *= 1. / np.max(colours)
    colours = np.clip(colours, 0, 1)

    settings = {'title': '"{0}" - {1}'.format(spd.name, cmfs.name),
                'x_label': u'Wavelength λ (nm)',
                'y_label': 'Spectral Power Distribution',
                'x_tighten': True,
                'x_ticker': True,
                'y_ticker': True}

    settings.update(kwargs)
    return colour_parameters_plot(
        [colour_parameter(x=x[0], y1=x[1], RGB=x[2])
         for x in tuple(zip(wavelengths, y1, colours))],
        **settings)


def multi_spd_plot(spds,
                   cmfs='CIE 1931 2 Degree Standard Observer',
                   use_spds_colours=False,
                   normalise_spds_colours=False,
                   **kwargs):
    """
    Plots given spectral power distributions.

    Parameters
    ----------
    spds : list, optional
        Spectral power distributions to plot.
    cmfs : unicode, optional
        Standard observer colour matching functions used for spectrum creation.
    use_spds_colours : bool, optional
        Use spectral power distributions colours.
    normalise_spds_colours : bool
        Should spectral power distributions colours normalised.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> data1 = {400: 0.0641, 420: 0.0645, 440: 0.0562}
    >>> data2 = {400: 0.134, 420: 0.789, 440: 1.289}
    >>> spd1 = colour.SpectralPowerDistribution('Custom1', data1)
    >>> spd2 = colour.SpectralPowerDistribution('Custom2', data2)
    >>> multi_spd_plot([spd1, spd2]))
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    if use_spds_colours:
        illuminant = ILLUMINANTS_RELATIVE_SPDS.get('D65')

    x_limit_min, x_limit_max, y_limit_min, y_limit_max = [], [], [], []
    for spd in spds:
        wavelengths, values = tuple(zip(*[(key, value) for key, value in spd]))

        start, end, steps = spd.shape
        x_limit_min.append(start)
        x_limit_max.append(end)
        y_limit_min.append(min(values))
        y_limit_max.append(max(values))

        matplotlib.pyplot.rc("axes", color_cycle=["r", "g", "b", "y"])

        if use_spds_colours:
            XYZ = spectral_to_XYZ(spd, cmfs, illuminant) / 100.
            if normalise_spds_colours:
                XYZ /= np.max(XYZ)
            RGB = XYZ_to_sRGB(XYZ)
            RGB = np.clip(RGB, 0., 1.)

            pylab.plot(wavelengths, values, color=RGB, label=spd.name,
                       linewidth=2.)
        else:
            pylab.plot(wavelengths, values, label=spd.name, linewidth=2.)

    settings = {'x_label': u'Wavelength λ (nm)',
                'y_label': 'Spectral Power Distribution',
                'x_tighten': True,
                'legend': True,
                'legend_location': 'upper left',
                'x_ticker': True,
                'y_ticker': True,
                'limits': [min(x_limit_min), max(x_limit_max),
                           min(y_limit_min), max(y_limit_max)]}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_cmfs_plot(cmfs='CIE 1931 2 Degree Standard Observer', **kwargs):
    """
    Plots given colour matching functions.

    Parameters
    ----------
    cmfs : unicode, optional
        Colour matching functions to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.single_cmfs_plot('CIE 1931 2 Degree Standard Observer')
    True
    """

    settings = {'title': '"{0}" - Colour Matching Functions'.format(cmfs)}
    settings.update(kwargs)

    return multi_cmfs_plot([cmfs], **settings)


def multi_cmfs_plot(cmfss=['CIE 1931 2 Degree Standard Observer',
                           'CIE 1964 10 Degree Standard Observer'], **kwargs):
    """
    Plots given colour matching functions.

    Parameters
    ----------
    cmfss : list, optional
        Colour matching functions to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.multi_cmfs_plot(['CIE 1931 2 Degree Standard Observer', 'CIE 1964 10 Degree Standard Observer'])
    True
    """

    x_limit_min, x_limit_max, y_limit_min, y_limit_max = [], [], [], []
    for axis, rgb in (('x', [1., 0., 0.]),
                      ('y', [0., 1., 0.]),
                      ('z', [0., 0., 1.])):
        for i, cmfs in enumerate(cmfss):
            cmfs, name = _get_cmfs(cmfs), cmfs

            rgb = [reduce(lambda y, _: y * 0.5, range(i), x) for x in rgb]
            wavelengths, values = tuple(
                zip(*[(key, value) for key, value in getattr(cmfs, axis)]))

            start, end, steps = cmfs.shape
            x_limit_min.append(start)
            x_limit_max.append(end)
            y_limit_min.append(min(values))
            y_limit_max.append(max(values))

            pylab.plot(wavelengths,
                       values,
                       color=rgb,
                       label=u'{0} - {1}'.format(
                           cmfs.labels.get(axis), cmfs.name),
                       linewidth=2.)

    settings = {
        'title': '{0} - Colour Matching Functions'.format(', '.join(cmfss)),
        'x_label': u'Wavelength λ (nm)',
        'y_label': 'Tristimulus Values',
        'x_tighten': True,
        'legend': True,
        'legend_location': 'upper right',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'y_axis_line': True,
        'limits': [min(x_limit_min), max(x_limit_max), min(y_limit_min),
                   max(y_limit_max)]}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_illuminant_relative_spd_plot(
        illuminant='A',
        cmfs='CIE 1931 2 Degree Standard Observer',
        **kwargs):
    """
    Plots given single illuminant relative spectral power distribution.

    Parameters
    ----------
    illuminant : unicode, optional
        Factory illuminant to plot.
    cmfs : unicode, optional
        Standard observer colour matching functions to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.single_illuminant_relative_spd_plot('A')
    True
    """

    title = 'Illuminant "{0}" - {1}'.format(illuminant, cmfs)

    illuminant, name = _get_illuminant(illuminant), illuminant
    cmfs, name = _get_cmfs(cmfs), cmfs

    settings = {'title': title,
                'y_label': 'Relative Spectral Power Distribution'}
    settings.update(kwargs)

    return single_spd_plot(illuminant, **settings)


def multi_illuminants_relative_spd_plot(illuminants=['A', 'B', 'C'], **kwargs):
    """
    Plots given illuminants relative spectral power distributions.

    Parameters
    ----------
    illuminants : tuple or list, optional
        Factory illuminants to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.multi_illuminants_relative_spd_plot(['A', 'B', 'C'])
    True
    """

    spds = []
    for illuminant in illuminants:
        spds.append(_get_illuminant(illuminant))

    settings = {
        'title': '{0} - Illuminants Relative Spectral Power Distribution'.format(
            ', '.join(illuminants)),
        'y_label': 'Relative Spectral Power Distribution'}
    settings.update(kwargs)

    return multi_spd_plot(spds, **settings)


def visible_spectrum_plot(cmfs='CIE 1931 2 Degree Standard Observer',
                          **kwargs):
    """
    Plots the visible colours spectrum using given standard observer *CIE XYZ*
    colour matching functions.

    Parameters
    ----------
    cmfs : unicode, optional
        Standard observer colour matching functions used for spectrum creation.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.visible_spectrum_plot('CIE 1931 2 Degree Standard Observer')
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    cmfs = cmfs.clone().interpolate(360, 830)

    start, end, steps = cmfs.shape
    wavelengths = np.arange(start, end + steps, steps)

    colours = []
    for i in wavelengths:
        XYZ = wavelength_to_XYZ(i, cmfs)
        colours.append(XYZ_to_sRGB(XYZ))

    colours = np.array([np.ravel(x) for x in colours])
    colours *= 1. / np.max(colours)
    colours = np.clip(colours, 0, 1)

    settings = {'title': 'The Visible Spectrum - {0}'.format(name),
                'x_label': u'Wavelength λ (nm)',
                'x_tighten': True}
    settings.update(kwargs)

    return colour_parameters_plot([colour_parameter(x=x[0], RGB=x[1])
                                   for x in tuple(zip(wavelengths, colours))],
                                  **settings)


@figure_size((32, 32))
def CIE_1931_chromaticity_diagram_colours_plot(
        surface=1.25,
        spacing=0.00075,
        cmfs='CIE 1931 2 Degree Standard Observer',
        **kwargs):
    """
    Plots the *CIE 1931 Chromaticity Diagram* colours.

    Parameters
    ----------
    surface : float, optional
        Generated markers surface.
    spacing : float, optional
        Spacing between markers.
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1931_chromaticity_diagram_colours_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    illuminant = ILLUMINANTS.get(
        'CIE 1931 2 Degree Standard Observer').get('E')

    XYZs = [value for key, value in cmfs]

    x, y = tuple(zip(*([XYZ_to_xy(x) for x in XYZs])))

    path = matplotlib.path.Path(tuple(zip(x, y)))
    x_dot, y_dot, colours = [], [], []
    for i in np.arange(0., 1., spacing):
        for j in np.arange(0., 1., spacing):
            if path.contains_path(matplotlib.path.Path([[i, j], [i, j]])):
                x_dot.append(i)
                y_dot.append(j)

                XYZ = xy_to_XYZ((i, j))
                RGB = normalise(XYZ_to_sRGB(XYZ, illuminant))

                colours.append(RGB)

    pylab.scatter(x_dot, y_dot, color=colours, s=surface)

    settings = {'no_ticks': True,
                'bounding_box': [0., 1., 0., 1.],
                'bbox_inches': 'tight',
                'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def CIE_1931_chromaticity_diagram_plot(
        cmfs='CIE 1931 2 Degree Standard Observer', **kwargs):
    """
    Plots the *CIE 1931 Chromaticity Diagram*.

    Parameters
    ----------
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1931_chromaticity_diagram_plot()
    True

    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    image = matplotlib.image.imread(
        os.path.join(RESOURCES_DIRECTORY,
                     'CIE_1931_Chromaticity_Diagram_{0}_Small.png'.format(
                         cmfs.name.replace(' ', '_'))))
    pylab.imshow(image, interpolation='nearest', extent=(0, 1, 0, 1))

    labels = (
        [390, 460, 470, 480, 490, 500, 510, 520, 540, 560, 580, 600, 620,
         700])

    wavelengths = cmfs.wavelengths
    equal_energy = np.array([1. / 3.] * 2)

    XYZs = [value for key, value in cmfs]

    x, y = tuple(zip(*([XYZ_to_xy(x) for x in XYZs])))

    wavelengths_chromaticity_coordinates = dict(
        tuple(zip(wavelengths, tuple(zip(x, y)))))

    pylab.plot(x, y, color='black', linewidth=2.)
    pylab.plot((x[-1], x[0]), (y[-1], y[0]), color='black', linewidth=2.)

    for label in labels:
        x, y = wavelengths_chromaticity_coordinates.get(label)
        pylab.plot(x, y, 'o', color='black', linewidth=2.)

        index = bisect.bisect(wavelengths, label)
        left = wavelengths[index - 1] if index >= 0 else wavelengths[index]
        right = (wavelengths[index]
                 if index < len(wavelengths) else
                 wavelengths[-1])

        dx = (wavelengths_chromaticity_coordinates.get(right)[0] -
              wavelengths_chromaticity_coordinates.get(left)[0])
        dy = (wavelengths_chromaticity_coordinates.get(right)[1] -
              wavelengths_chromaticity_coordinates.get(left)[1])

        norme = lambda x: x / np.linalg.norm(x)

        xy = np.array([x, y])
        direction = np.array((-dy, dx))

        normal = (np.array((-dy, dx))
                  if np.dot(norme(xy - equal_energy),
                            norme(direction)) > 0 else
                  np.array((dy, -dx)))
        normal = norme(normal)
        normal /= 25

        pylab.plot([x, x + normal[0] * 0.75],
                   [y, y + normal[1] * 0.75],
                   color='black',
                   linewidth=1.5)
        pylab.text(x + normal[0],
                   y + normal[1],
                   label,
                   clip_on=True,
                   ha='left' if normal[0] >= 0 else 'right',
                   va='center',
                   fontdict={'size': 'small'})

    settings = {
        'title': 'CIE 1931 Chromaticity Diagram - {0}'.format(name),
        'x_label': 'CIE x',
        'y_label': 'CIE y',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'bounding_box': [-0.1, 0.9, -0.1, 0.9],
        'bbox_inches': 'tight',
        'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def colourspaces_CIE_1931_chromaticity_diagram_plot(
        colourspaces=['sRGB', 'ACES RGB', 'Pointer Gamut'],
        cmfs='CIE 1931 2 Degree Standard Observer',
        **kwargs):
    """
    Plots given colourspaces in *CIE 1931 Chromaticity Diagram*.

    Parameters
    ----------
    colourspaces : list, optional
        Colourspaces to plot.
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> csps = ['sRGB', 'ACES RGB']
    >>> colour.plotting.colourspaces_CIE_1931_chromaticity_diagram_plot(csps)
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    settings = {'title': '{0} - {1}'.format(', '.join(colourspaces), name),
                'standalone': False}
    settings.update(kwargs)

    if not CIE_1931_chromaticity_diagram_plot(**settings):
        return

    x_limit_min, x_limit_max = [-0.1], [0.9]
    y_limit_min, y_limit_max = [-0.1], [0.9]
    for colourspace in colourspaces:
        if colourspace == 'Pointer Gamut':
            x, y = tuple(zip(*POINTER_GAMUT_DATA))
            pylab.plot(x,
                       y,
                       label='Pointer Gamut',
                       color='0.95',
                       linewidth=2.)
            pylab.plot([x[-1],
                        x[0]],
                       [y[-1],
                        y[0]],
                       color='0.95',
                       linewidth=2.)
        else:
            colourspace, name = _get_RGB_colourspace(
                colourspace), colourspace

            random_colour = lambda: float(random.randint(64, 224)) / 255
            r, g, b = random_colour(), random_colour(), random_colour()

            primaries = colourspace.primaries
            whitepoint = colourspace.whitepoint

            pylab.plot([whitepoint[0], whitepoint[0]],
                       [whitepoint[1], whitepoint[1]],
                       color=(r, g, b),
                       label=colourspace.name,
                       linewidth=2.)
            pylab.plot([whitepoint[0], whitepoint[0]],
                       [whitepoint[1], whitepoint[1]],
                       'o',
                       color=(r, g, b),
                       linewidth=2.)
            pylab.plot([primaries[0, 0], primaries[1, 0]],
                       [primaries[0, 1], primaries[1, 1]],
                       'o-',
                       color=(r, g, b),
                       linewidth=2.)
            pylab.plot([primaries[1, 0], primaries[2, 0]],
                       [primaries[1, 1], primaries[2, 1]],
                       'o-',
                       color=(r, g, b),
                       linewidth=2.)
            pylab.plot([primaries[2, 0], primaries[0, 0]],
                       [primaries[2, 1], primaries[0, 1]],
                       'o-',
                       color=(r, g, b),
                       linewidth=2.)

            x_limit_min.append(np.amin(primaries[:, 0]))
            y_limit_min.append(np.amin(primaries[:, 1]))
            x_limit_max.append(np.amax(primaries[:, 0]))
            y_limit_max.append(np.amax(primaries[:, 1]))

    settings.update({'legend': True,
                     'legend_location': 'upper right',
                     'x_tighten': True,
                     'y_tighten': True,
                     'limits': [min(x_limit_min), max(x_limit_max),
                                min(y_limit_min), max(y_limit_max)],
                     'margins': [-0.05, 0.05, -0.05, 0.05],
                     'standalone': True})

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def planckian_locus_CIE_1931_chromaticity_diagram_plot(
        illuminants=['A', 'B', 'C'],
        **kwargs):
    """
    Plots the planckian locus and given illuminants in
    *CIE 1931 Chromaticity Diagram*.

    Parameters
    ----------
    illuminants : tuple or list, optional
        Factory illuminants to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> ils = ['A', 'B', 'C']
    >>> colour.plotting.planckian_locus_CIE_1931_chromaticity_diagram_plot(ils)
    True
    """

    cmfs = CMFS.get('CIE 1931 2 Degree Standard Observer')

    settings = {
        'title': '{0} Illuminants - Planckian Locus\n \
CIE 1931 Chromaticity Diagram - CIE 1931 2 Degree Standard Observer'.format(
            ', '.join(illuminants)) if illuminants else
        'Planckian Locus\n \
CIE 1931 Chromaticity Diagram - CIE 1931 2 Degree Standard Observer',
        'standalone': False}
    settings.update(kwargs)

    if not CIE_1931_chromaticity_diagram_plot(**settings):
        return

    start, end = 1667, 100000
    x, y = tuple(zip(*[UCS_uv_to_xy(CCT_to_uv(x, 0., cmfs=cmfs))
                       for x in np.arange(start, end + 250, 250)]))

    pylab.plot(x, y, color='black', linewidth=2.)

    for i in [1667, 2000, 2500, 3000, 4000, 6000, 10000]:
        x0, y0 = UCS_uv_to_xy(CCT_to_uv(i, -0.025, cmfs=cmfs))
        x1, y1 = UCS_uv_to_xy(CCT_to_uv(i, 0.025, cmfs=cmfs))
        pylab.plot([x0, x1], [y0, y1], color='black', linewidth=2.)
        pylab.annotate('{0}K'.format(i),
                       xy=(x0, y0),
                       xytext=(0, -10),
                       textcoords='offset points',
                       size='x-small')

    for illuminant in illuminants:
        xy = ILLUMINANTS.get(cmfs.name).get(illuminant)
        if xy is None:
            raise KeyError(
                'Illuminant "{0}" not found in factory illuminants: "{1}".'.format(
                    illuminant, sorted(ILLUMINANTS.get(cmfs.name).keys())))

        pylab.plot(xy[0], xy[1], 'o', color='white', linewidth=2.)

        pylab.annotate(illuminant,
                       xy=(xy[0], xy[1]),
                       xytext=(-50, 30),
                       textcoords='offset points',
                       arrowprops=dict(arrowstyle='->',
                                       connectionstyle='arc3, rad=-0.2'))

    settings.update({'standalone': True})

    return display(**settings)


@figure_size((32, 32))
def CIE_1960_UCS_chromaticity_diagram_colours_plot(
        surface=1.25,
        spacing=0.00075,
        cmfs='CIE 1931 2 Degree Standard Observer',
        **kwargs):
    """
    Plots the *CIE 1960 UCS Chromaticity Diagram* colours.

    Parameters
    ----------
    surface : float, optional
        Generated markers surface.
    spacing : float, optional
        Spacing between markers.
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1960_UCS_chromaticity_diagram_colours_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    illuminant = ILLUMINANTS.get(
        'CIE 1931 2 Degree Standard Observer').get('E')

    UVWs = [XYZ_to_UCS(value) for key, value in cmfs]

    u, v = tuple(zip(*([UCS_to_uv(x) for x in UVWs])))

    path = matplotlib.path.Path(tuple(zip(u, v)))
    x_dot, y_dot, colours = [], [], []
    for i in np.arange(0., 1., spacing):
        for j in np.arange(0., 1., spacing):
            if path.contains_path(matplotlib.path.Path([[i, j], [i, j]])):
                x_dot.append(i)
                y_dot.append(j)

                XYZ = xy_to_XYZ(UCS_uv_to_xy((i, j)))
                RGB = normalise(XYZ_to_sRGB(XYZ, illuminant))

                colours.append(RGB)

    pylab.scatter(x_dot, y_dot, color=colours, s=surface)

    settings = {'no_ticks': True,
                'bounding_box': [0., 1., 0., 1.],
                'bbox_inches': 'tight',
                'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def CIE_1960_UCS_chromaticity_diagram_plot(
        cmfs='CIE 1931 2 Degree Standard Observer', **kwargs):
    """
    Plots the *CIE 1960 UCS Chromaticity Diagram*.

    Parameters
    ----------
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1960_UCS_chromaticity_diagram_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    image = matplotlib.image.imread(
        os.path.join(RESOURCES_DIRECTORY,
                     'CIE_1960_UCS_Chromaticity_Diagram_{0}_Small.png'.format(
                         cmfs.name.replace(' ', '_'))))
    pylab.imshow(image, interpolation='nearest', extent=(0, 1, 0, 1))

    labels = [420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530,
              540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 680]

    wavelengths = cmfs.wavelengths
    equal_energy = np.array([1. / 3.] * 2)

    UVWs = [XYZ_to_UCS(value) for key, value in cmfs]

    u, v = tuple(zip(*([UCS_to_uv(x) for x in UVWs])))

    wavelengths_chromaticity_coordinates = dict(
        tuple(zip(wavelengths, tuple(zip(u, v)))))

    pylab.plot(u, v, color='black', linewidth=2.)
    pylab.plot((u[-1], u[0]), (v[-1], v[0]), color='black', linewidth=2.)

    for label in labels:
        u, v = wavelengths_chromaticity_coordinates.get(label)
        pylab.plot(u, v, 'o', color='black', linewidth=2.)

        index = bisect.bisect(wavelengths, label)
        left = wavelengths[index - 1] if index >= 0 else wavelengths[index]
        right = (wavelengths[index]
                 if index < len(wavelengths) else
                 wavelengths[-1])

        dx = (wavelengths_chromaticity_coordinates.get(right)[0] -
              wavelengths_chromaticity_coordinates.get(left)[0])
        dy = (wavelengths_chromaticity_coordinates.get(right)[1] -
              wavelengths_chromaticity_coordinates.get(left)[1])

        norme = lambda x: x / np.linalg.norm(x)

        uv = np.array([u, v])
        direction = np.array((-dy, dx))

        normal = (np.array((-dy, dx))
                  if np.dot(norme(uv - equal_energy),
                            norme(direction)) > 0 else
                  np.array((dy, -dx)))
        normal = norme(normal)
        normal /= 25

        pylab.plot([u, u + normal[0] * 0.75],
                   [v, v + normal[1] * 0.75],
                   color='black',
                   linewidth=1.5)
        pylab.text(u + normal[0],
                   v + normal[1],
                   label,
                   clip_on=True,
                   ha='left' if normal[0] >= 0 else 'right',
                   va='center',
                   fontdict={'size': 'small'})

    settings = {
        'title': 'CIE 1960 UCS Chromaticity Diagram - {0}'.format(name),
        'x_label': 'CIE u',
        'y_label': 'CIE v',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'bounding_box': [-0.075, 0.675, -0.15, 0.6],
        'bbox_inches': 'tight',
        'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def planckian_locus_CIE_1960_UCS_chromaticity_diagram_plot(
        illuminants=['A', 'C', 'E'], **kwargs):
    """
    Plots the planckian locus and given illuminants in
    *CIE 1960 UCS Chromaticity Diagram*.

    Parameters
    ----------
    illuminants : tuple or list, optional
        Factory illuminants to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> ils = ['A', 'C', 'E']
    >>> colour.plotting.planckian_locus_CIE_1960_UCS_chromaticity_diagram_plot(ils)
    True
    """

    cmfs = CMFS.get('CIE 1931 2 Degree Standard Observer')

    settings = {
        'title': '{0} Illuminants - Planckian Locus\n \
CIE 1960 UCS Chromaticity Diagram - CIE 1931 2 Degree Standard Observer'.format(
            ', '.join(illuminants)) if illuminants else
        'Planckian Locus\n \
CIE 1960 UCS Chromaticity Diagram - CIE 1931 2 Degree Standard Observer',
        'standalone': False}
    settings.update(kwargs)

    if not CIE_1960_UCS_chromaticity_diagram_plot(**settings):
        return

    xy_to_uv = lambda x: UCS_to_uv(XYZ_to_UCS(xy_to_XYZ(x)))

    start, end = 1667, 100000
    u, v = tuple(zip(*[CCT_to_uv(x, 0., cmfs=cmfs)
                       for x in np.arange(start, end + 250, 250)]))

    pylab.plot(u, v, color='black', linewidth=2.)

    for i in [1667, 2000, 2500, 3000, 4000, 6000, 10000]:
        u0, v0 = CCT_to_uv(i, -0.05)
        u1, v1 = CCT_to_uv(i, 0.05)
        pylab.plot([u0, u1], [v0, v1], color='black', linewidth=2.)
        pylab.annotate('{0}K'.format(i),
                       xy=(u0, v0),
                       xytext=(0, -10),
                       textcoords='offset points',
                       size='x-small')

    for illuminant in illuminants:
        uv = xy_to_uv(ILLUMINANTS.get(cmfs.name).get(illuminant))
        if uv is None:
            raise KeyError(
                'Illuminant "{0}" not found in factory illuminants: "{1}".'.format(
                    illuminant, sorted(ILLUMINANTS.get(cmfs.name).keys())))

        pylab.plot(uv[0], uv[1], 'o', color='white', linewidth=2.)

        pylab.annotate(illuminant,
                       xy=(uv[0], uv[1]),
                       xytext=(-50, 30),
                       textcoords='offset points',
                       arrowprops=dict(arrowstyle='->',
                                       connectionstyle='arc3, rad=-0.2'))

    settings.update({'standalone': True})

    return display(**settings)


@figure_size((32, 32))
def CIE_1976_UCS_chromaticity_diagram_colours_plot(
        surface=1.25,
        spacing=0.00075,
        cmfs='CIE 1931 2 Degree Standard Observer',
        **kwargs):
    """
    Plots the *CIE 1976 UCS Chromaticity Diagram* colours.

    Parameters
    ----------
    surface : float, optional
        Generated markers surface.
    spacing : float, optional
        Spacing between markers.
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1976_UCS_chromaticity_diagram_colours_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    illuminant = ILLUMINANTS.get(
        'CIE 1931 2 Degree Standard Observer').get('D50')

    Luvs = [XYZ_to_Luv(value, illuminant) for key, value in cmfs]

    u, v = tuple(zip(*([Luv_to_uv(x) for x in Luvs])))

    path = matplotlib.path.Path(tuple(zip(u, v)))
    x_dot, y_dot, colours = [], [], []
    for i in np.arange(0., 1., spacing):
        for j in np.arange(0., 1., spacing):
            if path.contains_path(matplotlib.path.Path([[i, j], [i, j]])):
                x_dot.append(i)
                y_dot.append(j)

                XYZ = xy_to_XYZ(Luv_uv_to_xy((i, j)))
                RGB = normalise(XYZ_to_sRGB(XYZ, illuminant))

                colours.append(RGB)

    pylab.scatter(x_dot, y_dot, color=colours, s=surface)

    settings = {'no_ticks': True,
                'bounding_box': [0., 1., 0., 1.],
                'bbox_inches': 'tight',
                'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


@figure_size((8, 8))
def CIE_1976_UCS_chromaticity_diagram_plot(
        cmfs='CIE 1931 2 Degree Standard Observer', **kwargs):
    """
    Plots the *CIE 1976 UCS Chromaticity Diagram*.

    Parameters
    ----------
    cmfs : unicode, optional
        Standard observer colour matching functions used for diagram bounds.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.CIE_1976_UCS_chromaticity_diagram_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    image = matplotlib.image.imread(
        os.path.join(RESOURCES_DIRECTORY,
                     'CIE_1976_UCS_Chromaticity_Diagram_{0}_Small.png'.format(
                         cmfs.name.replace(' ', '_'))))
    pylab.imshow(image, interpolation='nearest', extent=(0, 1, 0, 1))

    labels = [420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530,
              540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 680]

    wavelengths = cmfs.wavelengths
    equal_energy = np.array([1. / 3.] * 2)

    illuminant = ILLUMINANTS.get(
        'CIE 1931 2 Degree Standard Observer').get('D50')

    Luvs = [XYZ_to_Luv(value, illuminant) for key, value in cmfs]

    u, v = tuple(zip(*([Luv_to_uv(x) for x in Luvs])))

    wavelengths_chromaticity_coordinates = dict(zip(wavelengths,
                                                    tuple(zip(u, v))))

    pylab.plot(u, v, color='black', linewidth=2.)
    pylab.plot((u[-1], u[0]), (v[-1], v[0]), color='black', linewidth=2.)

    for label in labels:
        u, v = wavelengths_chromaticity_coordinates.get(label)
        pylab.plot(u, v, 'o', color='black', linewidth=2.)

        index = bisect.bisect(wavelengths, label)
        left = wavelengths[index - 1] if index >= 0 else wavelengths[index]
        right = (wavelengths[index]
                 if index < len(wavelengths) else
                 wavelengths[-1])

        dx = (wavelengths_chromaticity_coordinates.get(right)[0] -
              wavelengths_chromaticity_coordinates.get(left)[0])
        dy = (wavelengths_chromaticity_coordinates.get(right)[1] -
              wavelengths_chromaticity_coordinates.get(left)[1])

        norme = lambda x: x / np.linalg.norm(x)

        uv = np.array([u, v])
        direction = np.array((-dy, dx))

        normal = (np.array((-dy, dx))
                  if np.dot(norme(uv - equal_energy),
                            norme(direction)) > 0 else
                  np.array((dy, -dx)))
        normal = norme(normal)
        normal /= 25

        pylab.plot([u, u + normal[0] * 0.75],
                   [v, v + normal[1] * 0.75],
                   color='black',
                   linewidth=1.5)
        pylab.text(u + normal[0],
                   v + normal[1],
                   label,
                   clip_on=True,
                   ha='left' if normal[0] >= 0 else 'right',
                   va='center',
                   fontdict={'size': 'small'})

    settings = {
        'title': 'CIE 1976 UCS Chromaticity Diagram - {0}'.format(name),
        'x_label': 'CIE u"',
        'y_label': 'CIE v"',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'bounding_box': [-0.1, .7, -.1, .7],
        'bbox_inches': 'tight',
        'pad_inches': 0}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_munsell_value_function_plot(function='Munsell Value ASTM D1535-08',
                                       **kwargs):
    """
    Plots given *Lightness* function.

    Parameters
    ----------
    function : unicode, optional
        *Munsell* value function to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> f = 'Munsell Value ASTM D1535-08'
    >>> colour.plotting.single_munsell_value_function_plot(f)
    True
    """

    settings = {'title': '{0} - Munsell Value Function'.format(function)}
    settings.update(kwargs)

    return multi_munsell_value_function_plot([function], **settings)


@figure_size((8, 8))
def multi_munsell_value_function_plot(
        functions=['Munsell Value ASTM D1535-08',
                   'Munsell Value McCamy 1987'],
        **kwargs):
    """
    Plots given *Munsell* value functions.

    Parameters
    ----------
    functions : list, optional
        *Munsell* value functions to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> fs = ('Munsell Value ASTM D1535-08', 'Munsell Value McCamy 1987')
    >>> colour.plotting.multi_munsell_value_function_plot(fs)
    True
    """

    samples = np.linspace(0., 100., 1000)
    for i, function in enumerate(functions):
        function, name = MUNSELL_VALUE_FUNCTIONS.get(function), function
        if function is None:
            raise KeyError('"{0}" "Munsell" value function not found in \
supported "Munsell" value functions: "{1}".'.format(
                name, sorted(MUNSELL_VALUE_FUNCTIONS.keys())))

        pylab.plot(samples,
                   [function(x) for x in samples],
                   label=u'{0}'.format(name),
                   linewidth=2.)

    settings = {
        'title': '{0} - Munsell Functions'.format(', '.join(functions)),
        'x_label': 'Luminance Y',
        'y_label': 'Munsell Value V',
        'x_tighten': True,
        'legend': True,
        'legend_location': 'upper left',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'limits': [0., 100., 0., 100.]}

    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_lightness_function_plot(function='Lightness 1976', **kwargs):
    """
    Plots given *Lightness* function.

    Parameters
    ----------
    function : unicode, optional
        *Lightness* function to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.single_lightness_function_plot('Lightness 1976')
    True
    """

    settings = {'title': '{0} - Lightness Function'.format(function)}
    settings.update(kwargs)

    return multi_lightness_function_plot([function], **settings)


@figure_size((8, 8))
def multi_lightness_function_plot(
        functions=['Lightness 1976', 'Lightness Wyszecki 1964'],
        **kwargs):
    """
    Plots given *Lightness* functions.

    Parameters
    ----------
    functions : list, optional
        *Lightness* functions to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> fs = ('Lightness 1976', 'Lightness Wyszecki 1964')
    >>> colour.multi_lightness_function_plot(fs)
    True
    """

    samples = np.linspace(0., 100., 1000)
    for i, function in enumerate(functions):
        function, name = LIGHTNESS_FUNCTIONS.get(function), function
        if function is None:
            raise KeyError('"{0}" "Lightness" function not found in supported \
"Lightness" functions: "{1}".'.format(
                name, sorted(LIGHTNESS_FUNCTIONS.keys())))

        pylab.plot(samples,
                   [function(x) for x in samples],
                   label=u'{0}'.format(name),
                   linewidth=2.)

    settings = {
        'title': '{0} - Lightness Functions'.format(', '.join(functions)),
        'x_label': 'Luminance Y',
        'y_label': 'Lightness L*',
        'x_tighten': True,
        'legend': True,
        'legend_location': 'upper left',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'limits': [0., 100., 0., 100.]}

    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def single_transfer_function_plot(colourspace='sRGB', **kwargs):
    """
    Plots given colourspace transfer function.

    Parameters
    ----------
    colourspace : unicode, optional
        *RGB* Colourspace transfer function to plot.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.single_transfer_function_plot('sRGB')
    True
    """

    settings = {'title': '{0} - Transfer Function'.format(colourspace)}
    settings.update(kwargs)

    return multi_transfer_function_plot([colourspace], **settings)


@figure_size((8, 8))
def multi_transfer_function_plot(colourspaces=['sRGB', 'Rec. 709'],
                                 inverse=False, **kwargs):
    """
    Plots given colourspaces transfer functions.

    Parameters
    ----------
    colourspaces : list, optional
        Colourspaces transfer functions to plot.
    inverse : bool
        Plot inverse transfer functions.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting..multi_transfer_function_plot(['sRGB', 'Rec. 709'])
    True
    """

    samples = np.linspace(0., 1., 1000)
    for i, colourspace in enumerate(colourspaces):
        colourspace, name = _get_RGB_colourspace(colourspace), colourspace

        RGBs = np.array([colourspace.inverse_transfer_function(x)
                         if inverse else
                         colourspace.transfer_function(x)
                         for x in samples])
        pylab.plot(samples,
                   RGBs,
                   label=u'{0}'.format(colourspace.name),
                   linewidth=2.)

    settings = {
        'title': '{0} - Transfer Functions'.format(
            ', '.join(colourspaces)),
        'x_tighten': True,
        'legend': True,
        'legend_location': 'upper left',
        'x_ticker': True,
        'y_ticker': True,
        'grid': True,
        'limits': [0., 1., 0., 1.]}

    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)

    return display(**settings)


def blackbody_spectral_radiance_plot(
        temperature=3500,
        cmfs='CIE 1931 2 Degree Standard Observer',
        blackbody='VY Canis Major',
        **kwargs):
    """
    Plots given blackbody spectral radiance.

    Parameters
    ----------
    temperature : float, optional
        Blackbody temperature.
    cmfs : unicode, optional
        Standard observer colour matching functions.
    blackbody : unicode, optional
        Blackbody name.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.blackbody_spectral_radiance_plot(3500)
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    matplotlib.pyplot.subplots_adjust(hspace=0.4)

    spd = blackbody_spectral_power_distribution(temperature, *cmfs.shape)

    matplotlib.pyplot.figure(1)
    matplotlib.pyplot.subplot(211)

    settings = {'title': '{0} - Spectral Radiance'.format(blackbody),
                'y_label': u'W / (sr m²) / m',
                'standalone': False}
    settings.update(kwargs)

    single_spd_plot(spd, name, **settings)

    XYZ = spectral_to_XYZ(spd, cmfs) / 100.
    RGB = normalise(XYZ_to_sRGB(XYZ))

    matplotlib.pyplot.subplot(212)

    settings = {'title': '{0} - Colour'.format(blackbody),
                'x_label': '{0}K'.format(temperature),
                'y_label': '',
                'aspect': None,
                'standalone': False}

    single_colour_plot(colour_parameter(name='', RGB=RGB), **settings)

    settings = {'standalone': True}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)
    return display(**settings)


def blackbody_colours_plot(start=150,
                           end=12500,
                           steps=50,
                           cmfs='CIE 1931 2 Degree Standard Observer',
                           **kwargs):
    """
    Plots blackbody colours.

    Parameters
    ----------
    start : float, optional
        Temperature range start in kelvins.
    end : float, optional
        Temperature range end in kelvins.
    steps : float, optional
        Temperature range steps.
    cmfs : unicode, optional
        Standard observer colour matching functions.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> colour.plotting.blackbody_colours_plot()
    True
    """

    cmfs, name = _get_cmfs(cmfs), cmfs

    colours = []
    temperatures = []

    for temperature in np.arange(start, end + steps, steps):
        spd = blackbody_spectral_power_distribution(temperature,
                                                    *cmfs.shape)

        XYZ = spectral_to_XYZ(spd, cmfs) / 100.
        RGB = normalise(XYZ_to_sRGB(XYZ))

        colours.append(RGB)
        temperatures.append(temperature)

    settings = {'title': 'Blackbody Colours',
                'x_label': 'Temperature K',
                'y_label': '',
                'x_tighten': True,
                'x_ticker': True,
                'y_ticker': False}

    settings.update(kwargs)
    return colour_parameters_plot([colour_parameter(x=x[0], RGB=x[1])
                                   for x in tuple(zip(temperatures, colours))],
                                  **settings)


@figure_size((8, 8))
def colour_rendering_index_bars_plot(illuminant, **kwargs):
    """
    Plots the *colour rendering index* of given illuminant.

    Parameters
    ----------
    illuminant : SpectralPowerDistribution
        Illuminant to plot the *colour rendering index*.
    \*\*kwargs : \*\*
        Keywords arguments.

    Returns
    -------
    bool
        Definition success.

    Examples
    --------
    >>> il = colour.ILLUMINANTS_RELATIVE_SPDS.get('F2')
    >>> colour.plotting.colour_rendering_index_bars_plot(il)
    True
    """

    figure, axis = matplotlib.pyplot.subplots()

    colour_rendering_index, colour_rendering_indexes, additional_data = \
        get_colour_rendering_index(illuminant, additional_data=True)

    colours = ([[1.] * 3] + [normalise(XYZ_to_sRGB(x.XYZ / 100.))
                             for x in additional_data[0]])
    x, y = tuple(zip(*sorted(colour_rendering_indexes.items(),
                             key=lambda x: x[0])))
    x, y = np.array([0] + list(x)), np.array(
        [colour_rendering_index] + list(y))

    positive = True if np.sign(min(y)) in (0, 1) else False

    width = 0.5
    bars = pylab.bar(x, y, color=colours, width=width)
    y_ticks_steps = 10
    pylab.yticks(range(0 if positive else -100,
                       100 + y_ticks_steps,
                       y_ticks_steps))
    pylab.xticks(x + width / 2.,
                 ['Ra'] + ['R{0}'.format(index) for index in x[1:]])

    def label_bars(bars):
        for bar in bars:
            y = bar.get_y()
            height = bar.get_height()
            value = height if np.sign(y) in (0, 1) else -height
            axis.text(bar.get_x() + bar.get_width() / 2.,
                      0.025 * height + height + y,
                      '{0:.1f}'.format(value),
                      ha='center', va='bottom')

    label_bars(bars)

    settings = {
        'title': 'Colour Rendering Index - {0}'.format(illuminant.name),
        'grid': True,
        'x_tighten': True,
        'y_tighten': True,
        'limits': [-width, 14 + width * 2., -10. if positive else -110.,
                   110.]}
    settings.update(kwargs)

    bounding_box(**settings)
    aspect(**settings)
    return display(**settings)