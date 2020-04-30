import wx
import os
import json
import pandas as pd
from AdapterDialog import AdapterEditorDialog


class MainAdapterPanel(wx.Panel):

    def __init__(self, parent):
        super(MainAdapterPanel, self).__init__(parent)
        parent.active_panel = "Adapter"
        self.directory = parent.directory

        self.nModules = 6
        self.readAdapterList()

        adptAssignSizer = wx.BoxSizer(wx.HORIZONTAL)

        adptSelectSizer = wx.BoxSizer(wx.VERTICAL)
        adptAssignSizer.Add(adptSelectSizer, 1, wx.EXPAND, 0)

        self.sctrlAdapter = wx.SearchCtrl(self, wx.ID_ANY, "")
        self.sctrlAdapter.SetMinSize((180, 25))
        self.sctrlAdapter.ShowCancelButton(True)
        adptSelectSizer.Add(self.sctrlAdapter, 0,
                            wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.lbAdptChoices = wx.ListBox(self, wx.ID_ANY,
                                        choices=self.adptList,
                                        style=wx.LB_SINGLE | wx.LB_SORT)
        self.lbAdptChoices.SetMinSize((180, 150))
        adptSelectSizer.Add(self.lbAdptChoices, 0,
                            wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnNewAdpt = wx.Button(self, wx.ID_ANY, "Neuer Adapter")
        self.btnNewAdpt.SetMinSize((140, 21))
        adptSelectSizer.Add(self.btnNewAdpt, 0,
                            wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnEditAdpt = wx.Button(self, wx.ID_ANY, "Adapter bearbeiten")
        self.btnEditAdpt.SetMinSize((140, 21))
        self.btnEditAdpt.Disable()
        adptSelectSizer.Add(self.btnEditAdpt, 0,
                            wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT, 5)

        self.btnDeleteAdpt = wx.Button(self, wx.ID_ANY, u"Adapter löschen")
        self.btnDeleteAdpt.SetMinSize((140, 21))
        self.btnDeleteAdpt.Disable()
        adptSelectSizer.Add(self.btnDeleteAdpt, 0,
                            wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT, 5)

        adptInfoSizer = wx.BoxSizer(wx.VERTICAL)
        adptAssignSizer.Add(adptInfoSizer, 1, wx.EXPAND, 0)

        adptInfoSizer.Add((-1, 35))

        self.lboxAdptInfo = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.lboxAdptInfo.SetMinSize((150, 150))
        adptInfoSizer.Add(self.lboxAdptInfo, 0,
                          wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        mdlAsgnSizer = wx.BoxSizer(wx.VERTICAL)
        adptAssignSizer.Add(mdlAsgnSizer, 1, wx.EXPAND, 0)

        mdlAsgnSizer.Add((-1, 35))

        lcStyle = wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
        self.lcMdlAsgn = wx.ListCtrl(self, wx.ID_ANY, style=lcStyle)
        self.lcMdlAsgn.SetMinSize((180, 150))
        self.lcMdlAsgn.AppendColumn("Modul", format=wx.LIST_FORMAT_LEFT,
                                    width=90)
        self.lcMdlAsgn.AppendColumn("Adapter", format=wx.LIST_FORMAT_LEFT,
                                    width=90)
        self.readModuleSetting()
        mdlAsgnSizer.Add(self.lcMdlAsgn, 0,
                         wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnAssignAdpt = wx.Button(self, wx.ID_ANY, "Adapter zuweisen")
        self.btnAssignAdpt.SetMinSize((160, 21))
        mdlAsgnSizer.Add(self.btnAssignAdpt, 0,
                         wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)
        self.btnAssignAdpt.Disable()

        self.btnRemoveAsgn = wx.Button(self, wx.ID_ANY,
                                       "Zuweisungen entfernen")
        self.btnRemoveAsgn.SetMinSize((160, 21))
        mdlAsgnSizer.Add(self.btnRemoveAsgn, 0,
                         wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT, 5)

        self.SetSizer(adptAssignSizer)

        self.Layout()

        self.sctrlAdapter.Bind(wx.EVT_TEXT, self.onSearchAdpt)
        self.lbAdptChoices.Bind(wx.EVT_LISTBOX, self.onAdptChoiceSelected)
        self.lcMdlAsgn.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onModuleSelected)
        self.btnNewAdpt.Bind(wx.EVT_BUTTON, self.onNewAdptClicked)
        self.btnEditAdpt.Bind(wx.EVT_BUTTON, self.onEditAdptClicked)
        self.btnDeleteAdpt.Bind(wx.EVT_BUTTON, self.onDeleteAdptClicked)
        self.btnRemoveAsgn.Bind(wx.EVT_BUTTON, self.onRemoveAsgnClicked)
        self.btnAssignAdpt.Bind(wx.EVT_BUTTON, self.onAssignAdptClicked)

    def onSearchAdpt(self, event):

        self.lbAdptChoices.Clear()
        self.lboxAdptInfo.Clear()
        self.btnAssignAdpt.Disable()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()
        reducedAdptList = [i for i in self.adptList
                           if self.sctrlAdapter.GetValue() in i]
        self.lbAdptChoices.Set(reducedAdptList)
        self.lbAdptChoices.Update()

    def onAdptChoiceSelected(self, event):

        adptIdx = self.lbAdptChoices.GetSelection()
        selAdapter = self.lbAdptChoices.GetString(adptIdx)
        with open("{adapter}/{file}.adt".format(file=selAdapter,
                                                **self.directory), "r") as FSO:
            adptData = json.load(FSO)

        infoList = []
        for con in adptData.keys():
            infoList.append("{0} / {1}pol.".format(con,
                                                   adptData[con]["nPins"]))

        self.lboxAdptInfo.Clear()
        self.lboxAdptInfo.Set(infoList)
        self.lboxAdptInfo.Update()

        self.btnEditAdpt.Enable()
        self.btnDeleteAdpt.Enable()

        adptIdx = self.lbAdptChoices.GetSelection()
        mdlIdx = self.lcMdlAsgn.GetFirstSelected()
        if adptIdx > -1 and mdlIdx > -1:
            self.btnAssignAdpt.Enable()

    def onModuleSelected(self, event):
        adptIdx = self.lbAdptChoices.GetSelection()
        mdlIdx = self.lcMdlAsgn.GetFirstSelected()
        if adptIdx > -1 and mdlIdx > -1:
            self.btnAssignAdpt.Enable()

    def onNewAdptClicked(self, event):
        self.AdapterEditor = AdapterEditorDialog(self)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()

    def onAdapterEditorClose(self, event):
        self.readAdapterList()
        self.lboxAdptInfo.Clear()
        event.Skip()

    def onEditAdptClicked(self, event):
        adptIdx = self.lbAdptChoices.GetSelection()
        selAdapter = self.lbAdptChoices.GetString(adptIdx)
        self.AdapterEditor = AdapterEditorDialog(self, adptFile=selAdapter)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()

    def onDeleteAdptClicked(self, event):
        adptIdx = self.lbAdptChoices.GetSelection()
        selAdapter = self.lbAdptChoices.GetString(adptIdx)
        msg = 'Really?! Soll Adapter "{0}"'.format(selAdapter)
        msg += 'unwiderruflich gelöscht werden?'
        response = wx.MessageBox(msg, 'Info', wx.YES_NO | wx.ICON_WARNING)
        if response == wx.YES:
            os.remove("{adapter}/{file}.adt".format(file=selAdapter,
                                                    **self.directory))
            self.readAdapterList()

            for row in range(self.lcMdlAsgn.GetItemCount()):
                adapter = self.lcMdlAsgn.GetItem(itemIdx=row, col=1).GetText()
                if selAdapter == adapter:
                    self.lcMdlAsgn.SetItem(row, 1, "")
            self.dumpModuleSetting()

    def onRemoveAsgnClicked(self, event):
        for i in range(self.lcMdlAsgn.GetItemCount()):
            self.lcMdlAsgn.SetItem(i, 1, "")
        self.dumpModuleSetting()
        self.removeAssignedAliases()

    def onAssignAdptClicked(self, event):
        adptIdx = self.lbAdptChoices.GetSelection()
        selAdapter = self.lbAdptChoices.GetString(adptIdx)
        selModul = self.lcMdlAsgn.GetFirstSelected()

        self.lcMdlAsgn.SetItem(selModul, 1, selAdapter)
        self.dumpModuleSetting()
        self.removeAssignedAliases()

    def readAdapterList(self):
        self.adptList = [i.replace(".adt", "")
                         for i in os.listdir(self.directory["adapter"])
                         if ".adt" in i]

        if "lbAdptChoices" in self.__dict__:
            self.lbAdptChoices.Clear()
            self.lbAdptChoices.Set(self.adptList)
            self.lbAdptChoices.Update()
            self.btnEditAdpt.Disable()
            self.btnDeleteAdpt.Disable()

        if "lboxAdptInfo" in self.__dict__:
            self.lboxAdptInfo.Clear()

    def readModuleSetting(self):
        filename = "{modules}/module_setting.mdl".format(**self.directory)
        if os.path.exists(filename):
            with open(filename, "r") as FSO:
                setting = json.load(FSO)
            self.lcMdlAsgn.DeleteAllItems()
            for i, m in enumerate(setting):
                index = self.lcMdlAsgn.InsertItem(i, m)
                self.lcMdlAsgn.SetItem(index, 1, setting[m])
        else:
            self.lcMdlAsgn.DeleteAllItems()
            for i in range(self.nModules):
                self.lcMdlAsgn.InsertItem(i, "Modul {0}".format(i + 1))

    def dumpModuleSetting(self):
        setting = {}
        for row in range(self.lcMdlAsgn.GetItemCount()):
            module = self.lcMdlAsgn.GetItem(itemIdx=row, col=0)
            adapter = self.lcMdlAsgn.GetItem(itemIdx=row, col=1)
            setting[module.GetText()] = adapter.GetText()

        filename = "{modules}/module_setting.mdl".format(**self.directory)
        with open(filename, "w") as FSO:
            json.dump(setting, FSO, indent=2)

    def removeAssignedAliases(self):
        parts = [self.directory["tmp"], "ConnectionAlias", "alias.lst"]
        filename = "/".join(parts)
        if os.path.exists(filename):
            alias = pd.read_pickle(filename)
            alias["adpt"] = ""
            alias.to_pickle(filename)
