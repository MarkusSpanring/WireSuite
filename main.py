import wx
import os
import json
from Adapter import AdapterEditorGUI
from WireListGrid import WireListGrid
from WireListDataFrame import WireListDataFrame
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
        self.pnlAdapterAssignment = AdapterPanel(self)
        self.widgetSizer.Add(self.pnlAdapterAssignment, 0, wx.ALL, 5)
        self.frame.fSizer.Layout()
        self.frame.Fit()

    #----------------------------------------------------------------------
    def onWireListPanelSwitch(self, event):
        """"""
        self.onRemoveWidget(event)
        self.pnlWireList = WireListPanel(self)
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

class AdapterPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        parent.active_panel = "Adapter"
        self.directory = parent.directory
        # self = wx.Panel(self, wx.ID_ANY)

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

        # end wxGlade

    def onSearchAdpt(self, event):  # wxGlade: mainFrame.<event_handler>

        self.lboxAdptChoices.Clear()
        self.lboxAdptInfo.Clear()
        self.btnAssignAdpt.Disable()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()
        reducedAdptList = [i for i in self.adptList if self.sctrlAdapter.GetValue() in i]
        self.lboxAdptChoices.Set(reducedAdptList)
        self.lboxAdptChoices.Update()

    def onAdptChoiceSelected(self, event):  # wxGlade: mainFrame.<event_handler>

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

    def onNewAdptClicked(self, event):  # wxGlade: mainFrame.<event_handler>
        self.AdapterEditor = AdapterEditorGUI(self)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()
        # print("Event handler 'onNewAdptClicked' not implemented!")
        # event.Skip()

    def onAdapterEditorClose(self,event):
        self.readAdapterList()
        self.lboxAdptInfo.Clear()
        event.Skip()

    def onEditAdptClicked(self, event):  # wxGlade: mainFrame.<event_handler>
        selAdapter = self.lboxAdptChoices.GetString(self.lboxAdptChoices.GetSelection())
        self.AdapterEditor = AdapterEditorGUI(self,adptSetting=selAdapter)
        self.AdapterEditor.Bind(wx.EVT_CLOSE, self.onAdapterEditorClose)
        self.AdapterEditor.Show()
        self.btnEditAdpt.Disable()
        self.btnDeleteAdpt.Disable()

    def onDeleteAdptClicked(self, event):  # wxGlade: mainFrame.<event_handler>
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

    def onRemoveAssignClicked(self, event):  # wxGlade: mainFrame.<event_handler>
        for i in range(self.lctrlModulAssignment.GetItemCount() ):
            self.lctrlModulAssignment.SetItem(i,1, "" )
        self.dumpModuleSetting()

    def onAssignAdptClicked(self, event):  # wxGlade: mainFrame.<event_handler>
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

class WireListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent,size=(850,600))
        parent.active_panel = "WireList"

        self.wlDataFrame = WireListDataFrame()

        vboxMain = wx.BoxSizer(wx.VERTICAL)

        self.btnImportExcel = wx.Button(self, wx.ID_ANY, "Von Excel Importieren")
        vboxMain.Add(self.btnImportExcel, 0, wx.ALL, 5)

        self.btnImportPDF = wx.Button(self, wx.ID_ANY, "Von PDF Importieren")
        vboxMain.Add(self.btnImportPDF, 0, wx.ALL, 5)

        self.wireList = WireListGrid(self)
        vboxMain.Add(self.wireList, 1, wx.ALL | wx.EXPAND, 5)

        hboxBottom = wx.BoxSizer(wx.HORIZONTAL)
        vboxMain.Add(hboxBottom, 0, wx.ALIGN_CENTER | wx.EXPAND, 0)

        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        hboxBottom.Add(sizer_5, 1, wx.EXPAND, 0)

        self.rbSortOptions = wx.RadioBox(self, wx.ID_ANY, "", choices=["Rohdaten", "Sortiert", u"Sortiert mit Überschrift"], majorDimension=3, style=wx.RA_SPECIFY_ROWS)
        self.rbSortOptions.SetSelection(0)
        sizer_5.Add(self.rbSortOptions, 0, 0, 0)

        self.spacerPanel = wx.Panel(self, wx.ID_ANY)
        hboxBottom.Add(self.spacerPanel, 1, wx.EXPAND, 0)

        self.tcFilename = wx.TextCtrl(self, wx.ID_ANY, "")
        self.tcFilename.SetMinSize((200, 22))
        hboxBottom.Add(self.tcFilename, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.btnExport = wx.Button(self, wx.ID_ANY, "Exportieren")
        hboxBottom.Add(self.btnExport, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(vboxMain)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onImportExcelClicked, self.btnImportExcel)
        self.Bind(wx.EVT_BUTTON, self.onImportPDFClicked, self.btnImportPDF)
        self.Bind(wx.EVT_RADIOBOX, self.onSortOptionSelected, self.rbSortOptions)
        self.Bind(wx.EVT_BUTTON, self.onExportClicked, self.btnExport)
        # end wxGlade

    def onImportExcelClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        openFileDialog = wx.FileDialog(frame, "Öffnen", "", "", "Excel Dateien (*.xlsx)|*.xlsx", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.wlDataFrame.set_dataframe_from_excel(openFileDialog.GetPath())
        self.wireList.set_from_dataframe( self.wlDataFrame.get_dataframe() )
        self.rbSortOptions.SetSelection(0)

    def onImportPDFClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onImportPDFClicked' not implemented!")
        event.Skip()

    def onSortOptionSelected(self, event):  # wxGlade: MyFrame.<event_handler>

        print( self.rbSortOptions.GetSelection())
        print("Event handler 'onSortOptionSelected' not implemented!")
        event.Skip()

    def onExportClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onExportClicked' not implemented!")
        event.Skip()

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