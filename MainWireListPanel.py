import wx
import os
import shutil

import wx.lib.scrolledpanel as scrolled

from WireListGrid import WireListGrid
from WireListDataFrame import WireListDataFrame
from PDFToDataFrameDialog import PDFToDataFrameDialog


class MainWireListPanel(wx.Panel):
    def __init__(self, parent, *args, **kwds):
        # begin wxGlade: MainWireListPanel.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        super(MainWireListPanel, self).__init__(parent,
                                                size=(1000, 600),
                                                *args, **kwds)
        parent.active_panel = "WireList"

        self.directory = parent.directory
        self.openedFile = ""

        self.wlDF = WireListDataFrame()

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.panelBkg = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(self.panelBkg, 0, wx.EXPAND, 0)

        controlSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnImportExcel = wx.Button(self.panelBkg,
                                        wx.ID_ANY, "Excel importieren")
        controlSizer.Add(self.btnImportExcel, 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.btnImportPDF = wx.Button(self.panelBkg,
                                      wx.ID_ANY, "PDF importieren")
        controlSizer.Add(self.btnImportPDF, 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.spacerPanelLeft = wx.Panel(self.panelBkg, wx.ID_ANY)
        controlSizer.Add(self.spacerPanelLeft, 1, wx.EXPAND, 0)

        self.btnExport = wx.Button(self.panelBkg, wx.ID_ANY, "Exportieren")
        controlSizer.Add(self.btnExport, 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.sldZoom = wx.Slider(self, wx.ID_ANY, 50, 0, 100, size=(500, -1))
        mainSizer.Add(self.sldZoom, 0, wx.EXPAND, 0)
        self.sldZoom.Disable()

        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitWindow.SetMinimumPaneSize(20)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)

        self.splitWindow = wx.SplitterWindow(self, wx.ID_ANY)
        self.splitWindow.SetMinimumPaneSize(20)
        mainSizer.Add(self.splitWindow, 1, wx.EXPAND, 0)

        self.topPanel = scrolled.ScrolledPanel(self.splitWindow, wx.ID_ANY)
        self.topPanel.SetMinSize((-1, 20))

        pdfviewSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.sideViewImgPath = ""
        self.bmpSideView = wx.StaticBitmap(self.topPanel, wx.ID_ANY,
                                           wx.Bitmap(wx.Image(1, 1)))
        pdfviewSizer.Add(self.bmpSideView, 0, 0, 0)

        self.bottomPanel = wx.Panel(self.splitWindow, wx.ID_ANY)

        gridSizer = wx.BoxSizer(wx.HORIZONTAL)
        # mainSizer.Add(gridSizer, 1, wx.EXPAND, 0)

        self.switchPanel = wx.Panel(self.bottomPanel, wx.ID_ANY,
                                    style=wx.BORDER_RAISED)
        self.switchPanel.SetMinSize((150, 715))
        gridSizer.Add(self.switchPanel, 0, wx.EXPAND | wx.ALL, 5)

        switchSizer = wx.BoxSizer(wx.VERTICAL)

        self.btnSort = wx.Button(self.switchPanel, wx.ID_ANY, "Sortieren")
        switchSizer.Add(self.btnSort, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.btnSwitch = wx.Button(self.switchPanel, wx.ID_ANY, "Tauschen")
        switchSizer.Add(self.btnSwitch, 0,
                        wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)

        lcStyle = wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES
        self.lcConBox = wx.ListCtrl(self.switchPanel, wx.ID_ANY,
                                    style=lcStyle)
        self.lcConBox.SetMinSize((150, 658))
        self.lcConBox.AppendColumn("von", format=wx.LIST_FORMAT_LEFT,
                                   width=72)
        self.lcConBox.AppendColumn("zu", format=wx.LIST_FORMAT_LEFT,
                                   width=72)
        switchSizer.Add(self.lcConBox, 0, wx.EXPAND, 0)

        self.wlGrid = WireListGrid(self.bottomPanel)
        gridSizer.Add(self.wlGrid, 1, wx.ALL | wx.EXPAND, 5)

        self.switchPanel.SetSizer(switchSizer)

        self.bottomPanel.SetSizer(gridSizer)

        self.topPanel.SetSizer(pdfviewSizer)

        self.splitWindow.SplitHorizontally(self.topPanel, self.bottomPanel, 1)

        self.panelBkg.SetSizer(controlSizer)

        self.SetSizer(mainSizer)

        self.Layout()

        self.btnImportExcel.Bind(wx.EVT_BUTTON, self.onImportExcelClicked)
        self.btnImportPDF.Bind(wx.EVT_BUTTON, self.onImportPDFClicked)
        self.btnExport.Bind(wx.EVT_BUTTON, self.onExportClicked)
        self.sldZoom.Bind(wx.EVT_COMMAND_SCROLL_THUMBRELEASE, self.onZoom)
        self.btnSort.Bind(wx.EVT_BUTTON, self.onSortClicked)
        self.btnSwitch.Bind(wx.EVT_BUTTON, self.onSwitchClicked)
        self.lcConBox.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onSwitchClicked)
        self.lcConBox.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onConSelected)
        self.lcConBox.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onConDeselected)

    def onImportExcelClicked(self, event):
        openFileDialog = wx.FileDialog(self, "Öffnen", "", "",
                                       "Excel Dateien (*.xlsx)|*.xlsx",
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        openFileDialog.ShowModal()
        self.openedFile = openFileDialog.GetPath()
        self.wlDF.set_dataframe_from_excel(self.openedFile)
        self.wlGrid.from_df(self.wlDF.get_dataframe())
        self.wlGrid.ClearSelection()
        self.bmpSideView.SetBitmap(wx.Bitmap(wx.Image(1, 1)))

    def onImportPDFClicked(self, event):
        outfolder = "/".join([self.directory["tmp"], "WireList"])
        self.pdfimporter = PDFToDataFrameDialog(self.panelBkg,
                                                outfolder=outfolder)
        self.pdfimporter.Bind(wx.EVT_CLOSE, self.onPDFImporterClose)
        self.pdfimporter.ShowModal()
        self.wlGrid.ClearSelection()

    def onPDFImporterClose(self, event):
        self.sideViewImgPath = self.pdfimporter.getImagePath()
        self.sldZoom.SetValue(self.sldZoom.GetMax() * 0.5)
        self.onZoom(event)
        self.sldZoom.Enable()
        self.openedFile = self.pdfimporter.getPDFPath()
        self.topPanel.SetupScrolling()
        self.wlGrid.from_df(self.pdfimporter.getData())

        event.Skip()

    def onSortClicked(self, event):
        self.onConDeselected(event)
        self.wlGrid.ClearSelection()
        data = self.wlGrid.get_dataframe()
        if data.empty:
            return
        self.wlDF.set_dataframe(data)

        if self.lcConBox.GetItemCount() == 0:
            self.wlGrid.from_df(self.wlDF.get_dataframe(sort_rows=True))
            self.fillConnectionBox()

        else:
            connections = []
            for row in range(self.lcConBox.GetItemCount()):
                start = self.lcConBox.GetItem(itemIdx=row, col=0).GetText()
                end = self.lcConBox.GetItem(itemIdx=row, col=1).GetText()
                connections.append((start, end))

            self.wlDF.reorder_endpoints(connections)
            self.wlGrid.from_df(self.wlDF.get_dataframe(sort_rows=True))
            self.fillConnectionBox()
        self.wlGrid.ClearSelection()

    def onSwitchClicked(self, event):
        row = self.lcConBox.GetFirstSelected()
        if row == -1:
            return

        start = self.lcConBox.GetItem(itemIdx=row, col=0).GetText()
        end = self.lcConBox.GetItem(itemIdx=row, col=1).GetText()

        self.lcConBox.SetItem(row, 0, end)
        self.lcConBox.SetItem(row, 1, start)

    def onExportClicked(self, event):
        dlg = wx.FileDialog(self, "Drahtliste speichern unter:", ".",
                            self.getFilename(self.openedFile), "", wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:

            exportPath = dlg.GetPath()
            if os.path.exists(exportPath):
                shutil.rmtree(exportPath)

            raw_path = os.path.join(exportPath, "raw")
            msg_path = os.path.join(exportPath, "Messages")
            os.makedirs(raw_path)
            os.makedirs(msg_path)

            if self.openedFile:
                shutil.copy(self.openedFile, raw_path)

            self.wlDF.set_dataframe(self.wlGrid.get_dataframe())
            self.wlDF.export_markers(outfolder=msg_path)
            self.wlDF.export_connections(outfolder=exportPath)
            self.wlDF.to_excel(filename=self.getFilename(self.openedFile),
                               outfolder=exportPath)

        dlg.Destroy()

    def onZoom(self, event):
        if not self.sideViewImgPath:
            return
        img = wx.Image(self.sideViewImgPath, wx.BITMAP_TYPE_ANY)

        W = img.GetWidth()
        H = img.GetHeight()

        mV = float(self.sldZoom.GetMax())
        newPhotoSize = 1000 * (1 - ((mV * 0.5) - self.sldZoom.GetValue()) / mV)
        newW = newPhotoSize
        newH = newPhotoSize * H / W

        img = img.Scale(newW, newH)
        self.bmpSideView.SetBitmap(wx.Bitmap(img))
        self.bmpSideView.Refresh()
        self.topPanel.SetupScrolling()

    def onConSelected(self, event):
        itemIdx = self.lcConBox.GetFirstSelected()
        start = self.lcConBox.GetItem(itemIdx=itemIdx, col=0).GetText()
        end = self.lcConBox.GetItem(itemIdx=itemIdx, col=1).GetText()

        # Thats a bit of an overhead. Maybe use wlDF as wlGrid datatype
        self.wlDF.set_dataframe(self.wlGrid.get_dataframe())

        rows = self.wlDF.find_connections(start, end)
        for row in rows:
            for col in range(self.wlGrid.GetNumberCols()):
                self.wlGrid.SetCellBackgroundColour(row, col, "light blue")

        self.wlGrid.ForceRefresh()

    def onConDeselected(self, event):
        # There should be a function to colour all at once somewhere....
        for row in range(self.wlGrid.GetNumberRows()):
            for col in range(self.wlGrid.GetNumberCols()):
                self.wlGrid.SetCellBackgroundColour(row, col, "white")

        self.wlGrid.ForceRefresh()

    def fillConnectionBox(self):
        self.lcConBox.DeleteAllItems()

        for i, (start, end) in enumerate(self.wlDF.connections):
            index = self.lcConBox.InsertItem(i, start)
            self.lcConBox.SetItem(index, 1, end)

    def getFilename(self, path):
        filename = os.path.basename(path)
        return os.path.splitext(filename)[0]


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainWireListPanel(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
