import wx
import os
import json
from MainAdapterPanel import MainAdapterPanel
from MainWireListPanel import MainWireListPanel

########################################################################
class MyPanel(wx.Panel):
    """"""
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.directory = {}
        self.directory["adapter"] = "data/adapter"
        self.directory["modules"] = "data/modules"
        for d in self.directory.values():
            if not os.path.exists(d):
                os.makedirs(d)

        self.number_of_buttons = 0
        self.active_panel = "main"
        self.frame = parent

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.widgetSizer = wx.BoxSizer(wx.VERTICAL)

        self.btnAdptPanel = wx.BitmapButton(self, bitmap=wx.Bitmap("Adapter.png"))
        self.btnAdptPanel.Bind(wx.EVT_BUTTON, self.onAdptPanelSwitch)
        controlSizer.Add(self.btnAdptPanel, 0, wx.CENTER, 0)

        self.btnWireListPanel = wx.BitmapButton(self, bitmap=wx.Bitmap("WireList.png"))
        self.btnWireListPanel.Bind(wx.EVT_BUTTON, self.onWireListPanelSwitch)
        controlSizer.Add(self.btnWireListPanel, 0, wx.CENTER, 0)

        self.removeButton = wx.Button(self,  wx.ID_ANY,"Remove")
        self.removeButton.Bind(wx.EVT_BUTTON, self.onRemoveWidget)
        controlSizer.Add(self.removeButton, 0, wx.CENTER, 0)

        self.mainSizer.Add(controlSizer, 0, wx.CENTER,0)
        self.mainSizer.Add(wx.StaticLine(self, wx.ID_ANY), 0, wx.EXPAND, 0)
        self.mainSizer.Add(self.widgetSizer, 0, wx.CENTER|wx.ALL, 10)

        self.SetSizer(self.mainSizer)

    #----------------------------------------------------------------------
    def onAdptPanelSwitch(self, event):
        """"""
        self.onRemoveWidget(event)
        self.pnlAdapterAssignment = MainAdapterPanel(self)
        self.widgetSizer.Add(self.pnlAdapterAssignment, 0, wx.ALL, 5)
        self.frame.fSizer.Layout()
        self.frame.Fit()

    #----------------------------------------------------------------------
    def onWireListPanelSwitch(self, event):
        """"""
        self.onRemoveWidget(event)
        self.pnlWireList = MainWireListPanel(self)
        self.widgetSizer.Add(self.pnlWireList, 0, wx.ALL, 5)
        self.frame.fSizer.Layout()
        self.frame.Fit()

    def onRemoveWidget(self, event):
        """"""
        children = len(self.widgetSizer.GetChildren())

        if children > 0:
            for i in range( children ):
                self.widgetSizer.Hide(i)
                self.widgetSizer.Remove(i)

            self.frame.fSizer.Layout()
            self.frame.Fit()
        self.active_panel = ""

########################################################################
class MyFrame(wx.Frame):
    """"""
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, parent=None, title="WireSuite")
        self.fSizer = wx.BoxSizer(wx.VERTICAL)
        panel = MyPanel(self)
        self.fSizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(self.fSizer)
        self.Fit()
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop()