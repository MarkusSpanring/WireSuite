import wx
import os
import json
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
        adptSelectSizer.Add(self.sctrlAdapter, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.lboxAdptChoices = wx.ListBox(self, wx.ID_ANY,
                                          choices=self.adptList,
                                          style=wx.LB_SINGLE | wx.LB_SORT)
        self.lboxAdptChoices.SetMinSize((180, 150))
        adptSelectSizer.Add(self.lboxAdptChoices, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnNewAdpt = wx.Button(self, wx.ID_ANY, "Neuer Adapter")
        self.btnNewAdpt.SetMinSize((140, 21))
        adptSelectSizer.Add(self.btnNewAdpt, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnEditAdpt = wx.Button(self, wx.ID_ANY, "Adapter bearbeiten")
        self.btnEditAdpt.SetMinSize((140, 21))
        self.btnEditAdpt.Disable()
        adptSelectSizer.Add(self.btnEditAdpt, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT, 5)

        self.btnDeleteAdpt = wx.Button(self, wx.ID_ANY, u"Adapter löschen")
        self.btnDeleteAdpt.SetMinSize((140, 21))
        self.btnDeleteAdpt.Disable()
        adptSelectSizer.Add(self.btnDeleteAdpt, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT, 5)

        adptInfoSizer = wx.BoxSizer(wx.VERTICAL)
        adptAssignSizer.Add(adptInfoSizer, 1, wx.EXPAND, 0)

        adptInfoSizer.Add((-1, 35))

        self.lboxAdptInfo = wx.ListBox(self, wx.ID_ANY, choices=[])
        self.lboxAdptInfo.SetMinSize((150, 150))
        adptInfoSizer.Add(self.lboxAdptInfo, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        modulAssignSizer = wx.BoxSizer(wx.VERTICAL)
        adptAssignSizer.Add(modulAssignSizer, 1, wx.EXPAND, 0)

        modulAssignSizer.Add((-1, 35))

        self.lctrlModulAssignment = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.lctrlModulAssignment.SetMinSize((180, 150))
        self.lctrlModulAssignment.AppendColumn("Modul", format=wx.LIST_FORMAT_LEFT, width=90)
        self.lctrlModulAssignment.AppendColumn("Adapter", format=wx.LIST_FORMAT_LEFT, width=90)
        self.readModuleSetting()
        modulAssignSizer.Add(self.lctrlModulAssignment, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP, 5)

        self.btnAssignAdpt = wx.Button(self, wx.ID_ANY, "Adapter zuweisen")
        self.btnAssignAdpt.SetMinSize((160, 21))
        modulAssignSizer.Add(self.btnAssignAdpt, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT | wx.TOP , 5)
        self.btnAssignAdpt.Disable()

        self.btnRemoveAssignments = wx.Button(self, wx.ID_ANY, "Zuweisungen entfernen")
        self.btnRemoveAssignments.SetMinSize((160, 21))
        modulAssignSizer.Add(self.btnRemoveAssignments, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.RIGHT,  5)

        self.SetSizer(adptAssignSizer)

        self.Layout()

        self.Bind(wx.EVT_TEXT, self.onSearchAdpt, self.sctrlAdapter)
        self.Bind(wx.EVT_LISTBOX, self.onAdptChoiceSelected, self.lboxAdptChoices)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onModuleChoiceSelected, self.lctrlModulAssignment)
        self.Bind(wx.EVT_BUTTON, self.onNewAdptClicked, self.btnNewAdpt)
        self.Bind(wx.EVT_BUTTON, self.onEditAdptClicked, self.btnEditAdpt)
        self.Bind(wx.EVT_BUTTON, self.onDeleteAdptClicked, self.btnDeleteAdpt)
        self.Bind(wx.EVT_BUTTON, self.onRemoveAssignClicked, self.btnRemoveAssignments)
        self.Bind(wx.EVT_BUTTON, self.onAssignAdptClicked, self.btnAssignAdpt)

    def onSearchAdpt(self, event):

        self.lboxAdptChoices.Clear()
        self.lboxAdptInfo.Clear()
        self.btnAssignAdpt.Disable()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()
        reducedAdptList = [i for i in self.adptList if self.sctrlAdapter.GetValue() in i]
        self.lboxAdptChoices.Set(reducedAdptList)
        self.lboxAdptChoices.Update()

    def onAdptChoiceSelected(self, event):

        selAdapter = self.lboxAdptChoices.GetString(self.lboxAdptChoices.GetSelection())
        with open("{adapter}/{file}.adt".format(file=selAdapter,**self.directory), "r") as FSO:
            adptData = json.load(FSO)

        infoList = []
        for connector in adptData.keys():
            infoList.append("{0} / {1}pol.".format(connector, adptData[connector]["nPins"]))

        self.lboxAdptInfo.Clear()
        self.lboxAdptInfo.Set(infoList)
        self.lboxAdptInfo.Update()

        self.btnEditAdpt.Enable()
        self.btnDeleteAdpt.Enable()

        if self.lboxAdptChoices.GetSelection() > -1 and self.lctrlModulAssignment.GetFirstSelected() > -1:
            self.btnAssignAdpt.Enable()

    def onModuleChoiceSelected(self, event):
        if self.lboxAdptChoices.GetSelection() > -1 and self.lctrlModulAssignment.GetFirstSelected() > -1:
            self.btnAssignAdpt.Enable()

    def onNewAdptClicked(self, event):
        self.AdapterEditor = AdapterEditorDialog(self)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()

    def onAdapterEditorClose(self,event):
        self.readAdapterList()
        self.lboxAdptInfo.Clear()
        event.Skip()

    def onEditAdptClicked(self, event):
        selAdapter = self.lboxAdptChoices.GetString(self.lboxAdptChoices.GetSelection())
        self.AdapterEditor = AdapterEditorDialog(self,adptSetting=selAdapter)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()

    def onDeleteAdptClicked(self, event):
        selAdapter = self.lboxAdptChoices.GetString(self.lboxAdptChoices.GetSelection())
        response = wx.MessageBox('Really?! Soll Adapter "{0}" unwiderruflich gelöscht werden?'.format(selAdapter),
                                 'Info', wx.YES_NO | wx.ICON_WARNING)
        if response == wx.YES:
            os.remove( "{adapter}/{file}.adt".format(file=selAdapter,**self.directory) )
            self.readAdapterList()

            for row in range(self.lctrlModulAssignment.GetItemCount() ):
                adapter = self.lctrlModulAssignment.GetItem(itemIdx=row, col=1).GetText()
                if selAdapter == adapter:
                    self.lctrlModulAssignment.SetItem(row,1, "" )
            self.dumpModuleSetting()

    def onRemoveAssignClicked(self, event):
        for i in range(self.lctrlModulAssignment.GetItemCount() ):
            self.lctrlModulAssignment.SetItem(i,1, "" )
        self.dumpModuleSetting()

    def onAssignAdptClicked(self, event):
        selAdapter = self.lboxAdptChoices.GetString(self.lboxAdptChoices.GetSelection())
        selModul = self.lctrlModulAssignment.GetFirstSelected()

        self.lctrlModulAssignment.SetItem(selModul,1, selAdapter )
        self.dumpModuleSetting()

    def readAdapterList(self):
        self.adptList = [i.replace(".adt","") for i in os.listdir(self.directory["adapter"]) if ".adt" in i]
        if "lboxAdptChoices" in self.__dict__:
            self.lboxAdptChoices.Clear()
            self.lboxAdptChoices.Set(self.adptList)
            self.lboxAdptChoices.Update()
            self.btnEditAdpt.Disable()
            self.btnDeleteAdpt.Disable()

        if "lboxAdptInfo" in self.__dict__:
            self.lboxAdptInfo.Clear()

    def readModuleSetting(self):
        if os.path.exists("{modules}/module_setting.mdl".format(**self.directory)):
            with open("{modules}/module_setting.mdl".format(**self.directory), "r") as FSO:
                setting = json.load(FSO)
            self.lctrlModulAssignment.DeleteAllItems()
            for i,m in enumerate(setting):
                index = self.lctrlModulAssignment.InsertItem(i, m )
                self.lctrlModulAssignment.SetItem(index, 1, setting[m] )
        else:
            self.lctrlModulAssignment.DeleteAllItems()
            for i in range(self.nModules):
                self.lctrlModulAssignment.InsertItem(i, "Modul {0}".format(i+1) )

    def dumpModuleSetting(self):
        setting = {}
        for row in range(self.lctrlModulAssignment.GetItemCount() ):
            module = self.lctrlModulAssignment.GetItem(itemIdx=row, col=0)
            adapter = self.lctrlModulAssignment.GetItem(itemIdx=row, col=1)
            setting[module.GetText()] = adapter.GetText()

        with open("{modules}/module_setting.mdl".format(**self.directory),"w") as FSO:
            json.dump(setting, FSO, indent=2)