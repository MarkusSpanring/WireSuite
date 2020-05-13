#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.9pre on Thu Apr  9 15:31:26 2020
#

import wx
import os
import pandas as pd
import PDFToDataFrame as pdfocr

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class PDFToDataFrameDialog(wx.Dialog):
    def __init__(self, parent=None, outfolder="", *args, **kwds):
        # begin wxGlade: PDFToDataFrameGUI.__init__
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        super(PDFToDataFrameDialog, self).__init__(parent, *args, **kwds)

        self.SetSize((893, 655))
        self.SetTitle("frame")

        self.PhotoMaxSize = 600
        self.currentPage = -1
        self.outfolder = outfolder
        self.pdfpath = ""
        self.pdfPages = []
        self.clusters = []
        self.extractedData = pd.DataFrame([])
        self.extractedImagePath = ""
        self.extractedImage = wx.Bitmap(wx.Image(1, 1, clear=True))

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        btnPanel = wx.Panel(self, wx.ID_ANY)
        mainSizer.Add(btnPanel, 0, wx.EXPAND, 0)

        topSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btnImportPDF = wx.Button(btnPanel, wx.ID_ANY, "PDF importieren")
        topSizer.Add(self.btnImportPDF, 0, wx.ALL, 5)

        self.btnBack = wx.Button(btnPanel, wx.ID_ANY, "<<")
        topSizer.Add(self.btnBack, 0, wx.ALL, 5)

        self.btnForward = wx.Button(btnPanel, wx.ID_ANY, ">>")
        topSizer.Add(self.btnForward, 0, wx.ALL, 5)

        self.btnSelectPage = wx.Button(btnPanel, wx.ID_ANY, u"Seite auswählen")
        topSizer.Add(self.btnSelectPage, 0, wx.ALL, 5)

        spacerPanel = wx.Panel(btnPanel, wx.ID_ANY)
        spacerPanel.SetMinSize((630, 30))
        topSizer.Add(spacerPanel, 1, wx.ALL, 5)

        self.scClusterIdx = wx.SpinCtrl(btnPanel, wx.ID_ANY, "0", min=1, max=1)
        self.scClusterIdx.SetMinSize((50, 22))
        topSizer.Add(self.scClusterIdx, 0, wx.ALL, 5)

        self.btnSelectCluster = wx.Button(btnPanel, wx.ID_ANY, "Daten extrahieren")
        topSizer.Add(self.btnSelectCluster, 0, wx.ALL, 5)

        img = wx.Image(1000, self.PhotoMaxSize)
        self.pdfPage = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))
        mainSizer.Add(self.pdfPage, 0, wx.EXPAND, 0)

        btnPanel.SetSizer(topSizer)
        
        self.SetSizer(mainSizer)

        self.Layout()

        self.btnBack.Bind(wx.EVT_BUTTON, self.onPageBackClicked)
        self.btnForward.Bind(wx.EVT_BUTTON, self.onPageForwardClicked)
        self.btnSelectPage.Bind(wx.EVT_BUTTON, self.onSelectPageClicked)
        self.btnImportPDF.Bind(wx.EVT_BUTTON, self.onImportPDFClicked)
        self.btnSelectCluster.Bind(wx.EVT_BUTTON, self.onSelectClusterClicked)
        # end wxGlade

        self.btnBack.Disable()
        self.btnForward.Disable()
        self.btnSelectPage.Disable()
        self.btnSelectCluster.Disable()

    def onPageBackClicked(self, event):
        self.btnForward.Enable()
        self.currentPage -= 1
        if (self.currentPage - 1) < 0:
            self.btnBack.Disable()

        self.onView()

    def onPageForwardClicked(self, event):
        self.currentPage += 1
        if self.currentPage + 1 == len(self.pdfPages):
            self.btnForward.Disable()
        self.onView()

    def onSelectPageClicked(self, event):
        outfolder = os.path.dirname(self.pdfPages[self.currentPage])
        img, contours = pdfocr.find_contours_in_image(self.pdfPages[self.currentPage],
                                                      basefolder=self.outfolder)
        self.clusters = pdfocr.BoxClusters(img, outfolder=outfolder)
        self.clusters.build_clusters(contours=contours)

        self.pdfPages = [self.clusters.mark_clusters_in_image()]
        self.currentPage = 0
        self.btnBack.Disable()
        self.btnForward.Disable()

        self.btnSelectCluster.Enable()
        self.scClusterIdx.SetMax(self.clusters.size())
        self.scClusterIdx.SetValue(1)

        self.onView()

    def onImportPDFClicked(self, event):  # wxGlade: MyDialog.<event_handler>
        dialog = wx.FileDialog(None, "Öffnen", "", "",
                               "PDF Dateien (*.pdf)|*.pdf",
                                     wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.pdfpath = dialog.GetPath()
            self.currentPage = 0
            self.btnBack.Disable()
            self.btnForward.Disable()
            self.btnSelectPage.Enable()
            self.btnSelectCluster.Disable()

        dialog.Destroy()

        if self.pdfpath:
            self.pdfPages = pdfocr.save_images_from_pdf(self.pdfpath,
                                                        basefolder=self.outfolder)
            if len(self.pdfPages) > 1:
                self.btnForward.Enable()

            elif len(self.pdfPages) == 1:
                self.btnSelectPage.Disable()
                self.onSelectPageClicked(event)

            self.onView()

    def onView(self):
        img = wx.Image(self.pdfPages[self.currentPage], wx.BITMAP_TYPE_ANY)
        # scale the image, preserving the aspect ratio
        W = img.GetWidth()
        H = img.GetHeight()

        NewH = self.PhotoMaxSize
        NewW = self.PhotoMaxSize * W / H

        img = img.Scale(NewW, NewH)
        self.pdfPage.SetBitmap(wx.Bitmap(img))
        self.Refresh()

    def onSelectClusterClicked(self, event):
        clusterIdx = int(self.scClusterIdx.GetValue()) - 1

        image_path = self.clusters.get_cluster_image(clusterIdx)
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        newW = 1000 * (img.GetWidth() / img.GetHeight())
        self.extractedImage = wx.Bitmap(img.Scale(newW, 1000))
        self.extractedImagePath = image_path

        self.extractedData = self.clusters.get_df_from_cluster(clusterIdx)
        self.Close()

    def getImagePath(self):
        return self.extractedImagePath

    def getImage(self):
        return self.extractedImage

    def getData(self):
        return self.extractedData

    def getPDFPath(self):
        return self.pdfpath


class MyApp(wx.App):
    def OnInit(self):
        self.frame = PDFToDataFrameDialog(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
