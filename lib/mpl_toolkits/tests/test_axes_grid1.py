import matplotlib
import matplotlib.pyplot as plt
from matplotlib.testing.decorators import (
    image_comparison, remove_ticks_and_titles)

from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1 import AxesGrid
from mpl_toolkits.axes_grid1 import ImageGrid
from mpl_toolkits.axes_grid1.inset_locator import (
    zoomed_inset_axes,
    mark_inset,
    inset_axes,
    BboxConnectorPatch
)
from mpl_toolkits.axes_grid1.anchored_artists import (
    AnchoredSizeBar,
    AnchoredDirectionArrows)

from matplotlib.backend_bases import MouseEvent
from matplotlib.colors import LogNorm
from matplotlib.transforms import Bbox, TransformedBbox
from itertools import product

import pytest
import platform

import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal


@image_comparison(['divider_append_axes'])
def test_divider_append_axes():

    # the random data
    np.random.seed(0)
    x = np.random.randn(1000)
    y = np.random.randn(1000)

    fig, axScatter = plt.subplots()

    # the scatter plot:
    axScatter.scatter(x, y)

    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(axScatter)
    axHistbot = divider.append_axes("bottom", 1.2, pad=0.1, sharex=axScatter)
    axHistright = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)
    axHistleft = divider.append_axes("left", 1.2, pad=0.1, sharey=axScatter)
    axHisttop = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)

    # now determine nice limits by hand:
    binwidth = 0.25
    xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
    lim = (int(xymax/binwidth) + 1) * binwidth

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHisttop.hist(x, bins=bins)
    axHistbot.hist(x, bins=bins)
    axHistleft.hist(y, bins=bins, orientation='horizontal')
    axHistright.hist(y, bins=bins, orientation='horizontal')

    axHistbot.invert_yaxis()
    axHistleft.invert_xaxis()

    axHisttop.xaxis.set_ticklabels(())
    axHistbot.xaxis.set_ticklabels(())
    axHistleft.yaxis.set_ticklabels(())
    axHistright.yaxis.set_ticklabels(())


@image_comparison(['twin_axes_empty_and_removed'], extensions=["png"], tol=1)
def test_twin_axes_empty_and_removed():
    # Purely cosmetic font changes (avoid overlap)
    matplotlib.rcParams.update({"font.size": 8})
    matplotlib.rcParams.update({"xtick.labelsize": 8})
    matplotlib.rcParams.update({"ytick.labelsize": 8})
    generators = ["twinx", "twiny", "twin"]
    modifiers = ["", "host invisible", "twin removed", "twin invisible",
                 "twin removed\nhost invisible"]
    # Unmodified host subplot at the beginning for reference
    h = host_subplot(len(modifiers)+1, len(generators), 2)
    h.text(0.5, 0.5, "host_subplot", horizontalalignment="center",
        verticalalignment="center")
    # Host subplots with various modifications (twin*, visibility) applied
    for i, (mod, gen) in enumerate(product(modifiers, generators),
        len(generators)+1):
        h = host_subplot(len(modifiers)+1, len(generators), i)
        t = getattr(h, gen)()
        if "twin invisible" in mod:
            t.axis[:].set_visible(False)
        if "twin removed" in mod:
            t.remove()
        if "host invisible" in mod:
            h.axis[:].set_visible(False)
        h.text(0.5, 0.5, gen + ("\n" + mod if mod else ""),
            horizontalalignment="center", verticalalignment="center")
    plt.subplots_adjust(wspace=0.5, hspace=1)


def test_axesgrid_colorbar_log_smoketest():
    fig = plt.figure()
    grid = AxesGrid(fig, 111,  # modified to be only subplot
                    nrows_ncols=(1, 1),
                    label_mode="L",
                    cbar_location="top",
                    cbar_mode="single",
                    )

    Z = 10000 * np.random.rand(10, 10)
    im = grid[0].imshow(Z, interpolation="nearest", norm=LogNorm())

    grid.cbar_axes[0].colorbar(im)


