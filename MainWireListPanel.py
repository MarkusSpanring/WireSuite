import wx
import os

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

        self.openedFile = ""

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

        self.btnExport = wx.Button(self.panelBkg, wx.ID_ANY, "Exportieren")
        controlSizer.Add(self.btnExport, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitWindow.SetMinimumPaneSize(20)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)

        self.topPanel = wx.lib.scrolledpanel.ScrolledPanel(self.splitWindow, wx.ID_ANY)
        self.topPanel.SetMinSize((-1, 20))
        mainSizer.Add(self.topPanel, 1, wx.EXPAND, 0)

        bmpSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.bmpSideView = wx.StaticBitmap(self.topPanel, wx.ID_ANY, wx.Bitmap(wx.Image(1,1) ))

        bmpSizer.Add(self.bmpSideView, 0, 0, 0)

        self.bottomPanel = wx.Panel(self.splitWindow, wx.ID_ANY)

        gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        # mainSizer.Add(gridSizer, 1, wx.EXPAND, 0)

        self.switchPanel = wx.Panel(self.bottomPanel, wx.ID_ANY, style=wx.BORDER_RAISED)
        self.switchPanel.SetMinSize((150, 715))
        gridSizer.Add(self.switchPanel, 0, wx.EXPAND | wx.ALL, 5)

        switchSizer = wx.BoxSizer(wx.VERTICAL)

        self.btnSort = wx.Button(self.switchPanel, wx.ID_ANY, "Sortieren")
        switchSizer.Add(self.btnSort, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.btnSwitch = wx.Button(self.switchPanel, wx.ID_ANY, "Tauschen")
        switchSizer.Add(self.btnSwitch, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        self.connectionBox = wx.ListCtrl(self.switchPanel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.connectionBox.SetMinSize((150, 658))
        self.connectionBox.AppendColumn("von", format=wx.LIST_FORMAT_LEFT, width=72)
        self.connectionBox.AppendColumn("zu", format=wx.LIST_FORMAT_LEFT, width=72)
        switchSizer.Add(self.connectionBox, 0, wx.EXPAND, 0)

        self.wlGrid = WireListGrid(self.bottomPanel)
        gridSizer.Add(self.wlGrid, 1, wx.ALL | wx.EXPAND, 5)

        self.switchPanel.SetSizer(switchSizer)

        self.bottomPanel.SetSizer(gridSizer)

        self.topPanel.SetSizer(bmpSizer)

        self.splitWindow.SplitHorizontally(self.topPanel, self.bottomPanel, 1)

        self.panelBkg.SetSizer(controlSizer)

        self.SetSizer(mainSizer)

        self.Layout()

        self.Bind(wx.EVT_BUTTON, self.onImportExcelClicked, self.btnImportExcel)
        self.Bind(wx.EVT_BUTTON, self.onImportPDFClicked, self.btnImportPDF)
        self.Bind(wx.EVT_BUTTON, self.onExportClicked, self.btnExport)
        self.Bind(wx.EVT_BUTTON, self.onSortClicked, self.btnSort)
        self.Bind(wx.EVT_BUTTON, self.onSwitchClicked, self.btnSwitch)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSwitchClicked, self.connectionBox)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onConnectionSelected, self.connectionBox)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onConnectionDeselected, self.connectionBox)

    def onImportExcelClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        openFileDialog = wx.FileDialog(self, "Öffnen", "", "", "Excel Dateien (*.xlsx)|*.xlsx",
                                              wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        excelfile = openFileDialog.GetPath()
        self.openedFile = self.getFilename(excelfile)
        self.wlDataFrame.set_dataframe_from_excel( excelfile )
        self.wlGrid.set_from_dataframe( self.wlDataFrame.get_dataframe() )
        self.wlGrid.ClearSelection()

    def onImportPDFClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        self.pdfimporter = PDFToDataFrameDialog(self.panelBkg)
        self.pdfimporter.Bind(wx.EVT_CLOSE, self.onPDFImporterClose)
        self.pdfimporter.ShowModal()
        self.wlGrid.ClearSelection()

    def onPDFImporterClose(self, event):
        self.bmpSideView.SetBitmap( self.pdfimporter.getImage() )
        self.openedFile = self.getFilename( self.pdfimporter.getPDFPath() )
        self.topPanel.SetupScrolling()
        self.wlGrid.set_from_dataframe( self.pdfimporter.getData() )

        event.Skip()

    def onSortClicked(self, event):  # wxGlade: MainWireListPanel.<event_haneventdler>
        self.onConnectionDeselected(event)
        self.wlGrid.ClearSelection()
        data = self.wlGrid.get_dataframe()
        if data.empty:
            return
        self.wlDataFrame.set_dataframe( data )

        if self.connectionBox.GetItemCount() == 0:
            self.wlGrid.set_from_dataframe(  self.wlDataFrame.get_dataframe(sort_rows=True) )
            self.fillConnectionBox()

        else:
            connections = []
            for row in range(self.connectionBox.GetItemCount() ):
                start = self.connectionBox.GetItem(itemIdx=row, col=0).GetText()
                end = self.connectionBox.GetItem(itemIdx=row, col=1).GetText()
                connections.append( (start,end) )

            self.wlDataFrame.reorder_endpoints(connections)
            self.wlGrid.set_from_dataframe(  self.wlDataFrame.get_dataframe(sort_rows=True) )
            self.fillConnectionBox()
        self.wlGrid.ClearSelection()

    def onSwitchClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        row = self.connectionBox.GetFirstSelected()
        if row == -1:
            return

        start = self.connectionBox.GetItem(itemIdx=row, col=0).GetText()
        end = self.connectionBox.GetItem(itemIdx=row, col=1).GetText()

        self.connectionBox.SetItem(row, 0, end )
        self.connectionBox.SetItem(row, 1, start )

    def onExportClicked(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        dlg = wx.FileDialog(self, "Drahtliste speichern unter:", ".", self.openedFile, "Ordner", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            print( dlg.GetPath() )
        dlg.Destroy()

    def onConnectionSelected(self, event):  # wxGlade: MainWireListPanel.<event_handler>
        itemIdx = self.connectionBox.GetFirstSelected()
        start = self.connectionBox.GetItem(itemIdx=itemIdx, col=0).GetText()
        end = self.connectionBox.GetItem(itemIdx=itemIdx, col=1).GetText()

        #Thats a bit of an overhead. Maybe use wlDF as wlGrid datatype
        self.wlDataFrame.set_dataframe( self.wlGrid.get_dataframe() )

        rows = self.wlDataFrame.find_connections(start, end)
        for row in rows:
            for col in range( self.wlGrid.GetNumberCols() ):
                self.wlGrid.SetCellBackgroundColour(row,col, "light blue")

        self.wlGrid.ForceRefresh()

    def onConnectionDeselected(self, event):
        #There should be a function to colour all at once somewhere....
        for row in range(self.wlGrid.GetNumberRows()):
            for col in range( self.wlGrid.GetNumberCols() ):
                self.wlGrid.SetCellBackgroundColour( row,col, "white")

        self.wlGrid.ForceRefresh()

    def fillConnectionBox(self):
        self.connectionBox.DeleteAllItems()

        for i, (start,end) in enumerate(self.wlDataFrame.connections):
            index = self.connectionBox.InsertItem(i, start)
            self.connectionBox.SetItem(index, 1, end )

    def getFilename(self,path):
        filename = os.path.basename( path )
        return os.path.splitext(filename)[0]

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
