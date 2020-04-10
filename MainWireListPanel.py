import wx

from WireListGrid import WireListGrid
from WireListDataFrame import WireListDataFrame
from PDFToDataFrameGUI import PDFToDataFrameGUI


class MainWireListPanel(wx.Panel):

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent,size=(1000,600))
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

        choices = ["Rohdaten", "Sortiert", u"Sortiert mit Überschrift"]
        self.rbSortOptions = wx.RadioBox(self, wx.ID_ANY, "", choices=choices,
                                                              majorDimension=3,
                                                              style=wx.RA_SPECIFY_ROWS)
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
    
        openFileDialog = wx.FileDialog(self, "Öffnen", "", "", "Excel Dateien (*.xlsx)|*.xlsx",
                                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.wlDataFrame.set_dataframe_from_excel(openFileDialog.GetPath())
        self.wireList.set_from_dataframe( self.wlDataFrame.get_dataframe() )
        self.rbSortOptions.SetSelection(0)

    def onImportPDFClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        self.pdfimporter = PDFToDataFrameGUI(self)
        self.pdfimporter.Bind(wx.EVT_CLOSE, self.onPDFImporterClose)
        self.pdfimporter.Show()

    def onPDFImporterClose(self, event):

        self.wireList.set_from_dataframe( self.pdfimporter.getData() )
        event.Skip()

    def onSortOptionSelected(self, event):  # wxGlade: MyFrame.<event_handler>

        print( self.rbSortOptions.GetSelection())
        print("Event handler 'onSortOptionSelected' not implemented!")
        event.Skip()

    def onExportClicked(self, event):  # wxGlade: MyFrame.<event_handler>
        print("Event handler 'onExportClicked' not implemented!")
        event.Skip()