@image_comparison(['inset_locator.png'], style='default', remove_text=True)
def test_inset_locator():
    def get_demo_image():
        from matplotlib.cbook import get_sample_data
        import numpy as np
        f = get_sample_data("axes_grid/bivariate_normal.npy", asfileobj=False)
        z = np.load(f)
        # z is a numpy array of 15x15
        return z, (-3, 4, -4, 3)

    fig, ax = plt.subplots(figsize=[5, 4])

    # prepare the demo image
    Z, extent = get_demo_image()
    Z2 = np.zeros([150, 150], dtype="d")
    ny, nx = Z.shape
    Z2[30:30 + ny, 30:30 + nx] = Z

    # extent = [-3, 4, -4, 3]
    ax.imshow(Z2, extent=extent, interpolation="nearest",
              origin="lower")

    axins = zoomed_inset_axes(ax, zoom=6, loc='upper right')
    axins.imshow(Z2, extent=extent, interpolation="nearest",
                 origin="lower")
    axins.yaxis.get_major_locator().set_params(nbins=7)
    axins.xaxis.get_major_locator().set_params(nbins=7)
    # sub region of the original image
    x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    plt.xticks(visible=False)
    plt.yticks(visible=False)

    # draw a bbox of the region of the inset axes in the parent axes and
    # connecting lines between the bbox and the inset axes area
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    asb = AnchoredSizeBar(ax.transData,
                          0.5,
                          '0.5',
                          loc='lower center',
                          pad=0.1, borderpad=0.5, sep=5,
                          frameon=False)
    ax.add_artist(asb)


@image_comparison(['inset_axes.png'], style='default', remove_text=True)
def test_inset_axes():
    def get_demo_image():
        from matplotlib.cbook import get_sample_data
        import numpy as np
        f = get_sample_data("axes_grid/bivariate_normal.npy", asfileobj=False)
        z = np.load(f)
        # z is a numpy array of 15x15
        return z, (-3, 4, -4, 3)

    fig, ax = plt.subplots(figsize=[5, 4])

    # prepare the demo image
    Z, extent = get_demo_image()
    Z2 = np.zeros([150, 150], dtype="d")
    ny, nx = Z.shape
    Z2[30:30 + ny, 30:30 + nx] = Z

    # extent = [-3, 4, -4, 3]
    ax.imshow(Z2, extent=extent, interpolation="nearest",
              origin="lower")

    # creating our inset axes with a bbox_transform parameter
    axins = inset_axes(ax, width=1., height=1., bbox_to_anchor=(1, 1),
                       bbox_transform=ax.transAxes)

    axins.imshow(Z2, extent=extent, interpolation="nearest",
                 origin="lower")
    axins.yaxis.get_major_locator().set_params(nbins=7)
    axins.xaxis.get_major_locator().set_params(nbins=7)
    # sub region of the original image
    x1, x2, y1, y2 = -1.5, -0.9, -2.5, -1.9
    axins.set_xlim(x1, x2)
    axins.set_ylim(y1, y2)

    plt.xticks(visible=False)
    plt.yticks(visible=False)

    # draw a bbox of the region of the inset axes in the parent axes and
    # connecting lines between the bbox and the inset axes area
    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

    asb = AnchoredSizeBar(ax.transData,
                          0.5,
                          '0.5',
                          loc='lower center',
                          pad=0.1, borderpad=0.5, sep=5,
                          frameon=False)
    ax.add_artist(asb)


def test_inset_axes_complete():
    dpi = 100
    figsize = (6, 5)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.subplots_adjust(.1, .1, .9, .9)

    ins = inset_axes(ax, width=2., height=2., borderpad=0)
    fig.canvas.draw()
    assert_array_almost_equal(
            ins.get_position().extents,
            np.array(((0.9*figsize[0]-2.)/figsize[0],
                      (0.9*figsize[1]-2.)/figsize[1], 0.9, 0.9)))

    ins = inset_axes(ax, width="40%", height="30%", borderpad=0)
    fig.canvas.draw()
    assert_array_almost_equal(
            ins.get_position().extents,
            np.array((.9-.8*.4, .9-.8*.3, 0.9, 0.9)))

    ins = inset_axes(ax, width=1., height=1.2, bbox_to_anchor=(200, 100),
                     loc=3, borderpad=0)
    fig.canvas.draw()
    assert_array_almost_equal(
            ins.get_position().extents,
            np.array((200./dpi/figsize[0], 100./dpi/figsize[1],
                     (200./dpi+1)/figsize[0], (100./dpi+1.2)/figsize[1])))

    ins1 = inset_axes(ax, width="35%", height="60%", loc=3, borderpad=1)
    ins2 = inset_axes(ax, width="100%", height="100%",
                      bbox_to_anchor=(0, 0, .35, .60),
                      bbox_transform=ax.transAxes, loc=3, borderpad=1)
    fig.canvas.draw()
    assert_array_equal(ins1.get_position().extents,
                       ins2.get_position().extents)

    with pytest.raises(ValueError):
        ins = inset_axes(ax, width="40%", height="30%",
                         bbox_to_anchor=(0.4, 0.5))

    with pytest.warns(UserWarning):
        ins = inset_axes(ax, width="40%", height="30%",
                         bbox_transform=ax.transAxes)


