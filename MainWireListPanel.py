import wx

import wx.lib.scrolledpanel as scrolled

from WireListGrid import WireListGrid
from WireListDataFrame import WireListDataFrame
from PDFToDataFrameDialog import PDFToDataFrameDialog



class MainWireListPanel(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        # begin wxGlade: MainWireListPanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        super(MainWireListPanel, self).__init__(parent,size=(1000,600), *args, **kwds)
        parent.active_panel = "WireList"

        self.wlDataFrame = WireListDataFrame()

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.panelBkg = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.panelBkg, 0, wx.EXPAND, 0)

        controlSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnImportExcel = wx.Button(self.panelBkg, wx.ID_ANY, "Excel importieren")
        controlSizer.Add(self.btnImportExcel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.btnImportPDF = wx.Button(self.panelBkg, wx.ID_ANY, "PDF importieren")
        controlSizer.Add(self.btnImportPDF, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.spacerPanelLeft = wx.Panel(self.panelBkg, wx.ID_ANY)
        controlSizer.Add(self.spacerPanelLeft, 1, wx.EXPAND, 0)

        self.lbStartParent = wx.ListBox(self.panelBkg, wx.ID_ANY, choices=[])
        self.lbStartParent.SetMinSize((133, 90))
        controlSizer.Add(self.lbStartParent, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        btnSizer = wx.BoxSizer(wx.VERTICAL)
        controlSizer.Add(btnSizer, 0, wx.ALIGN_CENTER, 0)

        self.btnSort = wx.Button(self.panelBkg, wx.ID_ANY, "button_7")
        btnSizer.Add(self.btnSort, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.btnMoveToStart = wx.Button(self.panelBkg, wx.ID_ANY, "<<")
        btnSizer.Add(self.btnMoveToStart, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.btnMoveToEnd = wx.Button(self.panelBkg, wx.ID_ANY, ">>")
        btnSizer.Add(self.btnMoveToEnd, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.lbEndParent = wx.ListBox(self.panelBkg, wx.ID_ANY, choices=[])
        self.lbEndParent.SetMinSize((133, 90))
        controlSizer.Add(self.lbEndParent, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.spacerPanelRight = wx.Panel(self.panelBkg, wx.ID_ANY)
        controlSizer.Add(self.spacerPanelRight, 1, wx.EXPAND, 0)

        self.txtExportName = wx.TextCtrl(self.panelBkg, wx.ID_ANY, "")
        self.txtExportName.SetMinSize((150, 22))
        controlSizer.Add(self.txtExportName, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.btnExport = wx.Button(self.panelBkg, wx.ID_ANY, "Exportieren")
        controlSizer.Add(self.btnExport, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitWindow.SetMinSize((1200, 600))
        self.splitWindow.SetMinimumPaneSize(20)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)

        self.splitWindowP1 = scrolled.ScrolledPanel(self.splitWindow)
        self.splitWindowP1.SetupScrolling()
        # self.splitWindowP1 = wx.Panel(self.splitWindow, wx.ID_ANY)
        self.splitWindowP1.SetMinSize((20, 600))

        leftSizer = wx.BoxSizer(wx.VERTICAL)

        img = wx.Image(1,1,clear=True)
        self.bmpSideView = wx.StaticBitmap(self.splitWindowP1, wx.ID_ANY, wx.Bitmap(img))
        leftSizer.Add(self.bmpSideView, 0, 0, 0)

        self.splitWindowP2 = wx.Panel(self.splitWindow, wx.ID_ANY)

        rightSizer = wx.BoxSizer(wx.VERTICAL)

        self.wireList = WireListGrid(self.splitWindowP2)
        rightSizer.Add(self.wireList, 1, wx.ALL | wx.EXPAND, 5)

        self.splitWindowP2.SetSizer(rightSizer)

        self.splitWindowP1.SetSizer(leftSizer)

        self.splitWindow.SplitVertically(self.splitWindowP1, self.splitWindowP2)

        self.panelBkg.SetSizer(controlSizer)

        self.SetSizer(mainSizer)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onImportExcelClicked, self.btnImportExcel)
        self.Bind(wx.EVT_BUTTON, self.onImportPDFClicked, self.btnImportPDF)
        self.Bind(wx.EVT_BUTTON, self.onSortClicked, self.btnSort)
        self.Bind(wx.EVT_BUTTON, self.onMoveStartClicked, self.btnMoveToStart)
        self.Bind(wx.EVT_BUTTON, self.onMoveEndClicked, self.btnMoveToEnd)
        self.Bind(wx.EVT_BUTTON, self.onExportClicked, self.btnExport)
        # self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.onSplitterMoved, self.splitWindow)
        # end wxGlade

    def onImportExcelClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        openFileDialog = wx.FileDialog(self, "Öffnen", "", "", "Excel Dateien (*.xlsx)|*.xlsx",
                                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.wlDataFrame.set_dataframe_from_excel(openFileDialog.GetPath())
        self.wireList.set_from_dataframe( self.wlDataFrame.get_dataframe() )

    def onImportPDFClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        self.pdfimporter = PDFToDataFrameDialog(self.panelBkg)
        self.pdfimporter.Bind(wx.EVT_CLOSE, self.onPDFImporterClose)
        self.pdfimporter.ShowModal()

    def onPDFImporterClose(self, event):

        self.bmpSideView.SetBitmap( self.pdfimporter.getImage() )
        self.wireList.set_from_dataframe( self.pdfimporter.getData() )
        event.Skip()

    def onSortClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        print("Event handler 'onSortClicked' not implemented!")
        event.Skip()

    def onMoveStartClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        print("Event handler 'onMoveStartClicked' not implemented!")
        event.Skip()

    def onMoveEndClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        print("Event handler 'onMoveEndClicked' not implemented!")
        event.Skip()

    def onExportClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        print("Event handler 'onExportClicked' not implemented!")
        event.Skip()

    def onSplitterMoved(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        print("Event handler 'onSplitterMoved' not implemented!")
        event.Skip()

# end of class MainWireListPanel

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWireListPanel(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

# end of class MyApp

if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
