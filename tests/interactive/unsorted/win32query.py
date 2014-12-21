import sys

if sys.argv[1:] == ['debug']:
    DEBUG = True

if sys.argv[1:] == ['test'] or DEBUG:
    print('Running tests..')
    # test have_font (Windows)
    test_arial = have_font('Arial')
    print('Have font "Arial"? %s' % test_arial)
    print('Have font "missing-one"? %s' % have_font('missing-one'))
    # test cache is not rebuilt
    FONTDB = [FontEntry('stub', False, '', False, FF_MODERN)]
    assert (have_font('Arial') != test_arial)
    # test cache is rebiult
    assert (have_font('Arial', refresh=True) == test_arial)
    if not DEBUG:
        sys.exit()

if sys.argv[1:] == ['vector']:
    fonts = font_list(vector_only=True)
elif sys.argv[1:] == ['mono']:
    fonts = font_list(monospace_only=True)
elif sys.argv[1:] == ['vector', 'mono']:
    fonts = font_list(vector_only=True, monospace_only=True)
else:
    fonts = font_list()
print('\n'.join(fonts))

if DEBUG:
    print("Total: %s" % len(
        font_list()))  # -- CHAPTER 2: WORK WITH FONT DIMENSIONS --
#
# Essential info about font metrics http://support.microsoft.com/kb/32667
# And about logical units at http://www.winprog.org/tutorial/fonts.html

# x. Convert desired font size from points into logical units (pixels)

# By default logical for the screen units are pixels. This is defined
# by default MM_TEXT mapping mode.

# Point is ancient unit of measurement for physical size of a font.
# 10pt is equal to 3.527mm. To make sure a char on screen has physical
# size equal to 3.527mm, we need to know display size to calculate how
# many pixels are in 3.527mm, and then fetch font that best matches
# this size.

# Essential info about conversion http://support.microsoft.com/kb/74299

# x.1 Get pixels per inch using GetDeviceCaps() or ...


#-- CHAPTER 3: LAYERED FONT API --
#
# y. Font object with several layers of info

# Font object should contains normalized font information. This
# information is split according to usage. For example, level 0 property
# is font id - its name. Level 1 can be information about loaded font
# characters - in pyglet it could be cached/used glyphs and video memory
# taken by those glyphs.

# [ ] (pyglet) investigate if it is possible to get video memory size
#              occupied by the font glyphs

# [ ] (pyglet) investigate if it is possible to unload font from video
#              memory if its unused