@image_comparison(['fill_facecolor.png'], remove_text=True, style='mpl20')
def test_fill_facecolor():
    fig, ax = plt.subplots(1, 5)
    fig.set_size_inches(5, 5)
    for i in range(1, 4):
        ax[i].yaxis.set_visible(False)
    ax[4].yaxis.tick_right()
    bbox = Bbox.from_extents(0, 0.4, 1, 0.6)

    # fill with blue by setting 'fc' field
    bbox1 = TransformedBbox(bbox, ax[0].transData)
    bbox2 = TransformedBbox(bbox, ax[1].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox1, bbox2, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", fc="b")
    p.set_clip_on(False)
    ax[0].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[0], 1, loc='upper right')
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[0], axins, loc1=2, loc2=4, fc="b", ec="0.5")

    # fill with yellow by setting 'facecolor' field
    bbox3 = TransformedBbox(bbox, ax[1].transData)
    bbox4 = TransformedBbox(bbox, ax[2].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox3, bbox4, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", facecolor="y")
    p.set_clip_on(False)
    ax[1].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[1], 1, loc='upper right')
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[1], axins, loc1=2, loc2=4, facecolor="y", ec="0.5")

    # fill with green by setting 'color' field
    bbox5 = TransformedBbox(bbox, ax[2].transData)
    bbox6 = TransformedBbox(bbox, ax[3].transData)
    # set color to BboxConnectorPatch
    p = BboxConnectorPatch(
        bbox5, bbox6, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", color="g")
    p.set_clip_on(False)
    ax[2].add_patch(p)
    # set color to marked area
    axins = zoomed_inset_axes(ax[2], 1, loc='upper right')
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    plt.gca().axes.get_xaxis().set_ticks([])
    plt.gca().axes.get_yaxis().set_ticks([])
    mark_inset(ax[2], axins, loc1=2, loc2=4, color="g", ec="0.5")

    # fill with green but color won't show if set fill to False
    bbox7 = TransformedBbox(bbox, ax[3].transData)
    bbox8 = TransformedBbox(bbox, ax[4].transData)
    # BboxConnectorPatch won't show green
    p = BboxConnectorPatch(
        bbox7, bbox8, loc1a=1, loc2a=2, loc1b=4, loc2b=3,
        ec="r", fc="g", fill=False)
    p.set_clip_on(False)
    ax[3].add_patch(p)
    # marked area won't show green
    axins = zoomed_inset_axes(ax[3], 1, loc='upper right')
    axins.set_xlim(0, 0.2)
    axins.set_ylim(0, 0.2)
    axins.get_xaxis().set_ticks([])
    axins.get_yaxis().set_ticks([])
    mark_inset(ax[3], axins, loc1=2, loc2=4, fc="g", ec="0.5", fill=False)


@image_comparison(['zoomed_axes.png', 'inverted_zoomed_axes.png'])
def test_zooming_with_inverted_axes():
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    ax.axis([1, 3, 1, 3])
    inset_ax = zoomed_inset_axes(ax, zoom=2.5, loc='lower right')
    inset_ax.axis([1.1, 1.4, 1.1, 1.4])

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])
    ax.axis([3, 1, 3, 1])
    inset_ax = zoomed_inset_axes(ax, zoom=2.5, loc='lower right')
    inset_ax.axis([1.4, 1.1, 1.4, 1.1])


@image_comparison(['anchored_direction_arrows.png'],
                  tol={'aarch64': 0.02}.get(platform.machine(), 0.0))
def test_anchored_direction_arrows():
    fig, ax = plt.subplots()
    ax.imshow(np.zeros((10, 10)), interpolation='nearest')

    simple_arrow = AnchoredDirectionArrows(ax.transAxes, 'X', 'Y')
    ax.add_artist(simple_arrow)


