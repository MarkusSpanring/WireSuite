import wx
import os
import json

import pandas as pd


class MainConnectionAliasPanel(wx.Panel):

    def __init__(self, parent, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        super(MainConnectionAliasPanel, self).__init__(parent,
                                                       size=(700, 330),
                                                       *args, **kwds)
        parent.active_panel = "ConnectionAlias"

        self.directory = parent.directory
        self.tmp_folder = "/".join([self.directory["tmp"], "ConnectionAlias"])
        self.adapters = {}
        self.wires = pd.DataFrame([])

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.importPanel = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.importPanel, 0, wx.EXPAND, 0)

        importSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnImportConn = wx.Button(self.importPanel, wx.ID_ANY,
                                       u"Kabelbaum auswählen")
        importSizer.Add(self.btnImportConn, 0,
                        wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.spacerPanel = wx.Panel(self.importPanel, wx.ID_ANY)
        importSizer.Add(self.spacerPanel, 1, wx.EXPAND, 0)

        self.btnCreateTest = wx.Button(self.importPanel, wx.ID_ANY,
                                       u"Prüfliste erstellen")
        importSizer.Add(self.btnCreateTest, 0, wx.LEFT | wx.RIGHT | wx.TOP, 5)

        line = wx.StaticLine(self, wx.ID_ANY)
        mainSizer.Add(line, 0, wx.ALL | wx.EXPAND, 5)

        self.descrPanel = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.descrPanel, 0, 0, 0)

        descrSizer = wx.BoxSizer(wx.HORIZONTAL)

        stAdapter = wx.StaticText(self.descrPanel, wx.ID_ANY, "Adapter")
        stAdapter.SetMinSize((133, 16))
        descrSizer.Add(stAdapter, 0, wx.ALL, 5)

        self.stWires = wx.StaticText(self.descrPanel, wx.ID_ANY, "Kabelbaum")
        self.stWires.SetMinSize((200, 16))
        descrSizer.Add(self.stWires, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.descrSpacer = wx.Panel(self.descrPanel, wx.ID_ANY)
        descrSizer.Add(self.descrSpacer, 1, wx.EXPAND, 0)

        aliasSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(aliasSizer, 1, wx.EXPAND, 0)

        self.lbAdapter = wx.ListBox(self, wx.ID_ANY, choices=[])
        aliasSizer.Add(self.lbAdapter, 0,
                       wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.lbWires = wx.ListBox(self, wx.ID_ANY, choices=[])
        aliasSizer.Add(self.lbWires, 0, wx.BOTTOM | wx.EXPAND | wx.RIGHT, 5)

        centerSizer = wx.BoxSizer(wx.VERTICAL)
        aliasSizer.Add(centerSizer, 1, wx.EXPAND, 0)

        self.centerSpacer = wx.Panel(self, wx.ID_ANY)
        centerSizer.Add(self.centerSpacer, 1, wx.EXPAND, 0)

        self.btnAssignAlias = wx.Button(self, wx.ID_ANY, "Alias zuweisen")
        centerSizer.Add(self.btnAssignAlias, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.btnAssignAlias.Disable()

        lcStyle = wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
        self.lcModules = wx.ListCtrl(self, wx.ID_ANY, style=lcStyle)
        self.lcModules.AppendColumn("Modul", format=wx.LIST_FORMAT_LEFT,
                                    width=60)

        self.lcModules.AppendColumn("Adapter", format=wx.LIST_FORMAT_LEFT,
                                    width=120)

        centerSizer.Add(self.lcModules, 1, wx.EXPAND | wx.BOTTOM, 5)
        self.lcModules.Disable()

        lcStyle = wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
        self.lcAlias = wx.ListCtrl(self, wx.ID_ANY, style=lcStyle)
        self.lcAlias.AppendColumn("Adapter", format=wx.LIST_FORMAT_LEFT,
                                  width=100)

        self.lcAlias.AppendColumn("Kabelbaum", format=wx.LIST_FORMAT_LEFT,
                                  width=150)
        aliasSizer.Add(self.lcAlias, 1,
                       wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        self.descrPanel.SetSizer(descrSizer)

        self.importPanel.SetSizer(importSizer)

        self.SetSizer(mainSizer)

        self.Layout()

        self.btnImportConn.Bind(wx.EVT_BUTTON, self.onImportWiresClicked)
        self.btnCreateTest.Bind(wx.EVT_BUTTON, self.onCreateTestClicked)
        self.btnAssignAlias.Bind(wx.EVT_BUTTON, self.onAssignAliasClicked)
        self.lbAdapter.Bind(wx.EVT_LISTBOX, self.onConnectorSelected)
        self.lbWires.Bind(wx.EVT_LISTBOX, self.onConnectorSelected)

        self.readSetting()

    def onImportWiresClicked(self, event):

        dlg = wx.DirDialog(self, "Kabelbaum auswählen",
                           style=wx.DD_DEFAULT_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            folder = dlg.GetPath()
        else:
            return
        dlg.Destroy()

        self.wires = pd.read_pickle(folder + "/connections.lst")

        if not self.wires.empty:
            parents = self.wires["start_parent"].to_list()
            parents += self.wires["end_parent"].to_list()
            parents = list(set(parents))
            parents.sort()

            self.lbWires.Set(parents)
            self.lbWires.Update()

            self.stWires.SetLabel(folder.split("/")[-1])
            self.btnAssignAlias.Disable()

    def onConnectorSelected(self, event):
        adptIdx = self.lbAdapter.GetSelection()
        wireIdx = self.lbWires.GetSelection()
        if adptIdx != -1 and wireIdx != -1:
            self.btnAssignAlias.Enable()
        else:
            self.btnAssignAlias.Disable()

    def onAssignAliasClicked(self, event):
        adptIdx = self.lbAdapter.GetSelection()
        wireIdx = self.lbWires.GetSelection()
        if adptIdx == -1 or wireIdx == -1:
            return

        self.lcAlias.Append([self.lbAdapter.GetString(adptIdx).split(" / ")[0],
                             self.lbWires.GetString(wireIdx)])

        self.lbWires.Delete(wireIdx)
        if adptIdx > 0:
            self.lbAdapter.Delete(adptIdx)

        adptIdx = self.lbAdapter.GetSelection()
        wireIdx = self.lbWires.GetSelection()
        if adptIdx == -1 or wireIdx == -1:
            self.btnAssignAlias.Disable()

        self.dumpAliasInfo()

    def onCreateTestClicked(self, event):
        print("Event handler 'onCreateTestClicked' not implemented!")
        event.Skip()

    def readSetting(self):
        self.adapters = {}
        modul_path = "{modules}/module_setting.mdl".format(**self.directory)
        if os.path.exists(modul_path):
            with open(modul_path, "r") as FSO:
                module = json.load(FSO)

            self.lcModules.DeleteAllItems()

            for i, m in enumerate(module):
                index = self.lcModules.InsertItem(i, m)
                self.lcModules.SetItem(index, 1, module[m])
                if module[m]:
                    adpt_path = "{adapter}/{file}.adt".format(file=module[m],
                                                              **self.directory)
                    with open(adpt_path, "r") as FSO:
                        self.adapters["M" + str(i + 1)] = json.load(FSO)

            connector_list = []
            alias = self.readAliasInfo()
            for adpt in self.adapters.keys():
                for connector in self.adapters[adpt].keys():
                    if adpt + ":" + connector in alias["adpt"].to_list():
                        continue
                    nPins = self.adapters[adpt][connector]["nPins"]
                    entry = "{0}:{1} / {2} pol.".format(adpt, connector, nPins)
                    connector_list.append(entry)
            connector_list.sort()
            connector_list = [u"Prüfspitze"] + connector_list
            self.lbAdapter.Set(connector_list)
            self.lbAdapter.Update()

            wires = []
            for i, row in alias.iterrows():
                if row["adpt"]:
                    self.lcAlias.Append([row["adpt"], row["wire"]])
                else:
                    wires.append(row["wire"])

            self.lbWires.Set(wires)
            self.lbWires.Update()

    def dumpAliasInfo(self):

        alias = []
        for row in range(self.lcAlias.GetItemCount()):
            adapter = self.lcAlias.GetItem(itemIdx=row, col=0)
            wires = self.lcAlias.GetItem(itemIdx=row, col=1)
            alias.append((adapter.GetText(), wires.GetText()))

        for item in range(self.lbWires.GetCount()):
            alias.append(("", self.lbWires.GetString(item)))

        alias = pd.DataFrame(alias, columns=["adpt", "wire"])
        filename = "/".join([self.tmp_folder, "alias.lst"])
        alias.to_pickle(filename)

    def readAliasInfo(self):
        filename = "/".join([self.tmp_folder, "alias.lst"])
        if not os.path.exists(filename):
            return pd.DataFrame([], columns=["adpt", "wire"])

        return pd.read_pickle(filename)


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainConnectionAliasPanel(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
