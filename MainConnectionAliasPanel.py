import wx



class MainConnectionAliasPanel(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        super(MainConnectionAliasPanel, self).__init__(parent,size=(700,330), *args, **kwds)
        parent.active_panel = "ConnectionAlias"

        self.directory = parent.directory

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.importPanel = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.importPanel, 0, wx.EXPAND, 0)

        importSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnImportConnections = wx.Button(self.importPanel, wx.ID_ANY, u"Kabelbaum auswählen")
        importSizer.Add(self.btnImportConnections, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)

        line = wx.StaticLine(self, wx.ID_ANY)
        mainSizer.Add(line, 0, wx.ALL | wx.EXPAND, 5)

        self.descrPanel = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.descrPanel, 0, 0, 0)

        descrSizer = wx.BoxSizer(wx.HORIZONTAL)

        stAdapter = wx.StaticText(self.descrPanel, wx.ID_ANY, "Adapter")
        stAdapter.SetMinSize((133, 16))
        descrSizer.Add(stAdapter, 0, wx.ALL, 5)

        stWires = wx.StaticText(self.descrPanel, wx.ID_ANY, "Kabelbaum")
        stWires.SetMinSize((133, 16))
        descrSizer.Add(stWires, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.descrSpacer = wx.Panel(self.descrPanel, wx.ID_ANY)
        descrSizer.Add(self.descrSpacer, 1, wx.EXPAND, 0)

        aliasSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(aliasSizer, 1, wx.EXPAND, 0)

        self.lbAdapter = wx.ListBox(self, wx.ID_ANY, choices=[])
        aliasSizer.Add(self.lbAdapter, 0, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.lbWires = wx.ListBox(self, wx.ID_ANY, choices=[])
        aliasSizer.Add(self.lbWires, 0, wx.BOTTOM | wx.EXPAND | wx.RIGHT, 5)

        self.btnAssignAlias = wx.Button(self, wx.ID_ANY, "Alias zuweisen")
        aliasSizer.Add(self.btnAssignAlias, 0, wx.ALIGN_CENTER, 0)

        self.lcAlias = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lcAlias.AppendColumn("Adapter", format=wx.LIST_FORMAT_LEFT, width=150)
        self.lcAlias.AppendColumn("Kabelbaum", format=wx.LIST_FORMAT_LEFT, width=150)
        aliasSizer.Add(self.lcAlias, 1, wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.descrPanel.SetSizer(descrSizer)

        self.importPanel.SetSizer(importSizer)

        self.SetSizer(mainSizer)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onImportWiresClicked, self.btnImportConnections)
        self.Bind(wx.EVT_BUTTON, self.onAssignAliasClicked, self.btnAssignAlias)
        # end wxGlade

    def onImportWiresClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onImportWiresClicked' not implemented!")
        event.Skip()

    def onAssignAliasClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onAssignAliasClicked' not implemented!")
        event.Skip()

# end of class MyFrame

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