@image_comparison(['anchored_direction_arrows_many_args.png'])
def test_anchored_direction_arrows_many_args():
    fig, ax = plt.subplots()
    ax.imshow(np.ones((10, 10)))

    direction_arrows = AnchoredDirectionArrows(
            ax.transAxes, 'A', 'B', loc='upper right', color='red',
            aspect_ratio=-0.5, pad=0.6, borderpad=2, frameon=True, alpha=0.7,
            sep_x=-0.06, sep_y=-0.08, back_length=0.1, head_width=9,
            head_length=10, tail_width=5)
    ax.add_artist(direction_arrows)


def test_axes_locatable_position():
    fig, ax = plt.subplots()
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad='2%')
    fig.canvas.draw()
    assert np.isclose(cax.get_position(original=False).width,
                      0.03621495327102808)


@image_comparison(['image_grid.png'],
                  remove_text=True, style='mpl20',
                  savefig_kwarg={'bbox_inches': 'tight'})
def test_image_grid():
    # test that image grid works with bbox_inches=tight.
    im = np.arange(100).reshape((10, 10))

    fig = plt.figure(1, (4, 4))
    grid = ImageGrid(fig, 111, nrows_ncols=(2, 2), axes_pad=0.1)

    for i in range(4):
        grid[i].imshow(im, interpolation='nearest')
        grid[i].set_title('test {0}{0}'.format(i))


def test_gettightbbox():
    fig, ax = plt.subplots(figsize=(8, 6))

    l, = ax.plot([1, 2, 3], [0, 1, 0])

    ax_zoom = zoomed_inset_axes(ax, 4)
    ax_zoom.plot([1, 2, 3], [0, 1, 0])

    mark_inset(ax, ax_zoom, loc1=1, loc2=3, fc="none", ec='0.3')

    remove_ticks_and_titles(fig)
    bbox = fig.get_tightbbox(fig.canvas.get_renderer())
    np.testing.assert_array_almost_equal(bbox.extents,
                                         [-17.7, -13.9, 7.2, 5.4])


@pytest.mark.parametrize("click_on", ["big", "small"])
@pytest.mark.parametrize("big_on_axes,small_on_axes", [
    ("gca", "gca"),
    ("host", "host"),
    ("host", "parasite"),
    ("parasite", "host"),
    ("parasite", "parasite")
])
def test_picking_callbacks_overlap(big_on_axes, small_on_axes, click_on):
    """Test pick events on normal, host or parasite axes."""
    # Two rectangles are drawn and "clicked on", a small one and a big one
    # enclosing the small one. The axis on which they are drawn as well as the
    # rectangle that is clicked on are varied.
    # In each case we expect that both rectangles are picked if we click on the
    # small one and only the big one is picked if we click on the big one.
    # Also tests picking on normal axes ("gca") as a control.
    big = plt.Rectangle((0.25, 0.25), 0.5, 0.5, picker=5)
    small = plt.Rectangle((0.4, 0.4), 0.2, 0.2, facecolor="r", picker=5)
    # Machinery for "receiving" events
    received_events = []
    def on_pick(event):
        received_events.append(event)
    plt.gcf().canvas.mpl_connect('pick_event', on_pick)
    # Shortcut
    rectangles_on_axes = (big_on_axes, small_on_axes)
    # Axes setup
    axes = {"gca": None, "host": None, "parasite": None}
    if "gca" in rectangles_on_axes:
        axes["gca"] = plt.gca()
    if "host" in rectangles_on_axes or "parasite" in rectangles_on_axes:
        axes["host"] = host_subplot(111)
        axes["parasite"] = axes["host"].twin()
    # Add rectangles to axes
    axes[big_on_axes].add_patch(big)
    axes[small_on_axes].add_patch(small)
    # Simulate picking with click mouse event
    if click_on == "big":
        click_axes = axes[big_on_axes]
        axes_coords = (0.3, 0.3)
    else:
        click_axes = axes[small_on_axes]
        axes_coords = (0.5, 0.5)
    # In reality mouse events never happen on parasite axes, only host axes
    if click_axes is axes["parasite"]:
        click_axes = axes["host"]
    (x, y) = click_axes.transAxes.transform(axes_coords)
    m = MouseEvent("button_press_event", click_axes.figure.canvas, x, y,
                   button=1)
    click_axes.pick(m)
    # Checks
    expected_n_events = 2 if click_on == "small" else 1
    assert len(received_events) == expected_n_events
    event_rects = [event.artist for event in received_events]
    assert big in event_rects
    if click_on == "small":
        assert small in event_rects
