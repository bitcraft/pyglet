Warning
=======

The tests for pyglet are going through a major overhaul in organization and
implementation.  My goals are to organize the tests into the following types:
  - Interactive tests that require user input or verification
  - Integration tests that may open a window but do not require user interaction
  - Unit tests that make uses of mocks to verify behaviour
  
The pyglet project seems to have decent coverage, but it is difficult to tell
because of how awkward the testing procedures are.  This reorganization aims
to reduce the complexity of testing so that patches and changes can be verified
more quickly.

One particularly part of the pyglet project is that many modules include tests
as part of the module.  As I go through the project, I am copy/pasting the
module level tests that I find and putting the in tests/unsorted.  After their
tirage, they can be converted into a test that fits the 3 aforementioned types
and everyone will appreciate how easy testing is.
