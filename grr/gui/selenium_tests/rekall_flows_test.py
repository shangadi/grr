#!/usr/bin/env python
"""Test the Rekall flows-related UI."""

import unittest
from grr.gui import gui_test_lib
from grr.lib import flags
from grr.server.grr_response_server.flows.general import memory
from grr.test_lib import db_test_lib
from grr.test_lib import test_lib


@db_test_lib.DualDBTest
class TestRekallFlows(gui_test_lib.GRRSeleniumTest):
  """Tests the Rekall flows UI."""

  def setUp(self):
    super(TestRekallFlows, self).setUp()
    self.client_id = self.SetupClient(0).Basename()
    self.RequestAndGrantClientApproval(self.client_id)

  def testRekallFlowsAreShownInDebugUIByDefault(self):
    self.Open("/#/clients/%s/launch-flow" % self.client_id)

    self.Click("css=#_Memory")
    self.Click("css=#_Filesystem")
    # Make sure that there's no race by clicking on 2 categories and
    # checking that we actually see the items from the second category.
    self.WaitUntil(self.IsElementPresent, "css=a:contains('File Finder')")
    self.WaitUntilNot(self.IsElementPresent,
                      "css=a:contains('AnalyzeClientMemory')")

    # Open settings dialog and change mode from BASIC to ADVANCED
    self.Click("css=grr-user-settings-button")
    self.Select("css=.form-group:has(label:contains('Mode')) select", "DEBUG")
    self.Click("css=button[name=Proceed]")

    # Try again. AnalyzeClientMemory should be visible now.
    self.Click("css=#_Memory")
    self.WaitUntil(self.IsElementPresent,
                   "css=a:contains('AnalyzeClientMemory')")

  def testRekallFlowsAreShownInBasicUIWhenRekallIsEnabled(self):
    with test_lib.ConfigOverrider({"Rekall.enabled": True}):
      memory.MemoryFlowsInit().RunOnce()

    try:
      self.Open("/#/clients/%s/launch-flow" % self.client_id)

      self.Click("css=#_Memory")
      self.WaitUntilNot(self.IsElementPresent,
                        "css=a:contains('AnalyzeClientMemory')")
    finally:
      memory.MemoryFlowsInit().RunOnce()


def main(argv):
  del argv  # Unused
  unittest.main()


if __name__ == "__main__":
  flags.StartMain(main)
